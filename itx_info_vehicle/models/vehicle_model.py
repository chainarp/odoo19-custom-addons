# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ItxInfoVehicleModel(models.Model):
    _name = 'itx.info.vehicle.model'
    _description = 'Vehicle Model'
    _order = 'brand_id, name'

    # === Standard Fields ===
    code = fields.Char(
        string='Code',
        required=True,
        index=True,
        help='Market code, e.g., CIVIC, ACCORD',
    )
    name = fields.Char(
        string='Name',
        required=True,
        index=True,
        help='Model name, e.g., Civic, Accord',
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
        help='Abbreviation for Internal Reference, e.g., CIV, ACD',
    )

    # === Model Specific Fields ===
    brand_id = fields.Many2one(
        comodel_name='itx.info.vehicle.brand',
        string='Brand',
        required=True,
        index=True,
        ondelete='restrict',
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )

    # === Relational Fields ===
    generation_ids = fields.One2many(
        comodel_name='itx.info.vehicle.generation',
        inverse_name='model_id',
        string='Generations',
    )
    generation_count = fields.Integer(
        string='Generation Count',
        compute='_compute_generation_count',
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
        ('code_brand_uniq', 'UNIQUE(code, brand_id)',
         'Model code must be unique per brand!'),
        ('abbr_brand_uniq', 'UNIQUE(abbr, brand_id)',
         'Model abbreviation must be unique per brand!'),
    ]

    # === Compute Methods ===
    @api.depends('brand_id', 'brand_id.name', 'name')
    def _compute_full_name(self):
        for rec in self:
            if rec.brand_id and rec.name:
                rec.full_name = f"{rec.brand_id.name} {rec.name}"
            else:
                rec.full_name = rec.name or ''

    @api.depends('generation_ids')
    def _compute_generation_count(self):
        for rec in self:
            rec.generation_count = len(rec.generation_ids)

    # === Onchange Methods ===
    @api.onchange('name')
    def _onchange_name_set_abbr(self):
        """Auto-generate abbr from name (first 3 uppercase chars)"""
        if self.name and not self.abbr:
            clean = ''.join(c for c in self.name if c.isalnum())
            self.abbr = clean[:3].upper()

    @api.onchange('name')
    def _onchange_name_set_code(self):
        """Auto-generate code from name (uppercase)"""
        if self.name and not self.code:
            self.code = self.name.upper().replace(' ', '_').replace('-', '')

    # === CRUD Methods ===
    def name_get(self):
        return [(rec.id, f"[{rec.abbr}] {rec.full_name or rec.name}") for rec in self]
