# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class ItxModulerReport(models.Model):
    _name = 'itx.moduler.report'
    _description = 'ITX Moduler Report (Snapshot)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'model_id, name'

    # === Core Identification ===
    name = fields.Char(
        string='Report Name',
        required=True,
        help='Display name (e.g., "Invoice Report")'
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
        help='Model this report is for'
    )

    model_name = fields.Char(
        string='Model Name',
        related='model_id.model',
        readonly=True,
        store=True
    )

    # === Report Configuration ===
    report_type = fields.Selection([
        ('qweb-pdf', 'PDF'),
        ('qweb-html', 'HTML'),
        ('qweb-text', 'Text'),
    ], string='Report Type', default='qweb-pdf', required=True,
        help='Output format of the report')

    report_name = fields.Char(
        string='Template Name',
        required=True,
        help='Technical name of report template (e.g., "module.report_invoice")'
    )

    report_file = fields.Char(
        string='Report File',
        help='Report file name (usually same as report_name)'
    )

    # === Print Button ===
    print_report_name = fields.Char(
        string='Printed File Name',
        help='Expression for filename (e.g., "Invoice - %(object.number)s")'
    )

    # === Binding ===
    binding_model_id = fields.Many2one(
        'itx.moduler.model',
        string='Binding Model',
        help='Add print button to this model (if different from target model)'
    )

    binding_type = fields.Selection([
        ('report', 'Report'),
        ('action', 'Action'),
    ], string='Binding Type', default='report')

    # === Paper Format ===
    paperformat_id = fields.Many2one(
        'report.paperformat',
        string='Paper Format',
        help='Paper format for PDF reports'
    )

    # === Report Template (QWeb) ===
    arch = fields.Text(
        string='QWeb Template (XML)',
        help='QWeb template code for report'
    )

    # Template structure helper
    template_id_name = fields.Char(
        string='Template ID',
        help='XML ID for report template (e.g., "report_invoice_document")'
    )

    # === Multi-language ===
    multi = fields.Boolean(
        string='Multi Report',
        default=False,
        help='If True, one PDF per record; if False, all records in one PDF'
    )

    # === State & Tracking ===
    state = fields.Selection([
        ('draft', 'Draft'),
        ('validated', 'Validated'),
        ('applied', 'Applied'),
        ('exported', 'Exported'),
        ('archived', 'Archived')
    ], default='draft', required=True, index=True)

    # Link to real ir.actions.report when applied
    ir_report_id = fields.Many2one(
        'ir.actions.report',
        string='Applied Report',
        readonly=True,
        help='Link to real ir.actions.report when applied'
    )

    # Link to QWeb template view
    template_view_id = fields.Many2one(
        'ir.ui.view',
        string='Template View',
        readonly=True,
        help='Link to QWeb template view when applied'
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
        help='Prompt used to generate this report (if from AI)'
    )

    # === Version Control ===
    version = fields.Integer(
        string='Version',
        default=1,
        readonly=True
    )

    parent_version_id = fields.Many2one(
        'itx.moduler.report',
        string='Parent Version',
        readonly=True,
        help='Previous version of this report'
    )

    # === Computed ===
    @api.onchange('report_name')
    def _onchange_report_name(self):
        """Auto-fill report_file and template_id_name"""
        if self.report_name and not self.report_file:
            self.report_file = self.report_name

        if self.report_name and not self.template_id_name:
            # Extract template name from full name (e.g., "module.report_xxx" -> "report_xxx")
            parts = self.report_name.split('.')
            if len(parts) > 1:
                self.template_id_name = parts[-1]

    # === Actions ===
    def action_validate(self):
        """Validate report before applying"""
        self.ensure_one()

        if self.state != 'draft':
            raise UserError(_('Only draft reports can be validated'))

        if not self.report_name:
            raise ValidationError(_('Template name is required'))

        if self.arch:
            # Validate QWeb template
            try:
                from lxml import etree
                etree.fromstring(self.arch)
            except Exception as e:
                raise ValidationError(
                    f'Invalid QWeb template XML: {str(e)}'
                )

        self.state = 'validated'
        return True

    def action_apply_to_odoo(self):
        """Apply report to Odoo (create/update ir.actions.report)"""
        self.ensure_one()

        if self.state not in ('validated', 'applied'):
            raise UserError(_('Report must be validated before applying'))

        # Check if model is applied
        if not self.model_id.ir_model_id:
            raise UserError(
                _('Model "%s" must be applied first!') % self.model_id.name
            )

        # Create QWeb template if arch provided
        template_view = False
        if self.arch:
            template_name = self.template_id_name or self.report_name.split('.')[-1]
            template_view = self.env['ir.ui.view'].search([
                ('name', '=', template_name)
            ], limit=1)

            template_vals = {
                'name': template_name,
                'type': 'qweb',
                'arch': self.arch,
            }

            if template_view:
                template_view.write(template_vals)
            else:
                template_view = self.env['ir.ui.view'].create(template_vals)

        # Create/update ir.actions.report
        ir_report = self.env['ir.actions.report'].search([
            ('name', '=', self.name),
            ('model', '=', self.model_id.model),
        ], limit=1)

        vals = {
            'name': self.name,
            'model': self.model_id.model,
            'report_type': self.report_type,
            'report_name': self.report_name,
        }

        if self.report_file:
            vals['report_file'] = self.report_file

        if self.print_report_name:
            vals['print_report_name'] = self.print_report_name

        if self.binding_model_id and self.binding_model_id.ir_model_id:
            vals['binding_model_id'] = self.binding_model_id.ir_model_id.id
            vals['binding_type'] = self.binding_type
        elif not self.binding_model_id:
            # Bind to same model by default
            vals['binding_model_id'] = self.model_id.ir_model_id.id
            vals['binding_type'] = self.binding_type

        if self.paperformat_id:
            vals['paperformat_id'] = self.paperformat_id.id

        vals['multi'] = self.multi

        if ir_report:
            ir_report.write(vals)
        else:
            ir_report = self.env['ir.actions.report'].create(vals)

        self.write({
            'state': 'applied',
            'ir_report_id': ir_report.id,
            'template_view_id': template_view.id if template_view else False,
            'applied_date': fields.Datetime.now(),
        })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Applied'),
                'message': _('Report "%s" applied successfully') % self.name,
                'type': 'success',
            }
        }

    def _generate_report_xml(self):
        """Generate report XML for export"""
        self.ensure_one()

        xml = '<?xml version="1.0"?>\n'
        xml += '<odoo>\n'

        # Generate report action
        report_id = f"action_report_{self.name.lower().replace(' ', '_')}"
        xml += f'  <record id="{report_id}" model="ir.actions.report">\n'
        xml += f'    <field name="name">{self.name}</field>\n'
        xml += f'    <field name="model">{self.model_id.model}</field>\n'
        xml += f'    <field name="report_type">{self.report_type}</field>\n'
        xml += f'    <field name="report_name">{self.report_name}</field>\n'

        if self.report_file:
            xml += f'    <field name="report_file">{self.report_file}</field>\n'

        if self.print_report_name:
            xml += f'    <field name="print_report_name">{self.print_report_name}</field>\n'

        if self.binding_model_id:
            xml += f'    <field name="binding_model_id" ref="model_{self.binding_model_id.model.replace(".", "_")}"/>\n'
        else:
            xml += f'    <field name="binding_model_id" ref="model_{self.model_id.model.replace(".", "_")}"/>\n'

        xml += f'    <field name="binding_type">{self.binding_type}</field>\n'

        if self.paperformat_id:
            paperformat_xmlid = self.env['ir.model.data'].search([
                ('model', '=', 'report.paperformat'),
                ('res_id', '=', self.paperformat_id.id)
            ], limit=1)
            if paperformat_xmlid:
                xml += f'    <field name="paperformat_id" ref="{paperformat_xmlid.module}.{paperformat_xmlid.name}"/>\n'

        if self.multi:
            xml += '    <field name="multi" eval="True"/>\n'

        xml += '  </record>\n'

        # Generate QWeb template if provided
        if self.arch:
            template_name = self.template_id_name or self.report_name.split('.')[-1]
            xml += f'\n  <template id="{template_name}">\n'
            # Remove XML declaration if exists in arch
            arch_clean = self.arch
            if arch_clean.startswith('<?xml'):
                arch_clean = '\n'.join(arch_clean.split('\n')[1:])
            xml += arch_clean
            xml += '\n  </template>\n'

        xml += '</odoo>'

        return xml
