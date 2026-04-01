/** @odoo-module **/
import { registry } from "@web/core/registry";

const orderNotificationService = {
    dependencies: ["bus_service", "notification"],
    start(env, { bus_service, notification }) {

        // 1. บอกให้ Bus Service คอยฟัง Channel ชื่อนี้
        bus_service.addChannel("global_order_channel");

        // 2. เมื่อได้รับ Message ประเภท 'simple_notification' ให้ทำตามคำสั่งนี้
        bus_service.subscribe("simple_notification", (payload) => {
            notification.add(payload.message, {
                title: payload.title,
                type: "warning", // สีเหลือง/ส้ม (เปลี่ยนเป็น success, danger ได้)
                sticky: payload.sticky,
            });
        });
    },
};

// ลงทะเบียน Service เข้าสู่ระบบของ Odoo
registry.category("services").add("orderNotificationService", orderNotificationService);