# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class ItxModulerMenu(models.Model):
    _name = 'itx.moduler.menu'
    _description = 'ITX Moduler Menu (Snapshot)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, name'
    _parent_name = 'parent_id'
    _parent_store = True

    # === Core Identification ===
    name = fields.Char(
        string='Menu Name',
        required=True,
        tracking=True,
        translate=True,
        help='Display name of menu item'
    )

    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Display order'
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

    # === Menu Hierarchy ===
    parent_id = fields.Many2one(
        'itx.moduler.menu',
        string='Parent Menu',
        ondelete='restrict',
        index=True,
        help='Parent menu item (for submenu structure)'
    )

    parent_path = fields.Char(
        index=True
    )

    child_ids = fields.One2many(
        'itx.moduler.menu',
        'parent_id',
        string='Submenus'
    )

    # Link to existing Odoo menu (for extending)
    parent_odoo_menu_id = fields.Many2one(
        'ir.ui.menu',
        string='Existing Parent Menu',
        help='Add as submenu under existing Odoo menu (e.g., Settings, Sales)'
    )

    # === Action Link ===
    action_id = fields.Many2one(
        'itx.moduler.action.window',
        string='Window Action',
        help='Action to trigger when menu is clicked'
    )

    # === Display Options ===
    web_icon = fields.Char(
        string='Icon',
        help='Icon for menu (e.g., "fa-dashboard", "itx_moduler,static/description/icon.png")'
    )

    # === Security ===
    group_ids = fields.Many2many(
        'res.groups',
        'itx_moduler_menu_group_rel',
        'menu_id',
        'group_id',
        string='Groups',
        help='Only these groups can see this menu'
    )

    # === State & Tracking ===
    state = fields.Selection([
        ('draft', 'Draft'),
        ('validated', 'Validated'),
        ('applied', 'Applied'),
        ('exported', 'Exported'),
        ('archived', 'Archived')
    ], default='draft', required=True, tracking=True, index=True)

    # Link to real ir.ui.menu when applied
    ir_menu_id = fields.Many2one(
        'ir.ui.menu',
        string='Applied Menu',
        readonly=True,
        help='Link to real ir.ui.menu when state=applied'
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
        help='Prompt used to generate this menu (if from AI)',
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
        'itx.moduler.menu',
        string='Parent Version',
        readonly=True,
        help='Previous version of this menu'
    )

    # === Compatibility Properties ===
    @property
    def action(self):
        """Compatibility: ir.ui.menu uses 'action', we use 'action_id'"""
        return self.action_id

    @property
    def active(self):
        """Compatibility: menus are active by default"""
        return True

    # === Computed Fields ===
    complete_name = fields.Char(
        string='Complete Name',
        compute='_compute_complete_name',
        recursive=True,
        store=True
    )

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for menu in self:
            if menu.parent_id:
                menu.complete_name = f'{menu.parent_id.complete_name} / {menu.name}'
            else:
                menu.complete_name = menu.name

    # === Validations ===
    @api.constrains('parent_id')
    def _check_parent_recursion(self):
        """Prevent circular menu hierarchy"""
        if not self._check_recursion():
            raise ValidationError(
                _('Error! You cannot create recursive menus.')
            )

    # === Actions ===
    def action_validate(self):
        """Validate menu before applying"""
        self.ensure_one()

        if self.state != 'draft':
            raise UserError(_('Only draft menus can be validated'))

        # Validate that action exists if specified
        if self.action_id and self.action_id.state not in ('validated', 'applied'):
            raise ValidationError(
                _('Action "%s" must be validated first!') % self.action_id.name
            )

        self.state = 'validated'
        return True

    def action_apply_to_odoo(self):
        """Apply menu to Odoo (create/update ir.ui.menu)"""
        self.ensure_one()

        if self.state not in ('validated', 'applied'):
            raise UserError(_('Menu must be validated before applying'))

        # Apply action first if exists
        if self.action_id and not self.action_id.ir_action_id:
            self.action_id.action_apply_to_odoo()

        # Determine parent
        parent_id = False
        if self.parent_id and self.parent_id.ir_menu_id:
            parent_id = self.parent_id.ir_menu_id.id
        elif self.parent_odoo_menu_id:
            parent_id = self.parent_odoo_menu_id.id

        # Find or create ir.ui.menu
        ir_menu = self.env['ir.ui.menu'].search([
            ('name', '=', self.name),
            ('parent_id', '=', parent_id)
        ], limit=1)

        vals = {
            'name': self.name,
            'sequence': self.sequence,
            'parent_id': parent_id,
            'web_icon': self.web_icon,
        }

        if self.action_id and self.action_id.ir_action_id:
            vals['action'] = f'ir.actions.act_window,{self.action_id.ir_action_id.id}'

        if self.group_ids:
            vals['groups_id'] = [(6, 0, self.group_ids.ids)]

        if ir_menu:
            ir_menu.write(vals)
        else:
            ir_menu = self.env['ir.ui.menu'].create(vals)

        self.write({
            'state': 'applied',
            'ir_menu_id': ir_menu.id,
            'applied_date': fields.Datetime.now(),
        })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Applied'),
                'message': _('Menu "%s" applied successfully') % self.name,
                'type': 'success',
            }
        }

    def action_generate_xml(self):
        """Generate XML code for export"""
        self.ensure_one()

        code = self._generate_menu_xml()

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

    def _generate_menu_xml(self):
        """Generate menu XML for export"""
        self.ensure_one()

        xml = '<?xml version="1.0"?>\n'
        xml += '<odoo>\n'

        # Generate menu item
        menu_id = self.name.lower().replace(' ', '_')
        xml += f'  <menuitem id="{menu_id}"\n'
        xml += f'            name="{self.name}"\n'

        if self.parent_id:
            parent_xml_id = self.parent_id.name.lower().replace(' ', '_')
            xml += f'            parent="{parent_xml_id}"\n'
        elif self.parent_odoo_menu_id:
            # Try to get XML ID of parent
            data = self.env['ir.model.data'].search([
                ('model', '=', 'ir.ui.menu'),
                ('res_id', '=', self.parent_odoo_menu_id.id)
            ], limit=1)
            if data:
                xml += f'            parent="{data.module}.{data.name}"\n'

        if self.action_id:
            action_xml_id = self.action_id.name.lower().replace(' ', '_').replace('.', '_')
            xml += f'            action="{action_xml_id}"\n'

        xml += f'            sequence="{self.sequence}"\n'

        if self.web_icon:
            xml += f'            web_icon="{self.web_icon}"\n'

        if self.group_ids:
            groups_str = ','.join([f'base.{g.name}' for g in self.group_ids])
            xml += f'            groups="{groups_str}"\n'

        xml += '  />\n'
        xml += '</odoo>'

        return xml
