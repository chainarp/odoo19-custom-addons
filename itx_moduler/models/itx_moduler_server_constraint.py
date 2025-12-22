# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class ItxModulerServerConstraint(models.Model):
    _name = 'itx.moduler.server.constraint'
    _description = 'ITX Moduler Server Constraint (Snapshot)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'model_id, name'

    # === Core Identification ===
    name = fields.Char(
        string='Method Name',
        required=True,
        help='Python method name (e.g., "_check_email_format")'
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
    field_ids = fields.Many2many(
        'itx.moduler.model.field',
        'itx_moduler_server_constraint_field_rel',
        'constraint_id',
        'field_id',
        string='Trigger Fields',
        domain="[('model_id', '=', model_id)]",
        help='Fields that trigger this constraint when modified'
    )

    field_names = fields.Char(
        string='Field Names (comma-separated)',
        help='Alternative: Enter field names directly (e.g., "email,phone")'
    )

    code = fields.Text(
        string='Python Code',
        required=True,
        default='''# Available variables:
#  - self: recordset being validated
#  - ValidationError: exception to raise
# Example:
for record in self:
    if record.field and not condition:
        raise ValidationError('Error message')
''',
        help='Python validation code'
    )

    message = fields.Char(
        string='Default Error Message',
        translate=True,
        help='Default error message (can be overridden in code)'
    )

    # === Additional Info ===
    description = fields.Text(
        string='Description',
        help='Description of what this constraint validates'
    )

    # === State & Tracking ===
    state = fields.Selection([
        ('draft', 'Draft'),
        ('validated', 'Validated'),
        ('applied', 'Applied'),
        ('exported', 'Exported'),
        ('archived', 'Archived')
    ], default='draft', required=True, index=True)

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
        'itx.moduler.server.constraint',
        string='Parent Version',
        readonly=True,
        help='Previous version of this constraint'
    )

    # === Display ===
    @api.depends('name', 'field_names', 'field_ids')
    def _compute_display_name(self):
        for constraint in self:
            fields_str = constraint.field_names
            if not fields_str and constraint.field_ids:
                fields_str = ', '.join(constraint.field_ids.mapped('name'))

            if fields_str:
                constraint.display_name = f"{constraint.name} ({fields_str})"
            else:
                constraint.display_name = constraint.name

    # === Computed Fields ===
    @api.depends('field_ids', 'field_names')
    def _compute_trigger_fields_list(self):
        """Get list of trigger field names"""
        for constraint in self:
            fields = []
            if constraint.field_ids:
                fields.extend(constraint.field_ids.mapped('name'))
            if constraint.field_names:
                fields.extend([f.strip() for f in constraint.field_names.split(',')])
            constraint.trigger_fields_list = ', '.join(set(fields))

    trigger_fields_list = fields.Char(
        string='Trigger Fields',
        compute='_compute_trigger_fields_list',
        store=True
    )

    # === Validations ===
    @api.constrains('name')
    def _check_name(self):
        """Validate method name format"""
        for constraint in self:
            if not constraint.name.startswith('_check_'):
                raise ValidationError(
                    _('Server constraint method name should start with "_check_"\n'
                      'Example: _check_email_format')
                )

            # Check valid Python identifier
            import re
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', constraint.name):
                raise ValidationError(
                    _('Method name must be a valid Python identifier')
                )

    @api.constrains('code')
    def _check_code(self):
        """Basic Python syntax validation"""
        for constraint in self:
            if not constraint.code:
                raise ValidationError(_('Python code is required'))

            # Try to compile (basic syntax check)
            try:
                compile(constraint.code, '<string>', 'exec')
            except SyntaxError as e:
                raise ValidationError(
                    _('Python syntax error:\n%s') % str(e)
                )

    # === Actions ===
    def action_validate(self):
        """Validate constraint before applying"""
        self.ensure_one()

        if self.state != 'draft':
            raise UserError(_('Only draft constraints can be validated'))

        # Validate name and code
        self._check_name()
        self._check_code()

        self.state = 'validated'
        return True

    def action_apply_to_odoo(self):
        """
        Server constraints cannot be applied directly to Odoo at runtime.
        They must be exported to Python code and module upgraded.
        """
        self.ensure_one()

        if self.state not in ('validated', 'applied'):
            raise UserError(_('Constraint must be validated before applying'))

        # Mark as applied (but won't actually work until exported and upgraded)
        self.write({
            'state': 'applied',
            'applied_date': fields.Datetime.now(),
        })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Marked as Applied'),
                'message': _(
                    'Server constraint "%s" marked as applied.\n'
                    'Note: Will only work after exporting module and upgrading.'
                ) % self.name,
                'type': 'warning',
                'sticky': True,
            }
        }

    def _generate_python_code(self):
        """Generate Python @api.constrains decorator and method"""
        self.ensure_one()

        # Get trigger fields
        fields = []
        if self.field_ids:
            fields.extend([f"'{f.name}'" for f in self.field_ids])
        if self.field_names:
            fields.extend([f"'{f.strip()}'" for f in self.field_names.split(',')])

        fields_str = ', '.join(set(fields)) if fields else "'name'"

        # Generate method
        code = f"\n    @api.constrains({fields_str})\n"
        code += f"    def {self.name}(self):\n"

        if self.description:
            code += f'        """{self.description}"""\n'

        # Indent the user code
        user_code_lines = self.code.strip().split('\n')
        for line in user_code_lines:
            if line.strip():  # Skip empty lines
                code += f"        {line}\n"
            else:
                code += "\n"

        return code
