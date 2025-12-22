# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class ItxModulerRule(models.Model):
    _name = 'itx.moduler.rule'
    _description = 'ITX Moduler Record Rule (Snapshot)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'model_id, name'

    # === Core Identification ===
    name = fields.Char(
        string='Rule Name',
        required=True,
        help='Display name (e.g., "User sees own records")'
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
        help='Model this rule applies to'
    )

    model_name = fields.Char(
        string='Model Name',
        related='model_id.model',
        readonly=True,
        store=True
    )

    # === Rule Configuration ===
    active = fields.Boolean(
        string='Active',
        default=True,
        help='Deactivate to disable rule without deleting'
    )

    domain_force = fields.Text(
        string='Domain',
        required=True,
        default='[]',
        help='Domain filter (e.g., [(\'user_id\', \'=\', user.id)])'
    )

    # === Groups (which groups this rule applies to) ===
    group_ids = fields.Many2many(
        'itx.moduler.group',
        'itx_moduler_rule_group_rel',
        'rule_id',
        'group_id',
        string='Groups',
        help='Groups this rule applies to (empty = global rule)'
    )

    # External groups (for rules referencing base groups)
    external_group_ids = fields.Many2many(
        'res.groups',
        'itx_moduler_rule_ext_group_rel',
        'rule_id',
        'group_id',
        string='External Groups',
        help='Reference to existing Odoo groups (e.g., base.group_user)'
    )

    # === Permissions ===
    perm_read = fields.Boolean(
        string='Apply on Read',
        default=True,
        help='Apply rule on read operations'
    )

    perm_write = fields.Boolean(
        string='Apply on Write',
        default=True,
        help='Apply rule on write operations'
    )

    perm_create = fields.Boolean(
        string='Apply on Create',
        default=True,
        help='Apply rule on create operations'
    )

    perm_unlink = fields.Boolean(
        string='Apply on Delete',
        default=True,
        help='Apply rule on delete operations'
    )

    # === Global vs Group Rule ===
    global_rule = fields.Boolean(
        string='Global Rule',
        default=False,
        help='If True, applies to all users (ignore groups)'
    )

    # === State & Tracking ===
    state = fields.Selection([
        ('draft', 'Draft'),
        ('validated', 'Validated'),
        ('applied', 'Applied'),
        ('exported', 'Exported'),
        ('archived', 'Archived')
    ], default='draft', required=True, index=True)

    # Link to real ir.rule when applied
    ir_rule_id = fields.Many2one(
        'ir.rule',
        string='Applied Rule',
        readonly=True,
        help='Link to real ir.rule when state=applied'
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
        help='Prompt used to generate this rule (if from AI)'
    )

    # === Version Control ===
    version = fields.Integer(
        string='Version',
        default=1,
        readonly=True
    )

    parent_version_id = fields.Many2one(
        'itx.moduler.rule',
        string='Parent Version',
        readonly=True,
        help='Previous version of this rule'
    )

    # === Validations ===
    @api.constrains('domain_force')
    def _check_domain(self):
        """Validate domain syntax"""
        for rule in self:
            if rule.domain_force and rule.domain_force != '[]':
                domain_str = rule.domain_force.strip()
                if not (domain_str.startswith('[') and domain_str.endswith(']')):
                    raise ValidationError(
                        f'Domain must be a valid Python list\nGot: {rule.domain_force}'
                    )

    # === Actions ===
    def action_validate(self):
        """Validate rule before applying"""
        self.ensure_one()

        if self.state != 'draft':
            raise UserError(_('Only draft rules can be validated'))

        # Validate domain
        self._check_domain()

        self.state = 'validated'
        return True

    def action_apply_to_odoo(self):
        """Apply rule to Odoo (create/update ir.rule)"""
        self.ensure_one()

        if self.state not in ('validated', 'applied'):
            raise UserError(_('Rule must be validated before applying'))

        # Check if model is applied
        if not self.model_id.ir_model_id:
            raise UserError(
                _('Model "%s" must be applied first!') % self.model_id.name
            )

        # Find or create ir.rule
        ir_rule = self.env['ir.rule'].search([
            ('name', '=', self.name),
            ('model_id', '=', self.model_id.ir_model_id.id),
        ], limit=1)

        vals = {
            'name': self.name,
            'model_id': self.model_id.ir_model_id.id,
            'domain_force': self.domain_force,
            'active': self.active,
            'perm_read': self.perm_read,
            'perm_write': self.perm_write,
            'perm_create': self.perm_create,
            'perm_unlink': self.perm_unlink,
            'global': self.global_rule,
        }

        # Handle groups
        group_ids = []
        if self.group_ids:
            for group in self.group_ids:
                if group.ir_group_id:
                    group_ids.append(group.ir_group_id.id)
        if self.external_group_ids:
            group_ids.extend(self.external_group_ids.ids)

        if group_ids:
            vals['groups'] = [(6, 0, group_ids)]

        if ir_rule:
            ir_rule.write(vals)
        else:
            ir_rule = self.env['ir.rule'].create(vals)

        self.write({
            'state': 'applied',
            'ir_rule_id': ir_rule.id,
            'applied_date': fields.Datetime.now(),
        })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Applied'),
                'message': _('Rule "%s" applied successfully') % self.name,
                'type': 'success',
            }
        }

    def _generate_rule_xml(self):
        """Generate rule XML for export"""
        self.ensure_one()

        xml = '<?xml version="1.0"?>\n'
        xml += '<odoo>\n'

        # Generate rule record
        rule_id = self.name.lower().replace(' ', '_').replace('.', '_')
        xml += f'  <record id="rule_{rule_id}" model="ir.rule">\n'
        xml += f'    <field name="name">{self.name}</field>\n'
        xml += f'    <field name="model_id" ref="model_{self.model_id.model.replace(".", "_")}"/>\n'
        xml += f'    <field name="domain_force">{self.domain_force}</field>\n'

        if not self.active:
            xml += '    <field name="active" eval="False"/>\n'

        if not self.perm_read:
            xml += '    <field name="perm_read" eval="False"/>\n'
        if not self.perm_write:
            xml += '    <field name="perm_write" eval="False"/>\n'
        if not self.perm_create:
            xml += '    <field name="perm_create" eval="False"/>\n'
        if not self.perm_unlink:
            xml += '    <field name="perm_unlink" eval="False"/>\n'

        if self.global_rule:
            xml += '    <field name="global" eval="True"/>\n'

        # Handle groups
        if self.group_ids or self.external_group_ids:
            group_refs = []
            for group in self.group_ids:
                group_xmlid = f"group_{group.name.lower().replace(' ', '_')}"
                group_refs.append(f'ref("{group_xmlid}")')

            for ext_group in self.external_group_ids:
                ext_xmlid = self.env['ir.model.data'].search([
                    ('model', '=', 'res.groups'),
                    ('res_id', '=', ext_group.id)
                ], limit=1)
                if ext_xmlid:
                    group_refs.append(f'ref("{ext_xmlid.module}.{ext_xmlid.name}")')

            if group_refs:
                xml += f'    <field name="groups" eval="[(4, {"), (4, ".join(group_refs)})]"/>\n'

        xml += '  </record>\n'
        xml += '</odoo>'

        return xml
