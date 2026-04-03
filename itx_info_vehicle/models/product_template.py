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

    # === Main Vehicle Spec Field ===
    itx_spec_id = fields.Many2one(
        comodel_name='itx.info.vehicle.spec',
        string='Vehicle Spec',
        index=True,
        help='Primary vehicle spec this part is for',
    )

    # === Related Fields (Read-only, from Spec) ===
    itx_brand_id = fields.Many2one(
        comodel_name='itx.info.vehicle.brand',
        string='Brand',
        related='itx_spec_id.brand_id',
        store=True,
        readonly=True,
    )
    itx_model_id = fields.Many2one(
        comodel_name='itx.info.vehicle.model',
        string='Model',
        related='itx_spec_id.model_id',
        store=True,
        readonly=True,
    )
    itx_generation_id = fields.Many2one(
        comodel_name='itx.info.vehicle.generation',
        string='Generation',
        related='itx_spec_id.generation_id',
        store=True,
        readonly=True,
    )

    # === Compatible Specs (Many2many) ===
    itx_compatible_spec_ids = fields.Many2many(
        comodel_name='itx.info.vehicle.spec',
        relation='product_template_compatible_spec_rel',
        column1='product_id',
        column2='spec_id',
        string='Compatible Specs',
        help='Other vehicle specs this part is compatible with',
    )

    # === Part Category ===
    itx_part_category_id = fields.Many2one(
        comodel_name='itx.info.vehicle.part.category',
        string='Part Category',
        index=True,
    )

    # === Part Name (Master Table) ===
    itx_part_name_id = fields.Many2one(
        comodel_name='itx.info.vehicle.template.part',
        string='Part Name',
        index=True,
        help='Part name from master table (e.g., ไฟหน้าซ้าย, กันชนหน้า)',
    )

    # === Part Information ===
    itx_part_brand = fields.Char(
        string='Part Brand',
        index=True,
        help='Part manufacturer brand (e.g., Denso, Bosch, OEM)',
    )
    itx_part_number = fields.Char(
        string='Part Number',
        index=True,
        help='Manufacturer part number',
    )
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
    @api.constrains('itx_is_vehicle_part', 'itx_spec_id', 'itx_part_name_id',
                    'itx_part_origin', 'itx_condition')
    def _check_vehicle_part_required_and_unique(self):
        """
        1. Required fields validation for vehicle parts
        2. Unique constraint: spec_id + part_name_id + origin + condition
        Non-vehicle products (itx_is_vehicle_part=False) → Odoo original 100%
        """
        from odoo.exceptions import ValidationError

        for rec in self:
            if not rec.itx_is_vehicle_part:
                continue  # General product = Odoo original, no validation

            # === Required Fields Check ===
            missing = []
            if not rec.itx_spec_id:
                missing.append('Vehicle Spec')
            if not rec.itx_part_name_id:
                missing.append('Part Name')
            if not rec.itx_part_origin:
                missing.append('Part Origin')
            if not rec.itx_condition:
                missing.append('Condition')

            if missing:
                raise ValidationError(
                    f"Vehicle Part ต้องระบุ: {', '.join(missing)}"
                )

            # === Unique Constraint Check ===
            domain = [
                ('id', '!=', rec.id),
                ('itx_is_vehicle_part', '=', True),
                ('itx_spec_id', '=', rec.itx_spec_id.id),
                ('itx_part_name_id', '=', rec.itx_part_name_id.id),
                ('itx_part_origin', '=', rec.itx_part_origin),
                ('itx_condition', '=', rec.itx_condition),
            ]
            duplicate = self.search(domain, limit=1)
            if duplicate:
                raise ValidationError(
                    f"อะไหล่ซ้ำ: {rec.itx_spec_id.display_name} - "
                    f"{rec.itx_part_name_id.name} ({rec.itx_part_origin}, {rec.itx_condition}) "
                    f"มีอยู่แล้วในระบบ!"
                )

    # === Onchange Methods ===
    @api.onchange('itx_part_name_id')
    def _onchange_itx_part_name_id(self):
        """Auto-fill product name and category from part template"""
        if self.itx_is_vehicle_part and self.itx_part_name_id:
            self.name = self.itx_part_name_id.name
            # Always update category from part template
            if self.itx_part_name_id.category_id:
                self.itx_part_category_id = self.itx_part_name_id.category_id

    @api.onchange('itx_spec_id')
    def _onchange_itx_spec_id(self):
        """Recompute default_code when spec changes"""
        if self.itx_is_vehicle_part:
            self._compute_itx_default_code()

    @api.onchange('itx_is_vehicle_part', 'itx_spec_id', 'itx_part_category_id',
                  'itx_part_name_id', 'itx_sequence')
    def _onchange_compute_default_code(self):
        """Auto-generate internal reference from vehicle hierarchy"""
        if self.itx_is_vehicle_part:
            self._compute_itx_default_code()

    # === Compute Internal Reference ===
    def _compute_itx_default_code(self):
        """Build default_code from abbreviations
        Format: BRAND-MODEL-GEN-SPEC-CAT-PART-SEQ
        """
        for rec in self:
            if rec.itx_is_vehicle_part and rec.itx_spec_id:
                parts = []
                # Get from spec's related fields
                if rec.itx_spec_id.brand_id and rec.itx_spec_id.brand_id.abbr:
                    parts.append(rec.itx_spec_id.brand_id.abbr)
                if rec.itx_spec_id.model_id and rec.itx_spec_id.model_id.abbr:
                    parts.append(rec.itx_spec_id.model_id.abbr)
                if rec.itx_spec_id.generation_id and rec.itx_spec_id.generation_id.abbr:
                    parts.append(rec.itx_spec_id.generation_id.abbr)
                if rec.itx_spec_id.abbr:
                    parts.append(rec.itx_spec_id.abbr)
                if rec.itx_part_category_id and rec.itx_part_category_id.abbr:
                    parts.append(rec.itx_part_category_id.abbr)
                # Add part name abbr
                if rec.itx_part_name_id and rec.itx_part_name_id.abbr:
                    parts.append(rec.itx_part_name_id.abbr)
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
            'itx_is_vehicle_part', 'itx_spec_id', 'itx_part_category_id',
            'itx_part_name_id', 'itx_sequence'
        ]
        if any(f in vals for f in vehicle_fields):
            for record in self:
                if record.itx_is_vehicle_part:
                    record._compute_itx_default_code()

        return result
