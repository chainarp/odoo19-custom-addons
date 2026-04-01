# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ItxInfoVehicleGeneration(models.Model):
    _name = 'itx.info.vehicle.generation'
    _description = 'Vehicle Generation'
    _order = 'model_id, year_start desc'

    # === Standard Fields ===
    code = fields.Char(
        string='Code',
        required=True,
        index=True,
        help='Market code, e.g., FD-PRE, FD-POST, FB',
    )
    name = fields.Char(
        string='Name',
        required=True,
        index=True,
        help='Generation name, e.g., Gen 8 (FD) Pre-MC',
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
        help='Abbreviation for Internal Reference, e.g., FD1, FD2, FB',
    )

    # === Generation Specific Fields ===
    model_id = fields.Many2one(
        comodel_name='itx.info.vehicle.model',
        string='Model',
        required=True,
        index=True,
        ondelete='restrict',
    )
    chassis_code = fields.Char(
        string='Chassis Code',
        index=True,
        help='Chassis code, e.g., FD1/FD2, FB7',
    )
    year_start = fields.Integer(
        string='Year Start',
        help='Production start year',
    )
    year_end = fields.Integer(
        string='Year End',
        default=0,
        help='Production end year (0 = still in production)',
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )

    # === Relational Fields ===
    variant_ids = fields.One2many(
        comodel_name='itx.info.vehicle.variant',
        inverse_name='generation_id',
        string='Variants',
    )
    variant_count = fields.Integer(
        string='Variant Count',
        compute='_compute_variant_count',
    )

    # === Related Fields ===
    brand_id = fields.Many2one(
        comodel_name='itx.info.vehicle.brand',
        string='Brand',
        related='model_id.brand_id',
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
    year_range = fields.Char(
        string='Year Range',
        compute='_compute_year_range',
        store=True,
    )

    # === Constraints ===
    _sql_constraints = [
        ('code_model_uniq', 'UNIQUE(code, model_id)',
         'Generation code must be unique per model!'),
    ]

    @api.constrains('year_start', 'year_end')
    def _check_year_range(self):
        for rec in self:
            if rec.year_start and rec.year_end and rec.year_end != 0:
                if rec.year_end < rec.year_start:
                    raise ValidationError(
                        'Year end must be greater than or equal to year start!'
                    )

    # === Compute Methods ===
    @api.depends('model_id', 'model_id.full_name', 'name')
    def _compute_full_name(self):
        for rec in self:
            if rec.model_id and rec.model_id.full_name and rec.name:
                rec.full_name = f"{rec.model_id.full_name} {rec.name}"
            else:
                rec.full_name = rec.name or ''

    @api.depends('year_start', 'year_end')
    def _compute_year_range(self):
        for rec in self:
            if rec.year_start:
                if rec.year_end and rec.year_end != 0:
                    rec.year_range = f"{rec.year_start}-{rec.year_end}"
                else:
                    rec.year_range = f"{rec.year_start}-present"
            else:
                rec.year_range = ''

    @api.depends('variant_ids')
    def _compute_variant_count(self):
        for rec in self:
            rec.variant_count = len(rec.variant_ids)

    # === Onchange Methods ===
    @api.onchange('name')
    def _onchange_name_set_abbr(self):
        """Auto-generate abbr from name (extract from parentheses or first chars)"""
        if self.name and not self.abbr:
            import re
            # Try to extract from parentheses: "Gen 8 (FD)" -> "FD"
            match = re.search(r'\(([^)]+)\)', self.name)
            if match:
                self.abbr = match.group(1).upper()[:10]
            else:
                # Take first 3 chars
                clean = ''.join(c for c in self.name if c.isalnum())
                self.abbr = clean[:3].upper()

    @api.onchange('name', 'chassis_code')
    def _onchange_set_code(self):
        """Auto-generate code from chassis_code or name"""
        if not self.code:
            if self.chassis_code:
                self.code = self.chassis_code.upper().replace('/', '-')
            elif self.name:
                clean = ''.join(c for c in self.name if c.isalnum() or c == ' ')
                self.code = clean.upper().replace(' ', '-')

    # === CRUD Methods ===
    def name_get(self):
        result = []
        for rec in self:
            year_info = f" ({rec.year_range})" if rec.year_range else ""
            name = f"[{rec.abbr}] {rec.name}{year_info}"
            result.append((rec.id, name))
        return result
