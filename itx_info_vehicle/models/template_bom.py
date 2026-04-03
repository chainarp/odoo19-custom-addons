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
        required=True,
        index=True,
        help='Part category group, e.g., Body, Suspension, Electrical',
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

    # === CRUD Methods ===
    def name_get(self):
        result = []
        for rec in self:
            name = f"{rec.body_type_id.name} - {rec.part_template_id.name}"
            result.append((rec.id, name))
        return result
