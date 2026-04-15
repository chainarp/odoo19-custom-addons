# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ItxInfoVehicleBrand(models.Model):
    _name = 'itx.info.vehicle.brand'
    _description = 'Vehicle Brand'
    _order = 'name'

    # === Standard Fields ===
    code = fields.Char(
        string='Code',
        required=True,
        index=True,
        help='Market code, e.g., HONDA, TOYOTA',
    )
    name = fields.Char(
        string='Name',
        required=True,
        index=True,
        help='Brand name, e.g., Honda, Toyota',
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
        help='Abbreviation for Internal Reference, e.g., HON, TOY',
    )

    # === Brand Specific Fields ===
    country_id = fields.Many2one(
        comodel_name='res.country',
        string='Country',
        help='Country of origin',
    )
    logo = fields.Image(
        string='Logo',
        max_width=256,
        max_height=256,
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    source_module = fields.Selection([
        ('revival', 'Revival'),
        ('procure', 'Procure'),
    ], string='Source Module', index=True)

    # === Relational Fields ===
    model_ids = fields.One2many(
        comodel_name='itx.info.vehicle.model',
        inverse_name='brand_id',
        string='Models',
    )
    model_count = fields.Integer(
        string='Model Count',
        compute='_compute_model_count',
    )

    # === Constraints ===
    _sql_constraints = [
        ('code_source_uniq', 'UNIQUE(code, source_module)',
         'Brand code must be unique per source module!'),
        ('abbr_source_uniq', 'UNIQUE(abbr, source_module)',
         'Brand abbreviation must be unique per source module!'),
    ]

    # === Compute Methods ===
    @api.depends('model_ids')
    def _compute_model_count(self):
        for rec in self:
            rec.model_count = len(rec.model_ids)

    # === Onchange Methods ===
    @api.onchange('name')
    def _onchange_name_set_abbr(self):
        """Auto-generate abbr from name (first 3 uppercase chars)"""
        if self.name and not self.abbr:
            # Remove non-alphanumeric and take first 3 chars
            clean = ''.join(c for c in self.name if c.isalnum())
            self.abbr = clean[:3].upper()

    @api.onchange('name')
    def _onchange_name_set_code(self):
        """Auto-generate code from name (uppercase)"""
        if self.name and not self.code:
            self.code = self.name.upper().replace(' ', '_')

    # === CRUD Methods ===
    def name_get(self):
        return [(rec.id, f"[{rec.abbr}] {rec.name}") for rec in self]
