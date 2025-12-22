# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class ItxModulerGroup(models.Model):
    _name = 'itx.moduler.group'
    _description = 'ITX Moduler Group (Snapshot)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    # === Core Identification ===
    name = fields.Char(
        string='Group Name',
        required=True,
        tracking=True,
        help='Display name (e.g., "Sales Manager")'
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

    # === Group Configuration ===
    category_id = fields.Many2one(
        'ir.module.category',
        string='Application',
        help='Category/Application this group belongs to'
    )

    comment = fields.Text(
        string='Description',
        translate=True,
        help='Group description'
    )

    implied_ids = fields.Many2many(
        'res.groups',
        'itx_moduler_group_implied_rel',
        'gid',
        'hid',
        string='Implied Groups',
        help='Users in this group automatically get these groups'
    )

    # === State & Tracking ===
    state = fields.Selection([
        ('draft', 'Draft'),
        ('validated', 'Validated'),
        ('applied', 'Applied'),
        ('exported', 'Exported'),
        ('archived', 'Archived')
    ], default='draft', required=True, tracking=True, index=True)

    # Link to real res.groups when applied
    ir_group_id = fields.Many2one(
        'res.groups',
        string='Applied Group',
        readonly=True,
        help='Link to real res.groups when state=applied'
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
        help='Prompt used to generate this group (if from AI)',
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
        'itx.moduler.group',
        string='Parent Version',
        readonly=True,
        help='Previous version of this group'
    )

    # === Actions ===
    def action_validate(self):
        """Validate group before applying"""
        self.ensure_one()

        if self.state != 'draft':
            raise UserError(_('Only draft groups can be validated'))

        self.state = 'validated'
        return True

    def action_apply_to_odoo(self):
        """Apply group to Odoo (create/update res.groups)"""
        self.ensure_one()

        if self.state not in ('validated', 'applied'):
            raise UserError(_('Group must be validated before applying'))

        # Find or create res.groups
        ir_group = self.env['res.groups'].search([
            ('name', '=', self.name),
        ], limit=1)

        vals = {
            'name': self.name,
            'comment': self.comment or '',
        }

        if self.category_id:
            vals['category_id'] = self.category_id.id

        if self.implied_ids:
            vals['implied_ids'] = [(6, 0, self.implied_ids.ids)]

        if ir_group:
            ir_group.write(vals)
        else:
            ir_group = self.env['res.groups'].create(vals)

        self.write({
            'state': 'applied',
            'ir_group_id': ir_group.id,
            'applied_date': fields.Datetime.now(),
        })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Applied'),
                'message': _('Group "%s" applied successfully') % self.name,
                'type': 'success',
            }
        }

    def _generate_group_xml(self):
        """Generate group XML for export"""
        self.ensure_one()

        xml = '<?xml version="1.0"?>\n'
        xml += '<odoo>\n'

        # Generate group record
        group_id = self.name.lower().replace(' ', '_').replace('.', '_')
        xml += f'  <record id="group_{group_id}" model="res.groups">\n'
        xml += f'    <field name="name">{self.name}</field>\n'

        if self.category_id:
            # Try to find XML ID for category
            category_xmlid = self.env['ir.model.data'].search([
                ('model', '=', 'ir.module.category'),
                ('res_id', '=', self.category_id.id)
            ], limit=1)
            if category_xmlid:
                xml += f'    <field name="category_id" ref="{category_xmlid.module}.{category_xmlid.name}"/>\n'

        if self.comment:
            xml += f'    <field name="comment">{self.comment}</field>\n'

        if self.implied_ids:
            implied_refs = []
            for implied in self.implied_ids:
                implied_xmlid = self.env['ir.model.data'].search([
                    ('model', '=', 'res.groups'),
                    ('res_id', '=', implied.id)
                ], limit=1)
                if implied_xmlid:
                    implied_refs.append(f'ref("{implied_xmlid.module}.{implied_xmlid.name}")')

            if implied_refs:
                xml += f'    <field name="implied_ids" eval="[{", ".join(implied_refs)}]"/>\n'

        xml += '  </record>\n'
        xml += '</odoo>'

        return xml
