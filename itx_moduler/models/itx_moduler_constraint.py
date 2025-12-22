# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class ItxModulerConstraint(models.Model):
    _name = 'itx.moduler.constraint'
    _description = 'ITX Moduler SQL Constraint (Snapshot)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'model_id, name'

    # === Core Identification ===
    name = fields.Char(
        string='Constraint Name',
        required=True,
        help='Technical name (e.g., "name_unique")'
    )

    # === Module Link ===
    module_id = fields.Many2one(
        'itx.moduler.module',
        string='Module',
        required=True,
        ondelete='cascade',
        index=True
    )

    # === Target Model ===
    model_id = fields.Many2one(
        'itx.moduler.model',
        string='Model',
        required=True,
        ondelete='cascade',
        help='Model this constraint applies to'
    )

    model_name = fields.Char(
        string='Model Name',
        related='model_id.model',
        readonly=True,
        store=True
    )

    # === Constraint Configuration ===
    type = fields.Selection([
        ('u', 'Unique'),
        ('e', 'Exclude'),
        ('c', 'Check'),
    ], string='Constraint Type', required=True, default='u',
        help='Type of SQL constraint:\n'
             '- Unique: Ensures column values are unique\n'
             '- Check: Ensures values meet a condition\n'
             '- Exclude: Advanced exclusion constraint')

    definition = fields.Char(
        string='Constraint Definition',
        required=True,
        help='SQL constraint definition\n'
             'Examples:\n'
             '- Unique: "UNIQUE(column_name)"\n'
             '- Check: "CHECK(value >= 0)"\n'
             '- Exclude: "EXCLUDE USING gist (period WITH &&)"'
    )

    message = fields.Char(
        string='Error Message',
        required=True,
        translate=True,
        help='Error message shown when constraint is violated'
    )

    # === Additional Info ===
    description = fields.Text(
        string='Description',
        help='Description of what this constraint does'
    )

    # === State & Tracking ===
    state = fields.Selection([
        ('draft', 'Draft'),
        ('validated', 'Validated'),
        ('applied', 'Applied'),
        ('exported', 'Exported'),
        ('archived', 'Archived')
    ], default='draft', required=True, index=True)

    # Link to real ir.model.constraint when applied
    ir_constraint_id = fields.Many2one(
        'ir.model.constraint',
        string='Applied Constraint',
        readonly=True,
        help='Link to real ir.model.constraint when applied'
    )

    applied_date = fields.Datetime(
        string='Applied Date',
        readonly=True
    )

    # === AI Integration ===
    created_by_ai = fields.Boolean(
        string='AI Generated',
        default=False
    )

    ai_prompt = fields.Text(
        string='AI Prompt',
        help='Prompt used to generate this constraint (if from AI)'
    )

    # === Version Control ===
    version = fields.Integer(
        string='Version',
        default=1,
        readonly=True
    )

    parent_version_id = fields.Many2one(
        'itx.moduler.constraint',
        string='Parent Version',
        readonly=True,
        help='Previous version of this constraint'
    )

    # === Display ===
    @api.depends('name', 'type', 'definition')
    def _compute_display_name(self):
        for constraint in self:
            type_label = dict(self._fields['type'].selection).get(constraint.type, '')
            constraint.display_name = f"{constraint.name} ({type_label})"

    # === Validations ===
    @api.constrains('definition')
    def _check_definition(self):
        """Validate constraint definition syntax"""
        for constraint in self:
            # Only validate if manually creating/editing (state = draft)
            # Skip validation for imported constraints from database (state = applied)
            if constraint.state != 'draft':
                continue

            if not constraint.definition:
                raise ValidationError(_('Constraint definition is required'))

            # Optional: Log warnings for best practices (not blocking)
            definition = constraint.definition.upper().strip()

            if constraint.type == 'u' and not definition.startswith('UNIQUE'):
                _logger.info(
                    f'Note: Unique constraint "{constraint.name}" should start with "UNIQUE" '
                    f'for better SQL compatibility.'
                )

            if constraint.type == 'c' and not definition.startswith('CHECK'):
                _logger.info(
                    f'Note: Check constraint "{constraint.name}" should start with "CHECK" '
                    f'for better SQL compatibility.'
                )

    # === Actions ===
    def action_validate(self):
        """Validate constraint before applying"""
        self.ensure_one()

        if self.state != 'draft':
            raise UserError(_('Only draft constraints can be validated'))

        # Validate definition
        self._check_definition()

        self.state = 'validated'
        return True

    def action_apply_to_odoo(self):
        """Apply constraint to Odoo database"""
        self.ensure_one()

        if self.state not in ('validated', 'applied'):
            raise UserError(_('Constraint must be validated before applying'))

        # Check if model is applied
        if not self.model_id.ir_model_id:
            raise UserError(
                _('Model "%s" must be applied first!') % self.model_id.name
            )

        # Get table name
        table_name = self.model_id.model.replace('.', '_')

        # Build SQL constraint name (PostgreSQL format)
        sql_name = f"{table_name}_{self.name}"

        # Check if constraint already exists in ir.model.constraint
        ir_constraint = self.env['ir.model.constraint'].search([
            ('name', '=', sql_name),
            ('model', '=', self.model_id.ir_model_id.id),
        ], limit=1)

        vals = {
            'name': sql_name,
            'model': self.model_id.ir_model_id.id,
            'type': self.type,
            'definition': self.definition,
            'message': self.message,
        }

        if ir_constraint:
            ir_constraint.write(vals)
        else:
            # Create constraint record
            ir_constraint = self.env['ir.model.constraint'].create(vals)

            # Apply constraint to database (execute ALTER TABLE)
            try:
                constraint_sql = f"ALTER TABLE {table_name} ADD CONSTRAINT {sql_name} {self.definition}"
                self.env.cr.execute(constraint_sql)
            except Exception as e:
                # If constraint already exists in DB, that's ok
                if 'already exists' not in str(e):
                    raise UserError(
                        _('Failed to create SQL constraint:\n%s') % str(e)
                    )

        self.write({
            'state': 'applied',
            'ir_constraint_id': ir_constraint.id,
            'applied_date': fields.Datetime.now(),
        })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Applied'),
                'message': _('SQL Constraint "%s" applied successfully') % self.name,
                'type': 'success',
            }
        }

    def _generate_python_code(self):
        """Generate Python _sql_constraints for model file"""
        self.ensure_one()

        # Format: ('constraint_name', 'CONSTRAINT_DEFINITION', 'Error message')
        code = f"        ('{self.name}', '{self.definition}', '{self.message}'),"
        return code
