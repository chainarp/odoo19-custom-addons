# from odoo import http


# class CtVehicleMaster(http.Controller):
#     @http.route('/ct_vehicle_master/ct_vehicle_master', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ct_vehicle_master/ct_vehicle_master/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('ct_vehicle_master.listing', {
#             'root': '/ct_vehicle_master/ct_vehicle_master',
#             'objects': http.request.env['ct_vehicle_master.ct_vehicle_master'].search([]),
#         })

#     @http.route('/ct_vehicle_master/ct_vehicle_master/objects/<model("ct_vehicle_master.ct_vehicle_master"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ct_vehicle_master.object', {
#             'object': obj
#         })

