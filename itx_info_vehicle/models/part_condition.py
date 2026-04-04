# -*- coding: utf-8 -*-

from odoo import fields, models


class ItxInfoVehiclePartCondition(models.Model):
    _name = 'itx.info.vehicle.part.condition'
    _description = 'Part Condition'
    _order = 'sequence, name'

    code = fields.Char(
        string='Code',
        required=True,
        index=True,
        help='Unique code, e.g., NEW, LIKE_NEW, GOOD, FAIR',
    )
    name = fields.Char(
        string='Name',
        required=True,
        index=True,
        help='Condition name, e.g., New (มือหนึ่ง), Like New (มือสองสภาพใหม่)',
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
        ('code_uniq', 'UNIQUE(code)', 'Part condition code must be unique!'),
        ('abbr_uniq', 'UNIQUE(abbr)', 'Part condition abbreviation must be unique!'),
    ]

    def name_get(self):
        result = []
        for rec in self:
            name = f"[{rec.abbr}] {rec.name}"
            result.append((rec.id, name))
        return result
