# Part Name Reference (จาก User Excel)

**Source:** แบบประเมินซากรถยนต์.xlsx
**Generated:** 2026-04-03

---

## สรุป Body Types (จาก Sheet Names)

| Sheet | Thai | English | รหัสแนะนำ |
|-------|------|---------|-----------|
| กะบะแคป | กระบะแค็บ | Extra Cab Pickup | XCAB |
| กะบะ 4 ประตู | กระบะ 4 ประตู | Double Cab Pickup | DCAB |
| SUV | SUV | SUV | SUV |
| รถตู้ | รถตู้ | Van | VAN |
| รถตู้ VIP | รถตู้ VIP | VIP Van | VIPVAN |
| สิบล้อ | สิบล้อ | Truck | TRUCK |
| รถเก๋ง | รถเก๋ง | Sedan | SEDAN |

---

## รายการอะไหล่ (Cleaned & Corrected)

### กลุ่มบอดี้ (Body Parts)

| # | ชื่อไทย (แก้ไขแล้ว) | English | Code | หมายเหตุ |
|---|---------------------|---------|------|----------|
| 1 | กันชนหน้า | Front Bumper | BUMP_FR | |
| 2 | กันชนหลัง | Rear Bumper | BUMP_RR | |
| 3 | บังโคลนหน้าขวา | Front Right Fender | FEND_FR_R | |
| 4 | บังโคลนหน้าซ้าย | Front Left Fender | FEND_FR_L | |
| 5 | บังโคลนหลังขวา | Rear Right Fender | FEND_RR_R | เฉพาะรถเก๋ง |
| 6 | บังโคลนหลังซ้าย | Rear Left Fender | FEND_RR_L | เฉพาะรถเก๋ง |
| 7 | ประตูหน้าขวา | Front Right Door | DOOR_FR_R | |
| 8 | ประตูหน้าซ้าย | Front Left Door | DOOR_FR_L | |
| 9 | ประตูหลังขวา | Rear Right Door | DOOR_RR_R | 4 ประตู/SUV/รถเก๋ง |
| 10 | ประตูหลังซ้าย | Rear Left Door | DOOR_RR_L | 4 ประตู/SUV/รถเก๋ง |
| 11 | ประตูแค็บขวา | Right Cap Door | DOOR_CAP_R | เฉพาะกระบะแค็บ |
| 12 | ประตูแค็บซ้าย | Left Cap Door | DOOR_CAP_L | เฉพาะกระบะแค็บ |
| 13 | ประตูสไลด์ข้างซ้าย | Left Slide Door | DOOR_SL_L | เฉพาะรถตู้ |
| 14 | ประตูสไลด์ไฟฟ้าข้างซ้าย | Left Power Slide Door | DOOR_SLP_L | เฉพาะรถตู้ VIP |
| 15 | ประตูสไลด์ไฟฟ้าข้างขวา | Right Power Slide Door | DOOR_SLP_R | เฉพาะรถตู้ VIP |
| 16 | ฝากระโปรงหน้า | Front Hood | HOOD_FR | |
| 17 | ฝากระโปรงหลัง | Rear Hood/Trunk Lid | HOOD_RR | |
| 18 | ฝาปิดท้ายกระบะ | Tailgate | TAILGATE | เฉพาะกระบะ |
| 19 | หลังคา | Roof | ROOF | |
| 20 | กระจกมองข้างขวา | Right Side Mirror | MIRROR_R | |
| 21 | กระจกมองข้างซ้าย | Left Side Mirror | MIRROR_L | |
| 22 | แผงหน้า | Front Panel/Radiator Support | PANEL_FR | |
| 23 | แผงท้าย | Rear Panel | PANEL_RR | เฉพาะรถเก๋ง |
| 24 | หน้ากระจังตัวใน | Inner Grille | GRILLE_IN | |
| 25 | หน้ากระจังตัวนอก | Outer Grille | GRILLE_OUT | |
| 26 | กระบะ | Pickup Bed | BED | เฉพาะกระบะ |
| 27 | สเกิร์ตกันชนหน้า | Front Bumper Skirt | SKIRT_FR | เฉพาะรถเก๋ง |
| 28 | สเกิร์ตกันชนหลัง | Rear Bumper Skirt | SKIRT_RR | เฉพาะรถเก๋ง |
| 29 | สเกิร์ตบันไดขวา | Right Side Skirt | SKIRT_SD_R | เฉพาะรถเก๋ง |
| 30 | สเกิร์ตบันไดซ้าย | Left Side Skirt | SKIRT_SD_L | เฉพาะรถเก๋ง |
| 31 | บังลมหน้า | Front Deflector | DEFLECT_FR | เฉพาะสิบล้อ |

---

### กลุ่มช่วงล่าง (Suspension & Steering)

| # | ชื่อไทย (แก้ไขแล้ว) | English | Code | หมายเหตุ |
|---|---------------------|---------|------|----------|
| 1 | ปีกนกหน้าขวา | Front Right Lower Arm | ARM_LO_FR_R | |
| 2 | ปีกนกหน้าซ้าย | Front Left Lower Arm | ARM_LO_FR_L | |
| 3 | ปีกนกบนหน้าขวา | Front Right Upper Arm | ARM_UP_FR_R | |
| 4 | ปีกนกบนหน้าซ้าย | Front Left Upper Arm | ARM_UP_FR_L | |
| 5 | ปีกนกล่างหน้าขวา | Front Right Lower Arm | ARM_LO_FR_R | ซ้ำ #1 |
| 6 | ปีกนกล่างหน้าซ้าย | Front Left Lower Arm | ARM_LO_FR_L | ซ้ำ #2 |
| 7 | คอม้าหน้าขวา | Right Front Strut | STRUT_FR_R | |
| 8 | คอม้าหน้าซ้าย | Left Front Strut | STRUT_FR_L | |
| 9 | โช้คอัพหน้าขวา | Front Right Shock | SHOCK_FR_R | |
| 10 | โช้คอัพหน้าซ้าย | Front Left Shock | SHOCK_FR_L | |
| 11 | โช้คอัพหลังขวา | Rear Right Shock | SHOCK_RR_R | |
| 12 | โช้คอัพหลังซ้าย | Rear Left Shock | SHOCK_RR_L | |
| 13 | แร็คพวงมาลัย | Steering Rack | RACK_STEER | |
| 14 | เพลาท้าย | Rear Axle | AXLE_RR | |
| 15 | เพลาหน้า | Front Axle | AXLE_FR | เฉพาะ SUV |
| 16 | เพลาข้าง | Side Axle | AXLE_SD | เฉพาะสิบล้อ |
| 17 | เพลาขับหน้าขวา | Front Right Drive Shaft | SHAFT_FR_R | เฉพาะรถเก๋ง |
| 18 | เพลาขับหน้าซ้าย | Front Left Drive Shaft | SHAFT_FR_L | เฉพาะรถเก๋ง |
| 19 | คานใต้เครื่อง | Subframe | SUBFRAME | เฉพาะรถเก๋ง |
| 20 | คานหลัง | Rear Crossmember | CROSSMEM_RR | เฉพาะรถเก๋ง |
| 21 | แพหน้าทั้งชุด | Front Subframe Assembly | SUBFRAME_FR | เฉพาะรถเก๋ง |
| 22 | คานหลังทั้งชุด | Rear Subframe Assembly | SUBFRAME_RR | เฉพาะรถเก๋ง |

---

### กลุ่มไฟ (Lighting)

| # | ชื่อไทย (แก้ไขแล้ว) | English | Code | หมายเหตุ |
|---|---------------------|---------|------|----------|
| 1 | ไฟหน้าขวา | Right Headlight | LIGHT_HD_R | เดิม: ไฟใหญ่หน้าขวา |
| 2 | ไฟหน้าซ้าย | Left Headlight | LIGHT_HD_L | เดิม: ไฟใหญ่หน้าซ้าย |
| 3 | ไฟท้ายขวา | Right Taillight | LIGHT_TL_R | เดิม: ไฟท้ายหลังขวา |
| 4 | ไฟท้ายซ้าย | Left Taillight | LIGHT_TL_L | เดิม: ไฟท้ายหลังซ้าย |
| 5 | ไฟทับทิมหลังขวา | Right Rear Reflector | REFL_RR_R | |
| 6 | ไฟทับทิมหลังซ้าย | Left Rear Reflector | REFL_RR_L | |

---

### กลุ่มไฟฟ้า (Electrical)

| # | ชื่อไทย (แก้ไขแล้ว) | English | Code | หมายเหตุ |
|---|---------------------|---------|------|----------|
| 1 | ชุดสายไฟเข้ากล่องฟิวส์ | Fuse Box Wiring Harness | WIRE_FUSE | |
| 2 | ชุดสายไฟเข้าเครื่องยนต์ | Engine Wiring Harness | WIRE_ENG | |
| 3 | ชุดสายไฟเข้าคอนโซล | Console Wiring Harness | WIRE_CONS | |
| 4 | กล่อง ECU | ECU | ECU | |
| 5 | ปั๊ม ABS | ABS Pump | ABS_PUMP | |
| 6 | กล่องควบคุมแอร์แบ็ก | Airbag Control Module | AIRBAG_MOD | |
| 7 | เซ็นเซอร์กันชนหน้า | Front Bumper Sensor | SENS_BUMP_FR | |
| 8 | เซ็นเซอร์กันชนหลัง | Rear Bumper Sensor | SENS_BUMP_RR | |
| 9 | มอเตอร์พัดลมหม้อน้ำ | Radiator Fan Motor | MOTOR_RAD | |
| 10 | มอเตอร์พัดลมแอร์ | A/C Fan Motor | MOTOR_AC | |

---

### กลุ่มภายใน (Interior)

| # | ชื่อไทย (แก้ไขแล้ว) | English | Code | หมายเหตุ |
|---|---------------------|---------|------|----------|
| 1 | แผงแอร์ | A/C Panel | PANEL_AC | |
| 2 | ชุดคอนโซลหน้าปัด | Dashboard Console | CONSOLE | |
| 3 | ถุงลมนิรภัยขวา | Right Airbag | AIRBAG_R | |
| 4 | ถุงลมนิรภัยซ้าย | Left Airbag | AIRBAG_L | |
| 5 | ถุงลมหน้าซ้าย-ขวา | Front Airbags | AIRBAG_FR | เฉพาะรถตู้ VIP |
| 6 | ถุงลมหลังซ้าย-ขวา | Rear Airbags | AIRBAG_RR | เฉพาะรถตู้ VIP |

---

### กลุ่มเครื่องยนต์และส่งกำลัง (Engine & Drivetrain)

| # | ชื่อไทย (แก้ไขแล้ว) | English | Code | หมายเหตุ |
|---|---------------------|---------|------|----------|
| 1 | ชุดเกียร์ | Transmission | TRANS | |
| 2 | หม้อน้ำ | Radiator | RADIATOR | |
| 3 | ราคาตัดหัว | Cut-off Front Price | - | ไม่ใช่อะไหล่ |
| 4 | ราคาตัดท้าย | Cut-off Rear Price | - | ไม่ใช่อะไหล่ |

---

### กลุ่มล้อ (Wheels)

| # | ชื่อไทย (แก้ไขแล้ว) | English | Code | หมายเหตุ |
|---|---------------------|---------|------|----------|
| 1 | ล้อแม็กหน้าขวา | Front Right Alloy Wheel | WHEEL_FR_R | |
| 2 | ล้อแม็กหน้าซ้าย | Front Left Alloy Wheel | WHEEL_FR_L | |
| 3 | ล้อแม็กหลังขวา | Rear Right Alloy Wheel | WHEEL_RR_R | |
| 4 | ล้อแม็กหลังซ้าย | Rear Left Alloy Wheel | WHEEL_RR_L | |

---

### กลุ่มสิบล้อเฉพาะ (Truck Specific)

| # | ชื่อไทย (แก้ไขแล้ว) | English | Code | หมายเหตุ |
|---|---------------------|---------|------|----------|
| 1 | ปั๊มไฮดรอลิก | Hydraulic Pump | PUMP_HYD | |
| 2 | กระบอกไฮดรอลิก | Hydraulic Cylinder | CYL_HYD | |

---

## สรุปจำนวนอะไหล่

| หมวด | จำนวน |
|------|-------|
| กลุ่มบอดี้ | 31 |
| กลุ่มช่วงล่าง | 22 |
| กลุ่มไฟ | 6 |
| กลุ่มไฟฟ้า | 10 |
| กลุ่มภายใน | 6 |
| กลุ่มเครื่องยนต์ | 2 |
| กลุ่มล้อ | 4 |
| กลุ่มสิบล้อ | 2 |
| **รวม** | **~80 รายการ** |

---

## หมายเหตุการแก้ไขสะกด

| เดิม (จาก Excel) | แก้ไขเป็น | เหตุผล |
|------------------|-----------|--------|
| กะบะแคป | กระบะแค็บ | สะกดผิด |
| กะบะ | กระบะ | สะกดผิด |
| ไฟใหญ่หน้า | ไฟหน้า | ใช้คำทั่วไป |
| ไฟท้ายหลัง | ไฟท้าย | ซ้ำซ้อน |
| กล่องECU | กล่อง ECU | เว้นวรรค |
| ปั๊มABS | ปั๊ม ABS | เว้นวรรค |
| ประตูแคป | ประตูแค็บ | สะกดผิด |

---

## ข้อเสนอแนะ

1. **รวม Part ที่ซ้ำ**: ปีกนกหน้า กับ ปีกนกล่างหน้า เป็นตัวเดียวกัน
2. **แยก Position**: ซ้าย/ขวา/หน้า/หลัง ควรอยู่ใน field แยก (user handle)
3. **ไม่ใส่รายการที่ไม่ใช่อะไหล่**: ราคาตัดหัว, กำไร 25%, etc.

---

*ไฟล์นี้ใช้เป็น reference สำหรับสร้าง Part Template Master Data*
