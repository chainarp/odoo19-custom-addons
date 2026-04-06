# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ItxInfoVehicleTemplateBom(models.Model):
    _name = 'itx.info.vehicle.template.bom'
    _description = 'Vehicle BOM Template'
    _order = 'body_type_id, sequence, part_category_id'

    # === Main Fields ===
    body_type_id = fields.Many2one(
        comodel_name='itx.info.vehicle.mgr.body.type',
        string='Body Type',
        required=True,
        index=True,
        ondelete='cascade',
        help='Vehicle body type, e.g., Sedan, SUV, Double Cab',
    )
    part_category_id = fields.Many2one(
        comodel_name='itx.info.vehicle.part.category',
        string='Part Category',
        related='part_template_id.category_id',
        store=True,
        index=True,
        help='Part category group (from Part Template)',
    )
    part_template_id = fields.Many2one(
        comodel_name='itx.info.vehicle.template.part',
        string='Part Template',
        required=True,
        index=True,
        ondelete='cascade',
        help='Part template, e.g., Front Bumper, Left Headlight',
    )
    qty = fields.Integer(
        string='Quantity',
        default=1,
        help='Expected quantity of this part',
    )

    # === Default Origin & Condition ===
    default_part_origin_id = fields.Many2one(
        comodel_name='itx.info.vehicle.part.origin',
        string='Default Origin',
        index=True,
        help='Default part origin for assessment (e.g., OEM)',
    )
    default_part_condition_id = fields.Many2one(
        comodel_name='itx.info.vehicle.part.condition',
        string='Default Condition',
        index=True,
        help='Default part condition for assessment (e.g., Good)',
    )

    # === Cost Weight ===
    cost_weight = fields.Float(
        string='Cost Weight (%)',
        digits=(5, 2),
        default=0,
        help='% สัดส่วนต้นทุนของ part นี้ (รวมต่อ body_type ต้องได้ 100%)',
    )
    total_weight = fields.Float(
        string='Total Weight',
        compute='_compute_total_weight',
        digits=(5, 2),
        help='รวม cost_weight ทั้งหมดของ body_type นี้',
    )
    weight_status = fields.Char(
        string='Status',
        compute='_compute_total_weight',
        help='สถานะ: ขาด/เกิน/พอดี 100%',
    )

    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Display order in BOM',
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )

    # === Related Fields ===
    part_name = fields.Char(
        related='part_template_id.name',
        string='Part Name',
        store=True,
    )
    part_abbr = fields.Char(
        related='part_template_id.abbr',
        string='Part Abbr',
        store=True,
    )

    # === Constraints ===
    _sql_constraints = [
        ('unique_bom_line',
         'UNIQUE(body_type_id, part_template_id)',
         'Part already exists in this BOM template!'),
    ]

    # === Compute Methods ===
    @api.depends('cost_weight', 'body_type_id')
    def _compute_total_weight(self):
        for rec in self:
            if rec.body_type_id:
                # Sum all cost_weight for same body_type
                same_body_type = self.search([
                    ('body_type_id', '=', rec.body_type_id.id),
                    ('active', '=', True),
                ])
                total = sum(same_body_type.mapped('cost_weight'))
                rec.total_weight = total

                # Calculate status
                diff = total - 100
                if abs(diff) < 0.01:  # Close enough to 100%
                    rec.weight_status = '✓ 100%'
                elif diff < 0:
                    rec.weight_status = f'{diff:.2f}%'  # Shows as -2.00%
                else:
                    rec.weight_status = f'+{diff:.2f}%'  # Shows as +2.00%
            else:
                rec.total_weight = 0
                rec.weight_status = ''

    # === CRUD Methods ===
    def name_get(self):
        result = []
        for rec in self:
            name = f"{rec.body_type_id.name} - {rec.part_template_id.name}"
            result.append((rec.id, name))
        return result
