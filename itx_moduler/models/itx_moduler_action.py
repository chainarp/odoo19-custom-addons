# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import json


class ItxModulerActionWindow(models.Model):
    _name = 'itx.moduler.action.window'
    _description = 'ITX Moduler Window Action (Snapshot)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    # === Core Identification ===
    name = fields.Char(
        string='Action Name',
        required=True,
        tracking=True,
        help='Display name (e.g., "Products")'
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

    # === Target Model ===
    model_id = fields.Many2one(
        'itx.moduler.model',
        string='Model',
        required=True,
        ondelete='cascade',
        tracking=True,
        help='Model this action opens'
    )

    res_model = fields.Char(
        string='Model Name',
        related='model_id.model',
        readonly=True
    )

    # === View Configuration ===
    view_mode = fields.Char(
        string='View Mode',
        default='tree,form',
        required=True,
        help='Comma-separated view types (e.g., "tree,form,kanban")'
    )

    view_ids = fields.Many2many(
        'itx.moduler.view',
        'itx_moduler_action_view_rel',
        'action_id',
        'view_id',
        string='Views',
        help='Specific views to use (optional). Leave empty for default views.',
        domain="[('model_id', '=', model_id)]"
    )

    # === Filters & Context ===
    domain = fields.Char(
        string='Domain',
        default='[]',
        help='Filter records (Python list format, e.g., "[("active", "=", True)]")'
    )

    context = fields.Char(
        string='Context',
        default='{}',
        help='Additional context (Python dict format, e.g., "{"default_type": "sale"}")'
    )

    # === Display Options ===
    limit = fields.Integer(
        string='Limit',
        default=80,
        help='Default number of records per page'
    )

    target = fields.Selection([
        ('current', 'Current Window'),
        ('new', 'New Window'),
        ('inline', 'Inline'),
        ('fullscreen', 'Full Screen'),
        ('main', 'Main Action'),
    ], string='Target', default='current', required=True)

    # === Help Text ===
    help = fields.Html(
        string='Help',
        translate=True,
        help='Help text shown when no records'
    )

    # === Search View ===
    search_view_id = fields.Many2one(
        'itx.moduler.view',
        string='Search View',
        domain="[('model_id', '=', model_id), ('view_type', '=', 'search')]",
        help='Custom search view'
    )

    # === Binding ===
    binding_model_id = fields.Many2one(
        'ir.model',
        string='Binding Model',
        help='Add this action to another model (Action menu)'
    )

    binding_type = fields.Selection([
        ('action', 'Action'),
        ('report', 'Report'),
    ], string='Binding Type', default='action')

    # === State & Tracking ===
    state = fields.Selection([
        ('draft', 'Draft'),
        ('validated', 'Validated'),
        ('applied', 'Applied'),
        ('exported', 'Exported'),
        ('archived', 'Archived')
    ], default='draft', required=True, tracking=True, index=True)

    # Link to real ir.actions.act_window when applied
    ir_action_id = fields.Many2one(
        'ir.actions.act_window',
        string='Applied Action',
        readonly=True,
        help='Link to real ir.actions.act_window when state=applied'
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
        help='Prompt used to generate this action (if from AI)',
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
        'itx.moduler.action.window',
        string='Parent Version',
        readonly=True,
        help='Previous version of this action'
    )

    # === Compatibility Properties ===
    @property
    def m2o_res_model(self):
        """Compatibility: reference to model object"""
        return self.model_id

    @property
    def view_id(self):
        """Compatibility: first view in view_ids"""
        return self.view_ids[0] if self.view_ids else False

    @property
    def src_model(self):
        """Compatibility: source model for context actions"""
        return False

    @property
    def m2o_src_model(self):
        """Compatibility: source model object"""
        return False

    @property
    def view_type(self):
        """Compatibility: legacy view_type (deprecated in Odoo, use view_mode)"""
        return 'form'

    @property
    def usage(self):
        """Compatibility: usage field (menu action vs inline)"""
        return False

    @property
    def filter(self):
        """Compatibility: filter flag"""
        return False

    @property
    def auto_search(self):
        """Compatibility: auto search flag"""
        return True

    @property
    def multi(self):
        """Compatibility: allow multiple record selection"""
        return False

    @property
    def group_ids(self):
        """Compatibility: groups with access to this action"""
        # TODO: Implement action-level group access in future
        return self.env['res.groups'].browse([])

    # === Validations ===
    @api.constrains('domain')
    def _check_domain(self):
        """Validate domain syntax"""
        for action in self:
            if action.domain and action.domain != '[]':
                # Only do basic validation - allow domains with variables like active_id
                domain_str = action.domain.strip()
                if not (domain_str.startswith('[') and domain_str.endswith(']')):
                    raise ValidationError(
                        f'Domain must be a valid Python list (e.g., "[]" or "[("field", "=", value)]")\n'
                        f'Got: {action.domain}'
                    )

    @api.constrains('context')
    def _check_context(self):
        """Validate context syntax"""
        for action in self:
            if action.context and action.context != '{}':
                # Only do basic validation - allow contexts with variables like active_id
                context_str = action.context.strip()
                if not (context_str.startswith('{') and context_str.endswith('}')):
                    raise ValidationError(
                        f'Context must be a valid Python dict (e.g., "{{}}" or "{{"key": "value"}}")\n'
                        f'Got: {action.context}'
                    )

    # === Actions ===
    def action_validate(self):
        """Validate action before applying"""
        self.ensure_one()

        if self.state != 'draft':
            raise UserError(_('Only draft actions can be validated'))

        # Validate that model exists
        if not self.model_id:
            raise ValidationError(_('Model is required!'))

        # Validate domain and context
        self._check_domain()
        self._check_context()

        self.state = 'validated'
        return True

    def action_apply_to_odoo(self):
        """Apply action to Odoo (create/update ir.actions.act_window)"""
        self.ensure_one()

        if self.state not in ('validated', 'applied'):
            raise UserError(_('Action must be validated before applying'))

        # Check if model is applied
        if not self.model_id.ir_model_id:
            raise UserError(
                _('Model "%s" must be applied first!') % self.model_id.name
            )

        # Find or create ir.actions.act_window
        ir_action = self.env['ir.actions.act_window'].search([
            ('name', '=', self.name),
            ('res_model', '=', self.model_id.model)
        ], limit=1)

        vals = {
            'name': self.name,
            'res_model': self.model_id.model,
            'view_mode': self.view_mode,
            'domain': self.domain or '[]',
            'context': self.context or '{}',
            'limit': self.limit,
            'target': self.target,
            'help': self.help or '',
        }

        if self.search_view_id and self.search_view_id.ir_view_id:
            vals['search_view_id'] = self.search_view_id.ir_view_id.id

        if self.binding_model_id:
            vals['binding_model_id'] = self.binding_model_id.id
            vals['binding_type'] = self.binding_type

        if ir_action:
            ir_action.write(vals)
        else:
            ir_action = self.env['ir.actions.act_window'].create(vals)

        # Link specific views if specified
        if self.view_ids:
            # Clear existing view references
            ir_action.view_ids.unlink()

            # Create new view references
            for idx, view in enumerate(self.view_ids.sorted('sequence')):
                if view.ir_view_id:
                    self.env['ir.actions.act_window.view'].create({
                        'act_window_id': ir_action.id,
                        'view_id': view.ir_view_id.id,
                        'view_mode': view.view_type,
                        'sequence': idx + 1,
                    })

        self.write({
            'state': 'applied',
            'ir_action_id': ir_action.id,
            'applied_date': fields.Datetime.now(),
        })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Applied'),
                'message': _('Action "%s" applied successfully') % self.name,
                'type': 'success',
            }
        }

    def action_generate_xml(self):
        """Generate XML code for export"""
        self.ensure_one()

        code = self._generate_action_xml()

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

    def _generate_action_xml(self):
        """Generate action XML for export"""
        self.ensure_one()

        xml = '<?xml version="1.0"?>\n'
        xml += '<odoo>\n'

        # Generate action record
        action_id = self.name.lower().replace(' ', '_').replace('.', '_')
        xml += f'  <record id="{action_id}" model="ir.actions.act_window">\n'
        xml += f'    <field name="name">{self.name}</field>\n'
        xml += f'    <field name="res_model">{self.model_id.model}</field>\n'
        xml += f'    <field name="view_mode">{self.view_mode}</field>\n'

        if self.domain and self.domain != '[]':
            xml += f'    <field name="domain">{self.domain}</field>\n'

        if self.context and self.context != '{}':
            xml += f'    <field name="context">{self.context}</field>\n'

        if self.limit != 80:
            xml += f'    <field name="limit">{self.limit}</field>\n'

        if self.target != 'current':
            xml += f'    <field name="target">{self.target}</field>\n'

        if self.help:
            xml += f'    <field name="help" type="html">{self.help}</field>\n'

        if self.search_view_id:
            search_xml_id = self.search_view_id.name.lower().replace(' ', '_').replace('.', '_')
            xml += f'    <field name="search_view_id" ref="{search_xml_id}"/>\n'

        if self.binding_model_id:
            xml += f'    <field name="binding_model_id" ref="base.model_{self.binding_model_id.model.replace(".", "_")}"/>\n'
            xml += f'    <field name="binding_type">{self.binding_type}</field>\n'

        xml += '  </record>\n'

        # Generate view references if specified
        if self.view_ids:
            for idx, view in enumerate(self.view_ids.sorted('sequence')):
                view_xml_id = view.name.lower().replace(' ', '_').replace('.', '_')
                xml += f'\n  <record id="{action_id}_view_{idx+1}" model="ir.actions.act_window.view">\n'
                xml += f'    <field name="act_window_id" ref="{action_id}"/>\n'
                xml += f'    <field name="view_id" ref="{view_xml_id}"/>\n'
                xml += f'    <field name="view_mode">{view.view_type}</field>\n'
                xml += f'    <field name="sequence">{idx+1}</field>\n'
                xml += '  </record>\n'

        xml += '</odoo>'

        return xml

    def action_test(self):
        """Test this action (open it)"""
        self.ensure_one()

        if not self.ir_action_id:
            raise UserError(_('Action must be applied before testing'))

        return {
            'type': 'ir.actions.act_window',
            'name': self.name,
            'res_model': self.model_id.model,
            'view_mode': self.view_mode,
            'domain': eval(self.domain) if self.domain else [],
            'context': eval(self.context) if self.context else {},
            'limit': self.limit,
            'target': self.target,
        }
