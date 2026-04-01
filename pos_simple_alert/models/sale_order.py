from odoo import models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()

        # สร้างชื่อ Channel (จะตั้งชื่ออะไรก็ได้ แต่ฝั่ง JS ต้องใช้ชื่อเดียวกัน)
        channel = "global_order_channel"

        # ส่งข้อมูลเข้า WebSocket
        self.env['bus.bus']._sendone(channel, 'simple_notification', {
            'title': 'ออเดอร์ใหม่เข้าแล้ว!',
            'message': f'หมายเลข: {self.name} โดยลูกค้า {self.partner_id.name}',
            'sticky': True,  # ให้แจ้งเตือนค้างไว้จนกว่าจะกดปิด
        })
        return res