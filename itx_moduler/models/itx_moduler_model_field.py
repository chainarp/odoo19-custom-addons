# -*- coding: utf-8 -*-

import re
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ItxModulerModelField(models.Model):
    _name = 'itx.moduler.model.field'
    _description = 'ITX Moduler Model Field (Snapshot)'
    _order = 'sequence, name'

    # === Core ===
    name = fields.Char(
        string='Technical Name',
        required=True,
        help='Python field name (e.g., "product_id")'
    )

    field_description = fields.Char(
        string='Label',
        required=True,
        help='User-visible label (e.g., "Product")'
    )

    sequence = fields.Integer(
        string='Sequence',
        default=10
    )

    model_id = fields.Many2one(
        'itx.moduler.model',
        string='Model',
        required=True,
        ondelete='cascade',
        index=True
    )

    # === Field Type ===
    ttype = fields.Selection([
        # Basic types
        ('char', 'Char'),
        ('text', 'Text'),
        ('html', 'HTML'),
        ('integer', 'Integer'),
        ('float', 'Float'),
        ('monetary', 'Monetary'),
        ('boolean', 'Boolean'),
        ('date', 'Date'),
        ('datetime', 'Datetime'),
        ('binary', 'Binary/File'),
        ('selection', 'Selection'),

        # Relational
        ('many2one', 'Many2one'),
        ('one2many', 'One2many'),
        ('many2many', 'Many2many'),
        ('many2one_reference', 'Many2one Reference'),

        # Special
        ('reference', 'Reference'),
        ('json', 'JSON'),
        ('properties', 'Properties'),
        ('properties_definition', 'Properties Definition'),
    ], string='Field Type', required=True, default='char')

    # === Relational Fields Config ===
    relation = fields.Char(
        string='Relation Model',
        help='Target model for relational fields (e.g., "product.product")'
    )

    relation_field = fields.Char(
        string='Relation Field',
        help='For One2many: field name in related model pointing back'
    )

    relation_table = fields.Char(
        string='Relation Table',
        help='For Many2many: custom relation table name (auto-generated if empty)'
    )

    column1 = fields.Char(
        string='Column 1',
        help='For Many2many: first column name'
    )

    column2 = fields.Char(
        string='Column 2',
        help='For Many2many: second column name'
    )

    on_delete = fields.Selection([
        ('cascade', 'Cascade'),
        ('restrict', 'Restrict'),
        ('set null', 'Set NULL'),
    ], string='On Delete', default='set null',
       help='For Many2one: what to do when related record is deleted')

    # === Selection Config ===
    selection = fields.Text(
        string='Selection Values (Python)',
        help='For selection fields: Python list like [("draft","Draft"),("done","Done")]'
    )

    selection_ids = fields.One2many(
        'itx.moduler.model.field.selection',
        'field_id',
        string='Selection Options',
        help='Alternative: define selection options as records'
    )

    # === Field Properties ===
    required = fields.Boolean('Required', default=False)
    readonly = fields.Boolean('Readonly', default=False)
    store = fields.Boolean('Stored', default=True)
    index = fields.Boolean('Indexed', default=False)
    copy = fields.Boolean('Copied on duplicate', default=True)
    translate = fields.Boolean('Translatable', default=False)
    tracking = fields.Boolean('Track Changes', default=False)

    # === Default Value ===
    default_value = fields.Char(
        string='Default Value',
        help='Python expression or value (e.g., "False", "lambda self: self.env.user")'
    )

    # === Domain & Context ===
    domain = fields.Char(
        string='Domain',
        help='Filter for relational fields (Python expression)'
    )

    context = fields.Char(
        string='Context',
        help='Context for relational fields (Python dict)'
    )

    # === Computed Fields ===
    is_computed = fields.Boolean(
        string='Computed Field',
        default=False
    )

    compute_method = fields.Char(
        string='Compute Method',
        help='Method name (e.g., "_compute_total")'
    )

    depends = fields.Char(
        string='Depends',
        help='Comma-separated field dependencies (e.g., "qty, price")'
    )

    inverse_method = fields.Char(
        string='Inverse Method',
        help='Method name for writing computed field'
    )

    search_method = fields.Char(
        string='Search Method',
        help='Method name for searching computed field'
    )

    # === Display ===
    help = fields.Text(
        string='Help',
        help='Tooltip text for users'
    )

    placeholder = fields.Char(
        string='Placeholder',
        help='Placeholder text in forms'
    )

    groups = fields.Many2many(
        'res.groups',
        'itx_moduler_field_groups_rel',
        string='Groups',
        help='Restrict field visibility to these groups'
    )

    # === Size Limits ===
    size = fields.Integer(
        string='Size',
        help='For Char: max length. For Binary: max size in bytes.'
    )

    digits = fields.Char(
        string='Digits',
        help='For Float/Monetary: precision (e.g., "(16, 2)" for 2 decimals)'
    )

    # === Special ===
    related = fields.Char(
        string='Related Field',
        help='Dot-notation path to related field (e.g., "partner_id.name")'
    )

    company_dependent = fields.Boolean(
        string='Company Dependent',
        help='Value depends on current company (ir.property)'
    )

    # === Field Behavior ===
    selectable = fields.Boolean(
        string='Selectable',
        default=True,
        help='Whether field can be selected (for selection fields)'
    )

    copied = fields.Boolean(
        string='Copied on Duplicate',
        default=True,
        help='Whether field value is copied when record is duplicated'
    )

    attachment = fields.Boolean(
        string='Store as Attachment',
        default=True,
        help='For Binary: store in ir.attachment instead of database'
    )

    # === Widget (for views) ===
    widget = fields.Char(
        string='Widget',
        help='UI widget to use (e.g., "many2many_tags", "statusbar")'
    )

    # === State ===
    state = fields.Selection(
        related='model_id.state',
        store=True,
        string='State'
    )

    ir_model_field_id = fields.Many2one(
        'ir.model.fields',
        string='Applied Field',
        readonly=True
    )

    # === AI Metadata ===
    created_by_ai = fields.Boolean('Created by AI', default=False)
    ai_prompt = fields.Text('AI Prompt Fragment')

    # === Compatibility Properties (for legacy code generator) ===
    @property
    def compute(self):
        """Compatibility: code generator uses 'compute', we use 'compute_method'"""
        return self.compute_method

    # === Constraints ===
    _name_unique = models.Constraint(
        'UNIQUE(model_id, name)',
        'Field name must be unique per model!',
    )

    @api.constrains('name')
    def _check_field_name(self):
        """Validate field name"""
        pattern = r'^[a-z][a-z0-9_]*$'
        for record in self:
            if not re.match(pattern, record.name):
                raise ValidationError(
                    f'Field name "{record.name}" is invalid.\n'
                    'Must start with lowercase letter, use underscores only.'
                )

    @api.constrains('ttype', 'relation')
    def _check_relation(self):
        """Validate relational fields have relation model"""
        for record in self:
            if record.ttype in ('many2one', 'one2many', 'many2many'):
                if not record.relation:
                    raise ValidationError(
                        f'{record.ttype} field "{record.name}" must have a relation model'
                    )

    @api.constrains('ttype', 'relation_field')
    def _check_one2many_inverse(self):
        """Validate one2many has inverse field"""
        for record in self:
            if record.ttype == 'one2many':
                if not record.relation_field:
                    raise ValidationError(
                        f'One2many field "{record.name}" must have a relation_field (inverse field name)'
                    )

    @api.onchange('ttype')
    def _onchange_ttype(self):
        """Clear irrelevant fields when type changes"""
        if self.ttype not in ('many2one', 'one2many', 'many2many'):
            self.relation = False
            self.relation_field = False
            self.relation_table = False
            self.on_delete = False

        if self.ttype != 'selection':
            self.selection = False

        if self.ttype not in ('char', 'binary'):
            self.size = False

        if self.ttype not in ('float', 'monetary'):
            self.digits = False

        if self.ttype != 'binary':
            self.attachment = False

    def _validate_field(self):
        """Validate field configuration"""
        self.ensure_one()

        # Check relational fields
        if self.ttype in ('many2one', 'one2many', 'many2many'):
            if not self.relation:
                raise ValidationError(f'Field {self.name}: relation model is required')

        if self.ttype == 'one2many' and not self.relation_field:
            raise ValidationError(f'Field {self.name}: relation_field is required for one2many')

        # Check selection
        if self.ttype == 'selection':
            if not self.selection and not self.selection_ids:
                raise ValidationError(
                    f'Field {self.name}: selection field must have selection values'
                )

        return True

    def generate_python_code(self):
        """Generate Python field definition"""
        self.ensure_one()

        # Map ttype to fields.* class
        type_map = {
            'char': 'Char',
            'text': 'Text',
            'html': 'Html',
            'integer': 'Integer',
            'float': 'Float',
            'monetary': 'Monetary',
            'boolean': 'Boolean',
            'date': 'Date',
            'datetime': 'Datetime',
            'binary': 'Binary',
            'selection': 'Selection',
            'many2one': 'Many2one',
            'one2many': 'One2many',
            'many2many': 'Many2many',
            'reference': 'Reference',
            'json': 'Json',
        }

        field_type = type_map.get(self.ttype, 'Char')
        code = f"    {self.name} = fields.{field_type}("

        params = []

        # Add positional parameters first
        if self.ttype == 'selection':
            if self.selection:
                params.append(self.selection)
            elif self.selection_ids:
                sel_list = [(s.value, s.label) for s in self.selection_ids]
                params.append(str(sel_list))

        elif self.ttype in ('many2one', 'one2many', 'many2many'):
            params.append(f"'{self.relation}'")

            if self.ttype == 'one2many' and self.relation_field:
                params.append(f"'{self.relation_field}'")

            elif self.ttype == 'many2many':
                if self.relation_table:
                    params.append(f"'{self.relation_table}'")
                if self.column1:
                    params.append(f"'{self.column1}'")
                if self.column2:
                    params.append(f"'{self.column2}'")

        # String parameter
        params.append(f"string='{self.field_description}'")

        # Optional parameters
        if self.required:
            params.append("required=True")
        if self.readonly:
            params.append("readonly=True")
        if not self.store and self.is_computed:
            params.append("store=False")
        if self.index:
            params.append("index=True")
        if not self.copy:
            params.append("copy=False")
        if self.translate:
            params.append("translate=True")
        if self.tracking:
            params.append("tracking=True")

        if self.help:
            # Escape quotes in help text
            help_text = self.help.replace("'", "\\'")
            params.append(f"help='{help_text}'")

        if self.placeholder:
            params.append(f"placeholder='{self.placeholder}'")

        if self.default_value:
            params.append(f"default={self.default_value}")

        if self.domain:
            params.append(f"domain={self.domain}")

        if self.context:
            params.append(f"context={self.context}")

        # Relational params
        if self.ttype == 'many2one' and self.on_delete:
            params.append(f"ondelete='{self.on_delete}'")

        # Size/Digits
        if self.size and self.ttype == 'char':
            params.append(f"size={self.size}")

        if self.digits and self.ttype in ('float', 'monetary'):
            params.append(f"digits={self.digits}")

        # Computed field
        if self.is_computed and self.compute_method:
            params.append(f"compute='{self.compute_method}'")
            if self.inverse_method:
                params.append(f"inverse='{self.inverse_method}'")
            if self.search_method:
                params.append(f"search='{self.search_method}'")

        # Related field
        if self.related:
            params.append(f"related='{self.related}'")

        # Company dependent
        if self.company_dependent:
            params.append("company_dependent=True")

        # Binary attachment
        if self.ttype == 'binary' and self.attachment:
            params.append("attachment=True")

        # Groups
        if self.groups:
            group_xmlids = []
            for group in self.groups:
                xmlid = self.env['ir.model.data'].search([
                    ('model', '=', 'res.groups'),
                    ('res_id', '=', group.id)
                ], limit=1)
                if xmlid:
                    group_xmlids.append(f"'{xmlid.module}.{xmlid.name}'")
            if group_xmlids:
                params.append(f"groups={','.join(group_xmlids)}")

        code += ', '.join(params)
        code += ")\n"

        return code

    def action_apply_to_odoo(self, ir_model):
        """Create real ir.model.fields"""
        self.ensure_one()

        vals = {
            'name': self.name,
            'field_description': self.field_description,
            'model_id': ir_model.id,
            'ttype': self.ttype,
            'required': self.required,
            'readonly': self.readonly,
            'store': self.store,
            'index': self.index,
            'help': self.help or '',
            'translate': self.translate,
            'size': self.size or 0,
            'state': 'manual',
        }

        if self.ttype in ('many2one', 'one2many', 'many2many'):
            vals['relation'] = self.relation

        if self.ttype == 'one2many':
            vals['relation_field'] = self.relation_field

        if self.ttype == 'many2many':
            if self.relation_table:
                vals['relation_table'] = self.relation_table
            if self.column1:
                vals['column1'] = self.column1
            if self.column2:
                vals['column2'] = self.column2

        if self.ttype == 'selection' and self.selection:
            vals['selection'] = self.selection

        if self.related:
            vals['related'] = self.related

        # Check if field already exists
        ir_field = self.env['ir.model.fields'].search([
            ('model_id', '=', ir_model.id),
            ('name', '=', self.name)
        ], limit=1)

        if ir_field:
            ir_field.write(vals)
        else:
            ir_field = self.env['ir.model.fields'].create(vals)

        self.ir_model_field_id = ir_field

        return ir_field


class ItxModulerModelFieldSelection(models.Model):
    _name = 'itx.moduler.model.field.selection'
    _description = 'Selection Field Options'
    _order = 'sequence, id'

    field_id = fields.Many2one(
        'itx.moduler.model.field',
        required=True,
        ondelete='cascade'
    )

    sequence = fields.Integer(default=10)

    value = fields.Char(
        string='Technical Value',
        required=True,
        help='e.g., "draft"'
    )

    label = fields.Char(
        string='Display Label',
        required=True,
        help='e.g., "Draft"'
    )

    _value_unique = models.Constraint(
        'UNIQUE(field_id, value)',
        'Selection value must be unique per field!',
    )


class ItxModulerModelMethod(models.Model):
    _name = 'itx.moduler.model.method'
    _description = 'Model Python Methods'
    _order = 'sequence, name'

    model_id = fields.Many2one(
        'itx.moduler.model',
        required=True,
        ondelete='cascade',
        index=True
    )

    sequence = fields.Integer(default=10)

    name = fields.Char(
        string='Method Name',
        required=True,
        help='e.g., "_compute_total"'
    )

    method_type = fields.Selection([
        ('compute', '@api.depends Compute'),
        ('onchange', '@api.onchange'),
        ('constrains', '@api.constrains'),
        ('create', 'Override create()'),
        ('write', 'Override write()'),
        ('unlink', 'Override unlink()'),
        ('custom', 'Custom Method'),
    ], default='custom', required=True)

    decorator = fields.Char(
        string='Decorator',
        help='e.g., "@api.depends(\'qty\', \'price\')"'
    )

    code = fields.Text(
        string='Python Code',
        required=True,
        help='Method implementation (including def line)'
    )

    # AI can describe what method should do
    ai_description = fields.Text(
        string='Method Purpose',
        help='What this method should do (for AI regeneration)'
    )

    created_by_ai = fields.Boolean(default=False)

    _name_unique_method = models.Constraint(
        'UNIQUE(model_id, name)',
        'Method name must be unique per model!',
    )

    @api.constrains('name')
    def _check_method_name(self):
        """Validate method name"""
        pattern = r'^[a-z_][a-z0-9_]*$'
        for record in self:
            if not re.match(pattern, record.name):
                raise ValidationError(
                    f'Method name "{record.name}" is invalid.\n'
                    'Must start with lowercase letter or underscore.'
                )
