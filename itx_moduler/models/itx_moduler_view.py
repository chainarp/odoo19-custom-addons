# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class ItxModulerView(models.Model):
    _name = 'itx.moduler.view'
    _description = 'ITX Moduler View (Snapshot)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, name'

    # === Core Identification ===
    name = fields.Char(
        string='View Name',
        required=True,
        tracking=True,
        help='Technical view name (e.g., "product.template.form")'
    )

    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Order in view priority'
    )

    # === Module & Model Link ===
    module_id = fields.Many2one(
        'itx.moduler.module',
        string='Module',
        required=True,
        ondelete='cascade',
        tracking=True,
        index=True
    )

    model_id = fields.Many2one(
        'itx.moduler.model',
        string='Model',
        required=True,
        ondelete='cascade',
        tracking=True,
        index=True,
        help='Model this view is for'
    )

    # === View Configuration ===
    view_type = fields.Selection([
        ('form', 'Form'),
        ('list', 'List'),
        ('tree', 'Tree (deprecated)'),
        ('kanban', 'Kanban'),
        ('search', 'Search'),
        ('calendar', 'Calendar'),
        ('pivot', 'Pivot'),
        ('graph', 'Graph'),
        ('gantt', 'Gantt'),
        ('activity', 'Activity'),
    ], string='View Type', required=True, default='form', tracking=True)

    # View architecture - can be AI generated or manually edited
    arch = fields.Text(
        string='Architecture (XML)',
        help='View XML architecture',
        tracking=True
    )

    # Simple mode: Let user pick fields, we generate XML
    field_ids = fields.One2many(
        'itx.moduler.view.field',
        'view_id',
        string='View Fields',
        help='Fields to display in this view (simple mode)'
    )

    field_count = fields.Integer(
        string='Field Count',
        compute='_compute_field_count',
        store=True
    )

    # Inherit from existing view
    inherit_id = fields.Many2one(
        'ir.ui.view',
        string='Inherited View',
        help='View to inherit from (for customization)'
    )

    mode = fields.Selection([
        ('primary', 'Primary View'),
        ('extension', 'View Extension (inherit_id)')
    ], default='primary', required=True, tracking=True)

    # === State & Tracking ===
    state = fields.Selection([
        ('draft', 'Draft'),
        ('validated', 'Validated'),
        ('applied', 'Applied'),
        ('exported', 'Exported'),
        ('archived', 'Archived')
    ], default='draft', required=True, tracking=True, index=True)

    # Link to real ir.ui.view when applied
    ir_view_id = fields.Many2one(
        'ir.ui.view',
        string='Applied View',
        readonly=True,
        help='Link to real ir.ui.view when state=applied'
    )

    applied_date = fields.Datetime(
        string='Applied Date',
        readonly=True
    )

    # === AI Integration ===
    created_by_ai = fields.Boolean(
        string='AI Generated',
        default=False,
        tracking=True
    )

    ai_prompt = fields.Text(
        string='AI Prompt',
        help='Prompt used to generate this view (if from AI)',
        tracking=True
    )

    # === Version Control ===
    version = fields.Integer(
        string='Version',
        default=1,
        readonly=True,
        tracking=True
    )

    parent_version_id = fields.Many2one(
        'itx.moduler.view',
        string='Parent Version',
        readonly=True,
        help='Previous version of this view'
    )

    # === Compatibility Properties ===
    @property
    def type(self):
        """Compatibility: ir.ui.view uses 'type', we use 'view_type'"""
        return self.view_type

    @property
    def model(self):
        """Compatibility: return model technical name"""
        return self.model_id.model if self.model_id else ''

    @property
    def key(self):
        """Compatibility: ir.ui.view uses 'key' for view reference"""
        return False  # Most views don't have keys

    @property
    def priority(self):
        """Compatibility: view priority (default 16)"""
        return 16

    @property
    def active(self):
        """Compatibility: views are active by default"""
        return True

    @property
    def arch_db(self):
        """Compatibility: ir.ui.view uses 'arch_db', we use 'arch'"""
        return self.arch

    @property
    def group_ids(self):
        """Compatibility: groups with access to this view"""
        # TODO: Implement view-level group access in future
        return self.env['res.groups'].browse([])

    # === Computed Fields ===
    @api.depends('field_ids')
    def _compute_field_count(self):
        for view in self:
            view.field_count = len(view.field_ids)

    # === Validations ===
    @api.constrains('mode', 'inherit_id')
    def _check_inherit_mode(self):
        """Extension mode requires inherit_id"""
        for view in self:
            if view.mode == 'extension' and not view.inherit_id:
                raise ValidationError(
                    'Extension mode requires selecting an Inherited View!'
                )

    # === Actions ===
    def action_validate(self):
        """Validate view before applying"""
        self.ensure_one()

        if self.state != 'draft':
            raise UserError(_('Only draft views can be validated'))

        # Validate XML if provided
        if self.arch:
            try:
                from lxml import etree
                etree.fromstring(self.arch)
            except Exception as e:
                raise ValidationError(
                    f'Invalid XML architecture: {str(e)}'
                )

        self.state = 'validated'
        return True

    def action_apply_to_odoo(self):
        """Apply view to Odoo (create/update ir.ui.view)"""
        self.ensure_one()

        if self.state not in ('validated', 'applied'):
            raise UserError(_('View must be validated before applying'))

        # Check if model is applied
        if not self.model_id.ir_model_id:
            raise UserError(
                _('Model "%s" must be applied first!') % self.model_id.name
            )

        # Generate arch if not provided
        if not self.arch:
            self.arch = self._generate_view_arch()

        # Find or create ir.ui.view
        ir_view = self.env['ir.ui.view'].search([
            ('name', '=', self.name)
        ], limit=1)

        vals = {
            'name': self.name,
            'model': self.model_id.model,
            'type': self.view_type,
            'arch': self.arch,
        }

        if self.inherit_id:
            vals['inherit_id'] = self.inherit_id.id
            vals['mode'] = 'extension'

        if ir_view:
            ir_view.write(vals)
        else:
            ir_view = self.env['ir.ui.view'].create(vals)

        self.write({
            'state': 'applied',
            'ir_view_id': ir_view.id,
            'applied_date': fields.Datetime.now(),
        })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Applied'),
                'message': _('View "%s" applied successfully') % self.name,
                'type': 'success',
            }
        }

    def action_generate_xml(self):
        """Generate XML code for export"""
        self.ensure_one()

        code = self._generate_view_arch()

        return {
            'type': 'ir.actions.act_window',
            'name': f'Generated XML - {self.name}',
            'res_model': 'itx.moduler.code.viewer',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_code': code,
                'default_language': 'xml'
            }
        }

    def _generate_view_arch(self):
        """Generate view XML from field configuration"""
        self.ensure_one()

        if self.view_type == 'form':
            return self._generate_form_view()
        elif self.view_type in ('list', 'tree'):
            return self._generate_tree_view()
        elif self.view_type == 'kanban':
            return self._generate_kanban_view()
        elif self.view_type == 'search':
            return self._generate_search_view()
        else:
            return '<list><field name="name"/></list>'

    def _generate_form_view(self):
        """Generate form view XML"""
        xml = '<?xml version="1.0"?>\n'
        xml += '<form string="{}">\n'.format(self.model_id.name)
        xml += '  <sheet>\n'
        xml += '    <group>\n'

        for view_field in self.field_ids.sorted('sequence'):
            field = view_field.field_id
            attrs = []
            if view_field.required:
                attrs.append('required="1"')
            if view_field.readonly:
                attrs.append('readonly="1"')
            if view_field.invisible:
                attrs.append('invisible="1"')

            attrs_str = ' '.join(attrs)
            if attrs_str:
                xml += f'      <field name="{field.name}" {attrs_str}/>\n'
            else:
                xml += f'      <field name="{field.name}"/>\n'

        xml += '    </group>\n'
        xml += '  </sheet>\n'
        xml += '</form>'

        return xml

    def _generate_tree_view(self):
        """Generate tree/list view XML"""
        xml = '<?xml version="1.0"?>\n'
        xml += '<list string="{}">\n'.format(self.model_id.name)

        for view_field in self.field_ids.sorted('sequence'):
            field = view_field.field_id
            attrs = []
            if view_field.readonly:
                attrs.append('readonly="1"')
            if view_field.invisible:
                attrs.append('invisible="1"')

            attrs_str = ' '.join(attrs)
            if attrs_str:
                xml += f'  <field name="{field.name}" {attrs_str}/>\n'
            else:
                xml += f'  <field name="{field.name}"/>\n'

        xml += '</list>'
        return xml

    def _generate_kanban_view(self):
        """Generate kanban view XML"""
        xml = '<?xml version="1.0"?>\n'
        xml += '<kanban>\n'
        xml += '  <templates>\n'
        xml += '    <t t-name="kanban-box">\n'
        xml += '      <div class="oe_kanban_card">\n'
        xml += '        <div class="oe_kanban_content">\n'

        for view_field in self.field_ids.sorted('sequence')[:5]:  # Limit to first 5
            field = view_field.field_id
            xml += f'          <field name="{field.name}"/>\n'

        xml += '        </div>\n'
        xml += '      </div>\n'
        xml += '    </t>\n'
        xml += '  </templates>\n'
        xml += '</kanban>'
        return xml

    def _generate_search_view(self):
        """Generate search view XML"""
        xml = '<?xml version="1.0"?>\n'
        xml += '<search string="{}">\n'.format(self.model_id.name)

        for view_field in self.field_ids.sorted('sequence'):
            field = view_field.field_id
            xml += f'  <field name="{field.name}"/>\n'

        xml += '</search>'
        return xml


class ItxModulerViewField(models.Model):
    _name = 'itx.moduler.view.field'
    _description = 'View Field Configuration'
    _order = 'sequence, id'

    view_id = fields.Many2one(
        'itx.moduler.view',
        string='View',
        required=True,
        ondelete='cascade',
        index=True
    )

    field_id = fields.Many2one(
        'itx.moduler.model.field',
        string='Field',
        required=True,
        ondelete='cascade',
        domain="[('model_id', '=', model_id)]"
    )

    model_id = fields.Many2one(
        'itx.moduler.model',
        related='view_id.model_id',
        store=True,
        string='Model'
    )

    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Display order in view'
    )

    # Field visibility/behavior in this view
    invisible = fields.Boolean(
        string='Invisible',
        default=False,
        help='Hide this field in view'
    )

    readonly = fields.Boolean(
        string='Readonly',
        default=False,
        help='Make field readonly in this view'
    )

    required = fields.Boolean(
        string='Required',
        default=False,
        help='Make field required in this view'
    )

    # Widget override
    widget = fields.Char(
        string='Widget',
        help='Override default widget (e.g., "many2many_tags", "image", "html")'
    )

    # Display options
    colspan = fields.Integer(
        string='Colspan',
        help='Column span in form view'
    )

    # Computed display name
    name = fields.Char(
        string='Field Name',
        related='field_id.name',
        readonly=True
    )
