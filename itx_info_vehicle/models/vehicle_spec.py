# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError


FUEL_TYPE_SELECTION = [
    ('gasoline', 'Gasoline'),
    ('diesel', 'Diesel'),
    ('hybrid', 'Hybrid'),
    ('phev', 'Plug-in Hybrid'),
    ('ev', 'Electric (EV)'),
    ('lpg', 'LPG'),
    ('cng', 'CNG'),
    ('other', 'Other'),
]

TRANSMISSION_SELECTION = [
    ('manual', 'Manual (MT)'),
    ('auto', 'Automatic (AT)'),
    ('cvt', 'CVT'),
    ('dct', 'Dual Clutch (DCT)'),
    ('amt', 'Automated Manual (AMT)'),
    ('other', 'Other'),
]

DRIVE_TYPE_SELECTION = [
    ('ff', 'FF (Front-wheel Drive)'),
    ('fr', 'FR (Rear-wheel Drive)'),
    ('awd', 'AWD (All-wheel Drive)'),
    ('4wd', '4WD (Four-wheel Drive)'),
    ('rr', 'RR (Rear Engine, Rear Drive)'),
    ('mr', 'MR (Mid Engine, Rear Drive)'),
]


class ItxInfoVehicleSpec(models.Model):
    _name = 'itx.info.vehicle.spec'
    _description = 'Vehicle Spec'
    _order = 'generation_id, name'

    # === Standard Fields ===
    code = fields.Char(
        string='Code',
        required=True,
        index=True,
        help='Spec code, e.g., 1.8S-IVTEC, 2.0EL',
    )
    name = fields.Char(
        string='Name',
        required=True,
        index=True,
        help='Spec name, e.g., 1.8 S i-VTEC, 2.0 EL',
    )
    desc = fields.Text(
        string='Description',
        help='Additional description',
    )
    abbr = fields.Char(
        string='Abbreviation',
        size=10,
        required=True,
        index=True,
        help='Abbreviation for Internal Reference, e.g., 1.8S, 2.0L',
    )

    # === Spec Specific Fields ===
    generation_id = fields.Many2one(
        comodel_name='itx.info.vehicle.generation',
        string='Generation',
        required=True,
        index=True,
        ondelete='restrict',
    )
    body_type_id = fields.Many2one(
        comodel_name='itx.info.vehicle.mgr.body.type',
        string='Body Type',
        index=True,
        help='Body type, e.g., Sedan, Double Cab',
    )
    engine_id = fields.Many2one(
        comodel_name='itx.info.vehicle.mgr.engine',
        string='Engine',
        index=True,
        help='Engine code, e.g., 2KD-FTV, R18A',
    )
    # Legacy fields (for backward compatibility)
    engine_code = fields.Char(
        string='Engine Code (Legacy)',
        index=True,
        help='Engine code, e.g., R18A, K20A, L15B',
    )
    engine_displacement = fields.Float(
        string='Engine Displacement (L)',
        digits=(4, 1),
        help='Engine displacement in liters, e.g., 1.8, 2.0',
    )
    fuel_type = fields.Selection(
        selection=FUEL_TYPE_SELECTION,
        string='Fuel Type',
    )
    transmission = fields.Selection(
        selection=TRANSMISSION_SELECTION,
        string='Transmission',
    )
    drive_type = fields.Selection(
        selection=DRIVE_TYPE_SELECTION,
        string='Drive Type',
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    source_module = fields.Selection([
        ('revival', 'Revival'),
        ('procure', 'Procure'),
    ], string='Source Module', index=True)

    # === Related Fields ===
    brand_id = fields.Many2one(
        comodel_name='itx.info.vehicle.brand',
        string='Brand',
        related='generation_id.model_id.brand_id',
        store=True,
        index=True,
    )
    model_id = fields.Many2one(
        comodel_name='itx.info.vehicle.model',
        string='Model',
        related='generation_id.model_id',
        store=True,
        index=True,
    )

    # === Computed Fields ===
    full_name = fields.Char(
        string='Full Name',
        compute='_compute_full_name',
        store=True,
        index=True,
    )

    # === Constraints ===
    _sql_constraints = [
        ('code_gen_uniq', 'UNIQUE(code, generation_id)',
         'Spec code must be unique per generation!'),
    ]

    @api.constrains('engine_displacement')
    def _check_engine_displacement(self):
        for rec in self:
            if rec.engine_displacement and rec.engine_displacement <= 0:
                raise ValidationError(
                    'Engine displacement must be greater than 0!'
                )

    # === Compute Methods ===
    @api.depends('generation_id', 'generation_id.full_name', 'name')
    def _compute_full_name(self):
        for rec in self:
            if rec.generation_id and rec.generation_id.full_name and rec.name:
                rec.full_name = f"{rec.generation_id.full_name} {rec.name}"
            else:
                rec.full_name = rec.name or ''

    # === Onchange Methods ===
    @api.onchange('name', 'engine_displacement')
    def _onchange_set_abbr(self):
        """Auto-generate abbr from engine displacement or name"""
        if not self.abbr:
            if self.engine_displacement:
                # e.g., 1.8 -> "1.8"
                disp = str(self.engine_displacement)
                # Extract first part of name after displacement
                if self.name:
                    parts = self.name.split()
                    for part in parts:
                        if part[0].isalpha():
                            self.abbr = f"{disp}{part[0]}".upper()
                            return
                self.abbr = disp
            elif self.name:
                clean = ''.join(c for c in self.name if c.isalnum())
                self.abbr = clean[:4].upper()

    @api.onchange('name')
    def _onchange_name_set_code(self):
        """Auto-generate code from name"""
        if self.name and not self.code:
            self.code = self.name.upper().replace(' ', '-').replace('.', '')

    # === CRUD Methods ===
    def name_get(self):
        result = []
        for rec in self:
            engine_info = f" [{rec.engine_code}]" if rec.engine_code else ""
            name = f"[{rec.abbr}] {rec.name}{engine_info}"
            result.append((rec.id, name))
        return result
