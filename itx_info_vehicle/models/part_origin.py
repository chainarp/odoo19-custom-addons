# -*- coding: utf-8 -*-

from odoo import fields, models


class ItxInfoVehiclePartOrigin(models.Model):
    _name = 'itx.info.vehicle.part.origin'
    _description = 'Part Origin'
    _order = 'sequence, name'

    code = fields.Char(
        string='Code',
        required=True,
        index=True,
        help='Unique code, e.g., OEM, AFT, REC',
    )
    name = fields.Char(
        string='Name',
        required=True,
        index=True,
        help='Origin name, e.g., OEM (แท้), Aftermarket (เทียม)',
    )
    abbr = fields.Char(
        string='Abbreviation',
        size=10,
        required=True,
        index=True,
        help='Abbreviation for Internal Reference',
    )
    desc = fields.Text(
        string='Description',
        help='Additional description',
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )

    _sql_constraints = [
        ('code_uniq', 'UNIQUE(code)', 'Part origin code must be unique!'),
        ('abbr_uniq', 'UNIQUE(abbr)', 'Part origin abbreviation must be unique!'),
    ]

    def name_get(self):
        result = []
        for rec in self:
            name = f"[{rec.abbr}] {rec.name}"
            result.append((rec.id, name))
        return result
