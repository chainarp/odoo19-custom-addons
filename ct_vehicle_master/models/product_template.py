from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # Part brand (e.g. Denso, Bosch, NGK)
    part_brand = fields.Char(
        string='Part Brand',
        help='Brand/Manufacturer of the part (e.g. Denso, Bosch, NGK)'
    )

    # Compatible vehicle models (Many2many)
    compatible_vehicle_model_ids = fields.Many2many(
        'fleet.vehicle.model',
        'product_template_fleet_vehicle_model_rel',
        'product_template_id',
        'vehicle_model_id',
        string='Compatible Models',
        help='Vehicle models this part is compatible with'
    )

    # Part number
    part_number = fields.Char(
        string='Part Number',
        help='Manufacturer part number'
    )
