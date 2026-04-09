# -*- coding: utf-8 -*-

from odoo import api, fields, models


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
    @api.constrains('itx_is_vehicle_part', 'itx_spec_id', 'itx_part_name_id')
    def _check_vehicle_part_required_and_unique(self):
        """
        1. Required fields validation for vehicle parts
        2. Unique constraint: spec_id + part_name_id (origin/condition now in variant)
        Non-vehicle products (itx_is_vehicle_part=False) -> Odoo original 100%
        """
        from odoo.exceptions import ValidationError

        for rec in self:
            if not rec.itx_is_vehicle_part:
                continue

            # === Required Fields Check ===
            missing = []
            if not rec.itx_spec_id:
                missing.append('Vehicle Spec')
            if not rec.itx_part_name_id:
                missing.append('Part Name')

            if missing:
                raise ValidationError(
                    f"Vehicle Part ต้องระบุ: {', '.join(missing)}"
                )

            # === Unique Constraint Check: (spec, part_name) ===
            domain = [
                ('id', '!=', rec.id),
                ('itx_is_vehicle_part', '=', True),
                ('itx_spec_id', '=', rec.itx_spec_id.id),
                ('itx_part_name_id', '=', rec.itx_part_name_id.id),
            ]
            duplicate = self.search(domain, limit=1)
            if duplicate:
                raise ValidationError(
                    f"อะไหล่ซ้ำ: {rec.itx_spec_id.display_name} - "
                    f"{rec.itx_part_name_id.name} มีอยู่แล้วในระบบ!"
                )

    # === Onchange Methods ===
    @api.onchange('itx_part_name_id')
    def _onchange_itx_part_name_id(self):
        """Auto-fill product name and category from part template"""
        if self.itx_is_vehicle_part and self.itx_part_name_id:
            self.name = self.itx_part_name_id.name
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
        (origin/condition no longer in template default_code — shown in variant name)
        """
        for rec in self:
            if rec.itx_is_vehicle_part and rec.itx_spec_id:
                parts = []
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
            if vals.get('itx_is_vehicle_part') and not vals.get('itx_sequence'):
                vals['itx_sequence'] = self.env['ir.sequence'].next_by_code(
                    'itx.info.vehicle.part.sequence'
                ) or '00001'

        records = super().create(vals_list)

        for record in records:
            if record.itx_is_vehicle_part:
                record._compute_itx_default_code()

        return records

    def write(self, vals):
        result = super().write(vals)

        vehicle_fields = [
            'itx_is_vehicle_part', 'itx_spec_id', 'itx_part_category_id',
            'itx_part_name_id', 'itx_sequence'
        ]
        if any(f in vals for f in vehicle_fields):
            for record in self:
                if record.itx_is_vehicle_part:
                    record._compute_itx_default_code()

        return result

    # === Variant Helpers ===
    def _ensure_vehicle_part_attributes(self):
        """Ensure this template has Origin + Condition attribute lines (dynamic).
        Idempotent — safe to call multiple times.
        """
        self.ensure_one()
        PartOrigin = self.env['itx.info.vehicle.part.origin']
        PartCondition = self.env['itx.info.vehicle.part.condition']

        origin_attr = self.env.ref('itx_info_vehicle.attr_part_origin')
        condition_attr = self.env.ref('itx_info_vehicle.attr_part_condition')

        # Collect all attribute value IDs from master data
        origin_values = PartOrigin.search([
            ('active', '=', True),
            ('attribute_value_id', '!=', False),
        ]).mapped('attribute_value_id')

        condition_values = PartCondition.search([
            ('active', '=', True),
            ('attribute_value_id', '!=', False),
        ]).mapped('attribute_value_id')

        existing_attrs = self.attribute_line_ids.mapped('attribute_id')

        PTAL = self.env['product.template.attribute.line']

        if origin_attr not in existing_attrs and origin_values:
            PTAL.create({
                'product_tmpl_id': self.id,
                'attribute_id': origin_attr.id,
                'value_ids': [(6, 0, origin_values.ids)],
            })

        if condition_attr not in existing_attrs and condition_values:
            PTAL.create({
                'product_tmpl_id': self.id,
                'attribute_id': condition_attr.id,
                'value_ids': [(6, 0, condition_values.ids)],
            })

    def _get_or_create_variant(self, origin, condition):
        """Create/find a dynamic variant for the given origin + condition.

        :param origin: itx.info.vehicle.part.origin record
        :param condition: itx.info.vehicle.part.condition record
        :return: product.product (variant)
        """
        self.ensure_one()
        self._ensure_vehicle_part_attributes()

        origin_attr_value = origin.attribute_value_id
        condition_attr_value = condition.attribute_value_id

        if not origin_attr_value or not condition_attr_value:
            from odoo.exceptions import UserError
            raise UserError(
                f"Origin '{origin.name}' หรือ Condition '{condition.name}' "
                f"ยังไม่ได้ผูกกับ product.attribute.value"
            )

        # Find the product.template.attribute.value records for this template
        ptav_origin = self.env['product.template.attribute.value'].search([
            ('product_tmpl_id', '=', self.id),
            ('product_attribute_value_id', '=', origin_attr_value.id),
        ], limit=1)
        ptav_condition = self.env['product.template.attribute.value'].search([
            ('product_tmpl_id', '=', self.id),
            ('product_attribute_value_id', '=', condition_attr_value.id),
        ], limit=1)

        if not ptav_origin or not ptav_condition:
            from odoo.exceptions import UserError
            raise UserError(
                f"ไม่พบ attribute line สำหรับ {origin.name} / {condition.name} "
                f"บน template {self.display_name}"
            )

        combination = ptav_origin + ptav_condition
        return self._create_product_variant(combination)
