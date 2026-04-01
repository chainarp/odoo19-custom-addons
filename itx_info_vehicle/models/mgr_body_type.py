# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ItxInfoVehicleMgrBodyType(models.Model):
    _name = 'itx.info.vehicle.mgr.body.type'
    _description = 'Vehicle Body Type'
    _order = 'sequence, name'

    name = fields.Char(
        string='Name',
        required=True,
        index=True,
        help='Body type name, e.g., Double Cab, Sedan',
    )
    code = fields.Char(
        string='Code',
        required=True,
        index=True,
        help='Body type code, e.g., double_cab, sedan',
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
        ('code_uniq', 'UNIQUE(code)', 'Body type code must be unique!'),
    ]

    def name_get(self):
        return [(rec.id, f"[{rec.code}] {rec.name}") for rec in self]
