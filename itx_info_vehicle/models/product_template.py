# -*- coding: utf-8 -*-

from odoo import api, fields, models


PART_ORIGIN_SELECTION = [
    ('oem', 'OEM (แท้)'),
    ('aftermarket', 'Aftermarket (เทียม)'),
    ('reconditioned', 'Reconditioned (รีบิ้วท์)'),
]

CONDITION_SELECTION = [
    ('new', 'New (มือหนึ่ง)'),
    ('like_new', 'Like New (มือสองสภาพใหม่)'),
    ('good', 'Good (ใช้งานได้ดี)'),
    ('fair', 'Fair (ต้องซ่อม/ปรับแต่ง)'),
]


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # === Vehicle Part Flag ===
    itx_is_vehicle_part = fields.Boolean(
        string='Vehicle Part',
        default=False,
        index=True,
        help='Enable Vehicle Part mode',
    )

    # === Vehicle Hierarchy Fields ===
    itx_brand_id = fields.Many2one(
        comodel_name='itx.info.vehicle.brand',
        string='Brand',
        index=True,
    )
    itx_model_id = fields.Many2one(
        comodel_name='itx.info.vehicle.model',
        string='Model',
        index=True,
        domain="[('brand_id', '=', itx_brand_id)]",
    )
    itx_generation_id = fields.Many2one(
        comodel_name='itx.info.vehicle.generation',
        string='Generation',
        index=True,
        domain="[('model_id', '=', itx_model_id)]",
    )
    itx_variant_id = fields.Many2one(
        comodel_name='itx.info.vehicle.variant',
        string='Variant',
        index=True,
        domain="[('generation_id', '=', itx_generation_id)]",
    )
    itx_part_category_id = fields.Many2one(
        comodel_name='itx.info.vehicle.part.category',
        string='Part Category',
        index=True,
    )

    # === Part Information ===
    itx_part_origin = fields.Selection(
        selection=PART_ORIGIN_SELECTION,
        string='Part Origin',
        index=True,
        help='Part origin: OEM (แท้), Aftermarket (เทียม), Reconditioned (รีบิ้วท์)',
    )
    itx_condition = fields.Selection(
        selection=CONDITION_SELECTION,
        string='Condition',
        index=True,
        help='Part condition: New, Like New, Good, Fair',
    )
    itx_oem_part_number = fields.Char(
        string='OEM Part Number',
        index=True,
        help='Original Equipment Manufacturer part number (optional, fill later)',
    )
    itx_sequence = fields.Char(
        string='Sequence',
        size=10,
        index=True,
        help='Running number for Internal Reference (auto-generated, editable)',
    )

    # === Constraints ===
    _sql_constraints = [
        ('vehicle_part_uniq',
         'UNIQUE(itx_variant_id, itx_part_category_id, name, itx_part_origin, itx_condition, itx_oem_part_number)',
         'Part with same vehicle, category, name, origin, condition and OEM part number already exists!'),
    ]

    # === Onchange Methods ===
    @api.onchange('itx_brand_id')
    def _onchange_itx_brand_id(self):
        """Clear dependent fields when brand changes"""
        self.itx_model_id = False
        self.itx_generation_id = False
        self.itx_variant_id = False

    @api.onchange('itx_model_id')
    def _onchange_itx_model_id(self):
        """Clear dependent fields when model changes"""
        self.itx_generation_id = False
        self.itx_variant_id = False

    @api.onchange('itx_generation_id')
    def _onchange_itx_generation_id(self):
        """Clear variant when generation changes"""
        self.itx_variant_id = False

    @api.onchange('itx_is_vehicle_part', 'itx_brand_id', 'itx_model_id',
                  'itx_generation_id', 'itx_variant_id', 'itx_part_category_id',
                  'itx_sequence')
    def _onchange_compute_default_code(self):
        """Auto-generate internal reference from vehicle hierarchy"""
        if self.itx_is_vehicle_part:
            self._compute_itx_default_code()

    # === Compute Internal Reference ===
    def _compute_itx_default_code(self):
        """Build default_code from abbreviations"""
        for rec in self:
            if rec.itx_is_vehicle_part:
                parts = []
                if rec.itx_brand_id and rec.itx_brand_id.abbr:
                    parts.append(rec.itx_brand_id.abbr)
                if rec.itx_model_id and rec.itx_model_id.abbr:
                    parts.append(rec.itx_model_id.abbr)
                if rec.itx_generation_id and rec.itx_generation_id.abbr:
                    parts.append(rec.itx_generation_id.abbr)
                if rec.itx_variant_id and rec.itx_variant_id.abbr:
                    parts.append(rec.itx_variant_id.abbr)
                if rec.itx_part_category_id and rec.itx_part_category_id.abbr:
                    parts.append(rec.itx_part_category_id.abbr)
                if rec.itx_sequence:
                    parts.append(rec.itx_sequence)

                if parts:
                    rec.default_code = '-'.join(parts)

    # === CRUD Methods ===
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # Auto-generate sequence for vehicle parts
            if vals.get('itx_is_vehicle_part') and not vals.get('itx_sequence'):
                vals['itx_sequence'] = self.env['ir.sequence'].next_by_code(
                    'itx.info.vehicle.part.sequence'
                ) or '00001'

        records = super().create(vals_list)

        # Compute default_code for vehicle parts
        for record in records:
            if record.itx_is_vehicle_part:
                record._compute_itx_default_code()

        return records

    def write(self, vals):
        result = super().write(vals)

        # Recompute default_code if vehicle part fields changed
        vehicle_fields = [
            'itx_is_vehicle_part', 'itx_brand_id', 'itx_model_id',
            'itx_generation_id', 'itx_variant_id', 'itx_part_category_id',
            'itx_sequence'
        ]
        if any(f in vals for f in vehicle_fields):
            for record in self:
                if record.itx_is_vehicle_part:
                    record._compute_itx_default_code()

        return result
