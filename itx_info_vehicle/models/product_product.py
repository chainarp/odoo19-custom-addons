# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    # Override default_code to compute from template base code + variant
    # attribute values (Origin + Condition abbr) for vehicle parts.
    # Non-vehicle products preserve their manually-entered value because
    # their dependencies never change and the compute is idempotent.
    default_code = fields.Char(
        compute='_compute_itx_default_code',
        store=True,
        readonly=False,
    )

    @api.depends(
        'product_tmpl_id.itx_is_vehicle_part',
        'product_tmpl_id.itx_base_code',
        'product_template_attribute_value_ids',
        'product_template_attribute_value_ids.product_attribute_value_id',
    )
    def _compute_itx_default_code(self):
        """For vehicle parts: build default_code from template base code +
        origin abbr + condition abbr (read from linked master data).
        Non-vehicle products: preserve existing value (idempotent no-op).
        """
        origin_attr = self.env.ref(
            'itx_info_vehicle.attr_part_origin', raise_if_not_found=False
        )
        condition_attr = self.env.ref(
            'itx_info_vehicle.attr_part_condition', raise_if_not_found=False
        )
        PartOrigin = self.env['itx.info.vehicle.part.origin']
        PartCondition = self.env['itx.info.vehicle.part.condition']

        for product in self:
            tmpl = product.product_tmpl_id
            if not tmpl.itx_is_vehicle_part:
                # Preserve existing value — dependencies above don't change
                # for non-vehicle products, so this only runs on upgrade.
                product.default_code = product.default_code or False
                continue

            base = tmpl.itx_base_code or ''
            origin_abbr = ''
            condition_abbr = ''

            for ptav in product.product_template_attribute_value_ids:
                attr = ptav.attribute_id
                pav = ptav.product_attribute_value_id
                if origin_attr and attr == origin_attr:
                    origin = PartOrigin.search(
                        [('attribute_value_id', '=', pav.id)], limit=1
                    )
                    if origin:
                        origin_abbr = origin.abbr or ''
                elif condition_attr and attr == condition_attr:
                    condition = PartCondition.search(
                        [('attribute_value_id', '=', pav.id)], limit=1
                    )
                    if condition:
                        condition_abbr = condition.abbr or ''

            parts = [p for p in (base, origin_abbr, condition_abbr) if p]
            product.default_code = '-'.join(parts) if parts else False
