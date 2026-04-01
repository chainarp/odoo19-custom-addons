# from odoo import models, fields, api


# class ct_vehicle_master(models.Model):
#     _name = 'ct_vehicle_master.ct_vehicle_master'
#     _description = 'ct_vehicle_master.ct_vehicle_master'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

