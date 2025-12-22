# -*- coding: utf-8 -*-

import json
import re
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class ItxModulerModel(models.Model):
    _name = 'itx.moduler.model'
    _description = 'ITX Moduler Model (Snapshot)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, name'

    # === Core Identification ===
    name = fields.Char(
        string='Model Name',
        required=True,
        tracking=True,
        help='Human-readable name (e.g., "Product Template")'
    )

    model = fields.Char(
        string='Technical Name',
        required=True,
        tracking=True,
        help='Python model name (e.g., "product.template")',
    )

    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Order in module structure'
    )

    # === Module Link ===
    module_id = fields.Many2one(
        'itx.moduler.module',
        string='Module',
        required=True,
        ondelete='cascade',
        tracking=True,
        index=True
    )

    # === Description & Documentation ===
    description = fields.Text(
        string='Description',
        tracking=True,
        help='What this model represents (for AI context)'
    )

    # AI prompt that created this model
    ai_prompt = fields.Text(
        string='AI Prompt',
        help='Original prompt used to generate this model (if from AI)',
        tracking=True
    )

    # === Inheritance ===
    inherit_model_ids = fields.Many2many(
        'ir.model',
        'itx_moduler_model_inherit_rel',
        'moduler_model_id',
        'ir_model_id',
        string='Inherit Models',
        help='Models to inherit (_inherit). Can select multiple.'
    )

    inherit_model_names = fields.Char(
        string='Inherit (comma-separated)',
        help='Alternative: comma-separated model names (e.g., "mail.thread, mail.activity.mixin")',
        compute='_compute_inherit_model_names',
        inverse='_inverse_inherit_model_names',
        store=True
    )

    # === Model Configuration ===
    rec_name = fields.Char(
        string='Record Name Field',
        default='name',
        help='Field to use as record display name (default: name)'
    )

    order_field = fields.Char(
        string='Default Order',
        default='id desc',
        help='Default ordering (e.g., "name, id desc")'
    )

    transient_model = fields.Boolean(
        string='Transient Model (Wizard)',
        default=False,
        help='Check if this is a wizard (models.TransientModel)'
    )

    abstract_model = fields.Boolean(
        string='Abstract Model (Mixin)',
        default=False,
        help='Check if this is a mixin (models.AbstractModel)'
    )

    # === Fields ===
    field_ids = fields.One2many(
        'itx.moduler.model.field',
        'model_id',
        string='Fields',
        copy=True
    )

    field_count = fields.Integer(
        string='Field Count',
        compute='_compute_field_count',
        store=True
    )

    # === Python Methods ===
    method_ids = fields.One2many(
        'itx.moduler.model.method',
        'model_id',
        string='Python Methods',
        help='Custom Python methods (compute, onchange, CRUD overrides)'
    )

    method_count = fields.Integer(
        string='Method Count',
        compute='_compute_method_count',
        store=True
    )

    # === State & Tracking ===
    state = fields.Selection([
        ('draft', 'Draft'),
        ('validated', 'Validated'),
        ('applied', 'Applied'),
        ('exported', 'Exported'),
        ('archived', 'Archived')
    ], default='draft', required=True, tracking=True, index=True)

    # Link to real ir.model when applied
    ir_model_id = fields.Many2one(
        'ir.model',
        string='Applied Model',
        readonly=True,
        help='Link to real ir.model when state=applied'
    )

    applied_date = fields.Datetime(
        string='Applied Date',
        readonly=True
    )

    error_message = fields.Text(
        string='Error Message',
        readonly=True
    )

    # === Version Control ===
    version = fields.Integer(
        string='Version',
        default=1,
        readonly=True,
        help='Auto-incremented version number'
    )

    active = fields.Boolean(
        string='Active',
        default=True,
        help='False = archived version'
    )

    parent_version_id = fields.Many2one(
        'itx.moduler.model',
        string='Parent Version',
        help='Previous version this was cloned from',
        ondelete='set null'
    )

    child_version_ids = fields.One2many(
        'itx.moduler.model',
        'parent_version_id',
        string='Child Versions'
    )

    revision_ids = fields.One2many(
        'itx.moduler.model.revision',
        'model_id',
        string='Revision History'
    )

    revision_count = fields.Integer(
        string='Revision Count',
        compute='_compute_revision_count'
    )

    # === AI Metadata ===
    created_by_ai = fields.Boolean(
        string='Created by AI',
        default=False,
        help='True if this model was generated by Claude',
        index=True
    )

    ai_confidence = fields.Float(
        string='AI Confidence',
        help='Confidence score from AI generation (0-100%)',
        digits=(5, 2)
    )

    # === Standard Odoo Fields (explicit definition for mail.thread) ===
    create_date = fields.Datetime(
        string='Created on',
        readonly=True,
        index=True
    )

    create_uid = fields.Many2one(
        'res.users',
        string='Created by',
        readonly=True,
        index=True
    )

    write_date = fields.Datetime(
        string='Last Updated on',
        readonly=True,
        index=True
    )

    write_uid = fields.Many2one(
        'res.users',
        string='Last Updated by',
        readonly=True,
        index=True
    )

    # === Compatibility Properties (for legacy code generator) ===
    # These provide ir.model-compatible field names for the code generator
    @property
    def field_id(self):
        """Compatibility: ir.model uses 'field_id', we use 'field_ids'"""
        return self.field_ids

    @property
    def transient(self):
        """Compatibility: ir.model uses 'transient', we use 'transient_model'"""
        return self.transient_model

    @property
    def _abstract(self):
        """Compatibility: ir.model uses '_abstract', we use 'abstract_model'"""
        return self.abstract_model

    @property
    def m2o_inherit_py_class(self):
        """Compatibility: Placeholder for Python class inheritance"""
        # Return a dummy object with .name and .module attributes
        class DummyClass:
            name = None
            module = None
        return DummyClass()

    @property
    def m2o_inherit_model(self):
        """Compatibility: Placeholder for model inheritance"""
        # Return a dummy object with .model and .id attributes
        class DummyModel:
            model = None
            id = None
        return DummyModel()

    @property
    def nomenclator(self):
        """Compatibility: Always export data for now"""
        return True

    @property
    def view_ids(self):
        """Get all views for this model from snapshot tables"""
        return self.env['itx.moduler.view'].search([('model_id', '=', self.id)])

    @property
    def o2m_act_window(self):
        """Get all window actions for this model from snapshot tables"""
        return self.env['itx.moduler.action.window'].search([('model_id', '=', self.id)])

    @property
    def o2m_serverconstrains(self):
        """Compatibility: Server constrains not yet implemented in snapshots"""
        # TODO: Implement itx.moduler.server_constrain model in future
        return self.env['ir.model.server_constrain'].browse([])

    @property
    def o2m_server_action(self):
        """Get all server actions for this model from snapshot tables"""
        # TODO: Implement itx.moduler.action.server model
        return self.env['ir.actions.server'].browse([])

    @property
    def o2m_reports(self):
        """Get all reports for this model from snapshot tables"""
        # TODO: Implement itx.moduler.report model
        return self.env['ir.actions.report'].browse([])

    @property
    def o2m_constraints(self):
        """Compatibility: SQL constraints not yet implemented in snapshots"""
        # TODO: Implement itx.moduler.constraint model in future
        return self.env['ir.model.constraint'].browse([])

    @property
    def access_ids(self):
        """Compatibility: Get ACLs for this model from ir.model.access"""
        # ACLs are linked via model_id in ir.model.access
        return self.env['ir.model.access'].search([('model_id.model', '=', self.model)])

    @property
    def rule_ids(self):
        """Compatibility: Get record rules for this model"""
        # Rules are linked via model_id in ir.rule
        return self.env['ir.rule'].search([('model_id.model', '=', self.model)])

    # === Computed Fields ===
    @api.depends('field_ids')
    def _compute_field_count(self):
        for record in self:
            record.field_count = len(record.field_ids)

    @api.depends('method_ids')
    def _compute_method_count(self):
        for record in self:
            record.method_count = len(record.method_ids)

    @api.depends('revision_ids')
    def _compute_revision_count(self):
        for record in self:
            record.revision_count = len(record.revision_ids)

    @api.depends('inherit_model_ids')
    def _compute_inherit_model_names(self):
        for record in self:
            if record.inherit_model_ids:
                record.inherit_model_names = ','.join(
                    record.inherit_model_ids.mapped('model')
                )
            else:
                record.inherit_model_names = ''

    def _inverse_inherit_model_names(self):
        """Allow SA to type model names directly"""
        for record in self:
            if record.inherit_model_names:
                models = record.inherit_model_names.split(',')
                ir_models = self.env['ir.model'].search([
                    ('model', 'in', [m.strip() for m in models])
                ])
                record.inherit_model_ids = ir_models

    # === Constraints ===
    _model_unique = models.Constraint(
        'UNIQUE(module_id, model, version)',
        'Model technical name must be unique per module and version!',
    )

    @api.constrains('model')
    def _check_model_name(self):
        """Validate model name pattern"""
        pattern = r'^[a-z][a-z0-9_.]*[a-z0-9]$'
        for record in self:
            if not re.match(pattern, record.model):
                raise ValidationError(
                    f'Model name "{record.model}" is invalid.\n'
                    'Must be lowercase with dots/underscores only.'
                )

    @api.constrains('transient_model', 'abstract_model')
    def _check_model_type(self):
        """Cannot be both transient and abstract"""
        for record in self:
            if record.transient_model and record.abstract_model:
                raise ValidationError(
                    'Model cannot be both Transient and Abstract!'
                )

    # === CRUD Overrides ===
    @api.model_create_multi
    def create(self, vals_list):
        """Create revision on create"""
        records = super().create(vals_list)
        for record in records:
            record._create_revision('create', 'Model created')
        return records

    def write(self, vals):
        """Create revision on write if significant changes"""
        result = super().write(vals)

        # Track significant changes
        significant_fields = [
            'name', 'model', 'description', 'inherit_model_names',
            'rec_name', 'order_field', 'transient_model', 'abstract_model'
        ]

        if any(field in vals for field in significant_fields):
            for record in self:
                if record.state in ('draft', 'validated'):
                    record._create_revision('edit', 'Model edited')

        return result

    # === Actions ===
    def action_validate(self):
        """Validate model structure"""
        self.ensure_one()
        errors = []

        # Check has at least one field
        if not self.field_ids:
            errors.append('Model must have at least one field')

        # Check rec_name field exists
        if self.rec_name:
            rec_field = self.field_ids.filtered(
                lambda f: f.name == self.rec_name
            )
            if not rec_field:
                errors.append(f'rec_name field "{self.rec_name}" not found in fields')

        # Validate all fields
        for field in self.field_ids:
            try:
                field._validate_field()
            except ValidationError as e:
                errors.append(f'Field {field.name}: {str(e)}')

        if errors:
            self.state = 'draft'
            self.error_message = '\n'.join(errors)
            raise ValidationError('\n'.join(errors))
        else:
            self.write({
                'state': 'validated',
                'error_message': False
            })
            self._create_revision('validate', 'Model validated')

        return True

    def action_apply_to_odoo(self):
        """Create real ir.model from snapshot"""
        self.ensure_one()

        if self.state != 'validated':
            raise UserError('Model must be in Validated state before applying')

        # Safety check for standard modules
        if self.module_id._is_standard_module():
            raise UserError(
                'Cannot directly modify standard Odoo modules!\n'
                'Create an inheriting module instead.'
            )

        # Create or update ir.model
        ir_model = self.env['ir.model'].search([
            ('model', '=', self.model)
        ], limit=1)

        vals = {
            'name': self.name,
            'model': self.model,
            'info': self.description or '',
            'state': 'manual',
            'transient': self.transient_model,
        }

        if ir_model:
            ir_model.write(vals)
        else:
            ir_model = self.env['ir.model'].create(vals)

        # Apply fields
        for field in self.field_ids:
            field.action_apply_to_odoo(ir_model)

        # Update state
        self.write({
            'ir_model_id': ir_model.id,
            'state': 'applied',
            'applied_date': fields.Datetime.now()
        })

        self._create_revision('apply', f'Applied to Odoo (ir.model.id: {ir_model.id})')

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Model applied to Odoo successfully!'),
                'type': 'success',
                'sticky': False,
            }
        }

    def action_generate_python_code(self):
        """Generate Python code for export"""
        self.ensure_one()

        code = f"# -*- coding: utf-8 -*-\n\n"
        code += f"from odoo import models, fields, api, _\n"

        if self.field_ids.filtered(lambda f: f.ttype in ('many2one', 'one2many', 'many2many')):
            code += f"from odoo.exceptions import ValidationError, UserError\n"

        code += f"\n\n"
        code += f"class {self._get_class_name()}(models.{'TransientModel' if self.transient_model else 'AbstractModel' if self.abstract_model else 'Model'}):\n"
        code += f"    _name = '{self.model}'\n"
        code += f"    _description = '{self.name}'\n"

        if self.inherit_model_names:
            inherits = [m.strip() for m in self.inherit_model_names.split(',')]
            if len(inherits) == 1:
                code += f"    _inherit = '{inherits[0]}'\n"
            else:
                code += f"    _inherit = {inherits}\n"

        if self.rec_name and self.rec_name != 'name':
            code += f"    _rec_name = '{self.rec_name}'\n"

        if self.order_field and self.order_field != 'id desc':
            code += f"    _order = '{self.order_field}'\n"

        code += "\n"

        # Add fields
        for field in self.field_ids:
            code += field.generate_python_code()

        # Add methods
        if self.method_ids:
            code += "\n"
            for method in self.method_ids:
                code += f"{method.code}\n\n"

        return code

    def _get_class_name(self):
        """Convert model name to class name"""
        # product.template -> ProductTemplate
        parts = self.model.split('.')
        return ''.join(word.capitalize() for word in parts)

    def action_create_new_version(self):
        """Clone to new version"""
        self.ensure_one()

        new_version = self.copy({
            'version': self.version + 1,
            'parent_version_id': self.id,
            'state': 'draft',
            'active': True,
            'ir_model_id': False,
            'applied_date': False,
        })

        # Archive current version
        self.write({
            'active': False,
            'state': 'archived'
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'itx.moduler.model',
            'res_id': new_version.id,
            'view_mode': 'form',
            'target': 'current'
        }

    def action_view_revisions(self):
        """View revision history"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Revisions: {self.name}',
            'res_model': 'itx.moduler.model.revision',
            'view_mode': 'list,form',
            'domain': [('model_id', '=', self.id)],
            'context': {'create': False}
        }

    def action_view_fields(self):
        """View model fields"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Fields: {self.name}',
            'res_model': 'itx.moduler.model.field',
            'view_mode': 'list,form',
            'domain': [('model_id', '=', self.id)],
            'context': {'default_model_id': self.id}
        }

    def action_view_methods(self):
        """View model methods"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Methods: {self.name}',
            'res_model': 'itx.moduler.model.method',
            'view_mode': 'list,form',
            'domain': [('model_id', '=', self.id)],
            'context': {'default_model_id': self.id}
        }

    def _create_revision(self, change_type, change_summary):
        """Create revision record"""
        self.ensure_one()

        snapshot = {
            'model': {
                'name': self.name,
                'model': self.model,
                'description': self.description,
                'inherit_model_names': self.inherit_model_names,
                'rec_name': self.rec_name,
                'order_field': self.order_field,
                'transient_model': self.transient_model,
                'abstract_model': self.abstract_model,
            },
            'fields': [{
                'name': f.name,
                'field_description': f.field_description,
                'ttype': f.ttype,
                'required': f.required,
                'help': f.help,
            } for f in self.field_ids],
            'methods': [{
                'name': m.name,
                'code': m.code,
            } for m in self.method_ids]
        }

        return self.env['itx.moduler.model.revision'].create({
            'model_id': self.id,
            'version': self.version,
            'snapshot_data': json.dumps(snapshot, indent=2),
            'change_type': change_type,
            'change_summary': change_summary,
            'created_by_ai': self.created_by_ai,
            'ai_prompt': self.ai_prompt,
        })

    def _get_snapshot_json(self):
        """Get complete snapshot as JSON string"""
        self.ensure_one()
        snapshot = {
            'name': self.name,
            'model': self.model,
            'description': self.description,
            'version': self.version,
            'fields': [{
                'name': f.name,
                'field_description': f.field_description,
                'ttype': f.ttype,
            } for f in self.field_ids]
        }
        return json.dumps(snapshot, indent=2)
