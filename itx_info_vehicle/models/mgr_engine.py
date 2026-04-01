# -*- coding: utf-8 -*-

from odoo import api, fields, models


FUEL_TYPE_SELECTION = [
    ('gasoline', 'Gasoline (เบนซิน)'),
    ('diesel', 'Diesel (ดีเซล)'),
    ('hybrid', 'Hybrid'),
    ('phev', 'PHEV (Plug-in Hybrid)'),
    ('ev', 'EV (Electric)'),
    ('lpg', 'LPG'),
    ('cng', 'CNG'),
]


class ItxInfoVehicleMgrEngine(models.Model):
    _name = 'itx.info.vehicle.mgr.engine'
    _description = 'Vehicle Engine'
    _order = 'name'

    name = fields.Char(
        string='Name',
        required=True,
        index=True,
        help='Engine name, e.g., 2KD-FTV, 1ZZ-FE, K24A',
    )
    code = fields.Char(
        string='Code',
        required=True,
        index=True,
        help='Engine code (short), e.g., 2KD, 1ZZ, K24',
    )
    displacement = fields.Float(
        string='Displacement (L)',
        digits=(4, 1),
        help='Engine displacement in liters, e.g., 2.5, 1.8',
    )
    fuel_type = fields.Selection(
        selection=FUEL_TYPE_SELECTION,
        string='Fuel Type',
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )

    _sql_constraints = [
        ('code_uniq', 'UNIQUE(code)', 'Engine code must be unique!'),
    ]

    def name_get(self):
        result = []
        for rec in self:
            disp = f" {rec.displacement}L" if rec.displacement else ""
            result.append((rec.id, f"[{rec.code}] {rec.name}{disp}"))
        return result
