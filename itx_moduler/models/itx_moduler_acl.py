# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class ItxModulerAcl(models.Model):
    _name = 'itx.moduler.acl'
    _description = 'ITX Moduler Access Control List (Snapshot)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'model_id, name'

    # === Core Identification ===
    name = fields.Char(
        string='Name',
        required=True,
        help='ACL display name (e.g., "Sales Manager Access")'
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
        help='Model this ACL applies to'
    )

    model_name = fields.Char(
        string='Model Name',
        related='model_id.model',
        readonly=True,
        store=True
    )

    # === Group Access ===
    group_id = fields.Many2one(
        'itx.moduler.group',
        string='Group',
        ondelete='cascade',
        help='Group this ACL applies to (empty = public access)'
    )

    group_name = fields.Char(
        string='Group Name',
        related='group_id.name',
        readonly=True
    )

    # For groups not in this module (e.g., base.group_user)
    external_group_id = fields.Many2one(
        'res.groups',
        string='External Group',
        help='Reference to existing Odoo group (e.g., base.group_user)'
    )

    # === Permissions ===
    perm_read = fields.Boolean(
        string='Read Access',
        default=True,
        help='Allow reading records'
    )

    perm_write = fields.Boolean(
        string='Write Access',
        default=False,
        help='Allow updating records'
    )

    perm_create = fields.Boolean(
        string='Create Access',
        default=False,
        help='Allow creating new records'
    )

    perm_unlink = fields.Boolean(
        string='Delete Access',
        default=False,
        help='Allow deleting records'
    )

    # === State & Tracking ===
    state = fields.Selection([
        ('draft', 'Draft'),
        ('validated', 'Validated'),
        ('applied', 'Applied'),
        ('exported', 'Exported'),
        ('archived', 'Archived')
    ], default='draft', required=True, index=True)

    # Link to real ir.model.access when applied
    ir_access_id = fields.Many2one(
        'ir.model.access',
        string='Applied ACL',
        readonly=True,
        help='Link to real ir.model.access when state=applied'
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
        help='Prompt used to generate this ACL (if from AI)'
    )

    # === Version Control ===
    version = fields.Integer(
        string='Version',
        default=1,
        readonly=True
    )

    parent_version_id = fields.Many2one(
        'itx.moduler.acl',
        string='Parent Version',
        readonly=True,
        help='Previous version of this ACL'
    )

    # === Display ===
    @api.depends('name', 'model_name', 'group_name')
    def _compute_display_name(self):
        for acl in self:
            parts = []
            if acl.model_name:
                parts.append(acl.model_name)
            if acl.group_name:
                parts.append(acl.group_name)
            elif acl.external_group_id:
                parts.append(acl.external_group_id.name)
            else:
                parts.append('Public')

            acl.display_name = ' - '.join(parts) if parts else acl.name

    # === Validations ===
    @api.constrains('group_id', 'external_group_id')
    def _check_group(self):
        """Either group_id or external_group_id should be set, not both"""
        for acl in self:
            if acl.group_id and acl.external_group_id:
                raise ValidationError(
                    _('Cannot set both internal group and external group!')
                )

    # === Actions ===
    def action_validate(self):
        """Validate ACL before applying"""
        self.ensure_one()

        if self.state != 'draft':
            raise UserError(_('Only draft ACLs can be validated'))

        # Validate that model exists
        if not self.model_id:
            raise ValidationError(_('Model is required!'))

        self.state = 'validated'
        return True

    def action_apply_to_odoo(self):
        """Apply ACL to Odoo (create/update ir.model.access)"""
        self.ensure_one()

        if self.state not in ('validated', 'applied'):
            raise UserError(_('ACL must be validated before applying'))

        # Check if model is applied
        if not self.model_id.ir_model_id:
            raise UserError(
                _('Model "%s" must be applied first!') % self.model_id.name
            )

        # Determine group
        group_id = False
        if self.group_id and self.group_id.ir_group_id:
            group_id = self.group_id.ir_group_id.id
        elif self.external_group_id:
            group_id = self.external_group_id.id

        # Find or create ir.model.access
        domain = [
            ('model_id', '=', self.model_id.ir_model_id.id),
        ]
        if group_id:
            domain.append(('group_id', '=', group_id))
        else:
            domain.append(('group_id', '=', False))

        ir_access = self.env['ir.model.access'].search(domain, limit=1)

        vals = {
            'name': self.name,
            'model_id': self.model_id.ir_model_id.id,
            'group_id': group_id,
            'perm_read': self.perm_read,
            'perm_write': self.perm_write,
            'perm_create': self.perm_create,
            'perm_unlink': self.perm_unlink,
        }

        if ir_access:
            ir_access.write(vals)
        else:
            ir_access = self.env['ir.model.access'].create(vals)

        self.write({
            'state': 'applied',
            'ir_access_id': ir_access.id,
            'applied_date': fields.Datetime.now(),
        })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Applied'),
                'message': _('ACL "%s" applied successfully') % self.name,
                'type': 'success',
            }
        }

    def _generate_acl_csv(self):
        """Generate ACL CSV line for export"""
        self.ensure_one()

        # Generate CSV-safe ID
        csv_id = f"access_{self.model_id.model.replace('.', '_')}"
        if self.group_id:
            csv_id += f"_{self.group_id.name.lower().replace(' ', '_')}"
        elif self.external_group_id:
            csv_id += f"_{self.external_group_id.name.lower().replace(' ', '_')}"
        else:
            csv_id += "_public"

        # Generate model reference
        model_ref = f"model_{self.model_id.model.replace('.', '_')}"

        # Generate group reference
        group_ref = ""
        if self.group_id:
            group_ref = f"group_{self.group_id.name.lower().replace(' ', '_')}"
        elif self.external_group_id:
            # External group - need to find XML ID
            ext_xmlid = self.env['ir.model.data'].search([
                ('model', '=', 'res.groups'),
                ('res_id', '=', self.external_group_id.id)
            ], limit=1)
            if ext_xmlid:
                group_ref = f"{ext_xmlid.module}.{ext_xmlid.name}"

        # Build CSV line
        csv_line = f"{csv_id},{self.name},{model_ref},{group_ref},"
        csv_line += f"{'1' if self.perm_read else '0'},"
        csv_line += f"{'1' if self.perm_write else '0'},"
        csv_line += f"{'1' if self.perm_create else '0'},"
        csv_line += f"{'1' if self.perm_unlink else '0'}"

        return csv_line
