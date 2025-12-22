# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class ItxModulerServerAction(models.Model):
    _name = 'itx.moduler.server.action'
    _description = 'ITX Moduler Server Action (Snapshot)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'model_id, name'

    # === Core Identification ===
    name = fields.Char(
        string='Action Name',
        required=True,
        help='Display name (e.g., "Auto-assign Sales Team")'
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
        help='Model this action operates on'
    )

    model_name = fields.Char(
        string='Model Name',
        related='model_id.model',
        readonly=True,
        store=True
    )

    # === Action Type ===
    state = fields.Selection([
        ('code', 'Execute Python Code'),
        ('object_create', 'Create a new Record'),
        ('object_write', 'Update the Record'),
        ('multi', 'Execute several actions'),
        ('mail_post', 'Send Email'),
        ('sms', 'Send SMS Text Message'),
        ('webhook', 'Webhook'),
        ('next_activity', 'Create Next Activity'),
    ], string='Action Type', default='code', required=True,
        help='Type of server action to perform')

    # === Python Code ===
    code = fields.Text(
        string='Python Code',
        default='''# Available variables:
#  - env: Odoo Environment
#  - model: Model of the record on which the action is triggered
#  - records: Records on which the action is triggered (may be empty)
#  - record: First record (if exists)
# To assign result: action = {...}
''',
        help='Python code to execute when action type is "Execute Python Code"'
    )

    # === Automation Trigger Configuration ===
    is_automated = fields.Boolean(
        string='Automated Action',
        default=False,
        help='If True, create base.automation trigger'
    )

    trigger = fields.Selection([
        ('on_create', 'On Creation'),
        ('on_write', 'On Update'),
        ('on_create_or_write', 'On Creation & Update'),
        ('on_unlink', 'On Deletion'),
        ('on_time', 'Based on Date Field'),
        ('on_webhook', 'On Webhook'),
    ], string='Trigger', help='When to execute this action')

    filter_pre_domain = fields.Char(
        string='Before Update Domain',
        default='[]',
        help='Filter records before update (only for on_write)'
    )

    filter_domain = fields.Char(
        string='Apply on',
        default='[]',
        help='Filter which records trigger this action'
    )

    # For time-based triggers
    trg_date_id = fields.Many2one(
        'itx.moduler.model.field',
        string='Trigger Date Field',
        domain="[('model_id', '=', model_id), ('field_type', 'in', ('date', 'datetime'))]",
        help='Date field to base the trigger on (for on_time trigger)'
    )

    trg_date_range = fields.Integer(
        string='Delay After Date',
        default=0,
        help='Number of days/hours after trigger date'
    )

    trg_date_range_type = fields.Selection([
        ('minutes', 'Minutes'),
        ('hour', 'Hours'),
        ('day', 'Days'),
        ('month', 'Months'),
    ], string='Delay Type', default='day')

    # === Child Actions (for multi action) ===
    child_ids = fields.Many2many(
        'itx.moduler.server.action',
        'itx_moduler_server_action_rel',
        'parent_id',
        'child_id',
        string='Child Actions',
        help='Actions to execute (for multi action type)'
    )

    # === Create/Write Configuration ===
    crud_model_id = fields.Many2one(
        'itx.moduler.model',
        string='Target Model',
        help='Model to create/update (for object_create/object_write)'
    )

    fields_lines = fields.One2many(
        'itx.moduler.server.action.field',
        'action_id',
        string='Field Mappings',
        help='Fields to set on create/update'
    )

    # === Email Configuration ===
    template_id = fields.Many2one(
        'mail.template',
        string='Email Template',
        help='Email template to send (for mail_post)'
    )

    # === Activity Configuration ===
    activity_type_id = fields.Many2one(
        'mail.activity.type',
        string='Activity Type',
        help='Type of activity to create'
    )

    activity_summary = fields.Char(
        string='Activity Summary'
    )

    activity_note = fields.Html(
        string='Activity Note'
    )

    activity_user_field_name = fields.Char(
        string='User Field',
        help='Field name containing the user to assign activity to'
    )

    # === Webhook Configuration ===
    webhook_url = fields.Char(
        string='Webhook URL',
        help='URL to call for webhook action'
    )

    # === State & Tracking ===
    action_state = fields.Selection([
        ('draft', 'Draft'),
        ('validated', 'Validated'),
        ('applied', 'Applied'),
        ('exported', 'Exported'),
        ('archived', 'Archived')
    ], default='draft', required=True, index=True, string='Status')

    # Link to real ir.actions.server when applied
    ir_action_id = fields.Many2one(
        'ir.actions.server',
        string='Applied Action',
        readonly=True,
        help='Link to real ir.actions.server when applied'
    )

    # Link to base.automation if is_automated=True
    # TODO: Re-enable when base_automation is added to dependencies
    # automation_id = fields.Many2one(
    #     'base.automation',
    #     string='Applied Automation',
    #     readonly=True,
    #     help='Link to real base.automation when applied'
    # )

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
        help='Prompt used to generate this action (if from AI)'
    )

    # === Version Control ===
    version = fields.Integer(
        string='Version',
        default=1,
        readonly=True
    )

    parent_version_id = fields.Many2one(
        'itx.moduler.server.action',
        string='Parent Version',
        readonly=True,
        help='Previous version of this action'
    )

    # === Actions ===
    def action_validate(self):
        """Validate action before applying"""
        self.ensure_one()

        if self.action_state != 'draft':
            raise UserError(_('Only draft actions can be validated'))

        # Validate based on action type
        if self.state == 'code' and not self.code:
            raise ValidationError(_('Python code is required for code actions'))

        if self.state in ('object_create', 'object_write') and not self.crud_model_id:
            raise ValidationError(_('Target model is required for create/write actions'))

        self.action_state = 'validated'
        return True

    def action_apply_to_odoo(self):
        """Apply action to Odoo (create/update ir.actions.server)"""
        self.ensure_one()

        if self.action_state not in ('validated', 'applied'):
            raise UserError(_('Action must be validated before applying'))

        # Check if model is applied
        if not self.model_id.ir_model_id:
            raise UserError(
                _('Model "%s" must be applied first!') % self.model_id.name
            )

        # Create/update ir.actions.server
        vals = {
            'name': self.name,
            'model_id': self.model_id.ir_model_id.id,
            'state': self.state,
        }

        if self.code:
            vals['code'] = self.code

        if self.crud_model_id and self.crud_model_id.ir_model_id:
            vals['crud_model_id'] = self.crud_model_id.ir_model_id.id

        ir_action = self.ir_action_id or self.env['ir.actions.server'].create(vals)
        if self.ir_action_id:
            ir_action.write(vals)

        # TODO: Re-enable when base_automation is added to dependencies
        # Create base.automation if is_automated
        # automation = False
        # if self.is_automated and self.trigger:
        #     auto_vals = {
        #         'name': self.name,
        #         'model_id': self.model_id.ir_model_id.id,
        #         'trigger': self.trigger,
        #         'action_server_id': ir_action.id,
        #     }
        #
        #     if self.filter_domain and self.filter_domain != '[]':
        #         auto_vals['filter_domain'] = self.filter_domain
        #
        #     if self.trigger == 'on_time' and self.trg_date_id:
        #         if self.trg_date_id.ir_field_id:
        #             auto_vals['trg_date_id'] = self.trg_date_id.ir_field_id.id
        #             auto_vals['trg_date_range'] = self.trg_date_range
        #             auto_vals['trg_date_range_type'] = self.trg_date_range_type
        #
        #     automation = self.automation_id or self.env['base.automation'].create(auto_vals)
        #     if self.automation_id:
        #         automation.write(auto_vals)

        self.write({
            'action_state': 'applied',
            'ir_action_id': ir_action.id,
            # 'automation_id': automation.id if automation else False,
            'applied_date': fields.Datetime.now(),
        })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Applied'),
                'message': _('Server Action "%s" applied successfully') % self.name,
                'type': 'success',
            }
        }

    def _generate_action_xml(self):
        """Generate server action XML for export"""
        self.ensure_one()

        xml = '<?xml version="1.0"?>\n'
        xml += '<odoo>\n'

        # Generate server action record
        action_id = f"action_{self.name.lower().replace(' ', '_')}"
        xml += f'  <record id="{action_id}" model="ir.actions.server">\n'
        xml += f'    <field name="name">{self.name}</field>\n'
        xml += f'    <field name="model_id" ref="model_{self.model_id.model.replace(".", "_")}"/>\n'
        xml += f'    <field name="state">{self.state}</field>\n'

        if self.code:
            xml += '    <field name="code"><![CDATA[\n'
            xml += self.code
            xml += '\n    ]]></field>\n'

        xml += '  </record>\n'

        # Generate automation if is_automated
        if self.is_automated and self.trigger:
            auto_id = f"automation_{self.name.lower().replace(' ', '_')}"
            xml += f'\n  <record id="{auto_id}" model="base.automation">\n'
            xml += f'    <field name="name">{self.name}</field>\n'
            xml += f'    <field name="model_id" ref="model_{self.model_id.model.replace(".", "_")}"/>\n'
            xml += f'    <field name="trigger">{self.trigger}</field>\n'
            xml += f'    <field name="action_server_id" ref="{action_id}"/>\n'

            if self.filter_domain and self.filter_domain != '[]':
                xml += f'    <field name="filter_domain">{self.filter_domain}</field>\n'

            xml += '  </record>\n'

        xml += '</odoo>'

        return xml


class ItxModulerServerActionField(models.Model):
    _name = 'itx.moduler.server.action.field'
    _description = 'Server Action Field Mapping'
    _order = 'sequence, id'

    action_id = fields.Many2one(
        'itx.moduler.server.action',
        string='Action',
        required=True,
        ondelete='cascade'
    )

    sequence = fields.Integer(string='Sequence', default=10)

    field_id = fields.Many2one(
        'itx.moduler.model.field',
        string='Field',
        required=True,
        help='Field to set'
    )

    evaluation_type = fields.Selection([
        ('value', 'Value'),
        ('reference', 'Reference'),
        ('equation', 'Python Expression'),
    ], string='Evaluation Type', default='value', required=True)

    value = fields.Char(
        string='Value',
        help='Value to set (depends on evaluation type)'
    )
