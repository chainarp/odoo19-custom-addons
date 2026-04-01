# ITX Info Vehicle — Original Design Document

**Document Type:** BRD (Business Requirements Document) + SRS (Software Requirements Specification)
**Source:** Project Owner
**Odoo Version:** 17.0 (Original) → **19.0** (Current Project)

---

## ที่มาและความต้องการ (Business Context)

ธุรกิจซื้อซากรถยนต์มาแยกชิ้นส่วน (อะไหล่ชิ้นใหญ่) เพื่อขายต่อ
เช่น เครื่องยนต์, เกียร์, ช่วงล่าง, ไฟหน้า, กันชน เป็นต้น

### ปัญหาหลักที่ต้องแก้:
1. อะไหล่ 1 ชิ้น อาจใช้ได้กับรถหลายรุ่น (Cross-compatibility) เพราะผู้ผลิตใช้ Platform ร่วมกัน
2. อะไหล่มีจำนวนจำกัด มักมีแค่ 1 ชิ้นต่อซากรถ 1 คัน
3. ลูกค้าค้นหาจากรถของตัวเอง (Brand/Model/ปี) ไม่รู้จัก Chassis Code หรือ Platform
4. ต้องเชื่อมกับ Odoo Inventory, Sale, และ MRP (สำหรับ Unbuild/แยกชิ้นส่วน)

---

## ความรู้พื้นฐานด้านรถยนต์ที่ระบบต้องเข้าใจ

### Platform Sharing
ผู้ผลิตรถยนต์ใช้โครงสร้างพื้นฐาน (Platform) ร่วมกันระหว่างหลาย Model และหลาย Generation
เช่น Honda Civic FD (Gen8) และ Honda CR-V Gen3 ใช้ Platform ใกล้เคียงกัน
ทำให้อะไหล่บางชิ้นใช้แทนกันได้ข้ามรุ่น

### Chassis Code vs Generation vs VIN
- **Chassis Code** = รหัสรุ่นที่ผู้ผลิตใช้ภายใน เช่น FD1, FD2, FB7, FK7 (ไม่ใช่เลขประจำรถ)
- **Generation** = ยุคการผลิตของรถรุ่นนั้น เช่น Civic Gen8, Civic Gen9
- **VIN** = เลขตัวถัง 17 หลักมาตรฐานสากล ประจำรถแต่ละคัน (ไม่ซ้ำกัน)
- Chassis Code ≠ VIN — Chassis Code บอกรุ่น, VIN บอกตัวรถแต่ละคัน

### การใช้อะไหล่ร่วมกัน
แม้เครื่องยนต์รุ่นเดียวกัน อาจใช้แทนกันไม่ได้ 100% เพราะ Spec ต่างกัน, ปีผลิต, Engine mount
การยืนยัน Compatibility ที่แม่นยำที่สุดคือดู OEM Part Number ตรงกัน

---

## โครงสร้างข้อมูล (Data Architecture)

### ลำดับชั้นข้อมูลรถยนต์
```
Brand → Model → Generation → Variant
              ↓
          Platform (cross-cutting concern ที่ผูก Generation ข้าม Model ได้)
```

---

## Odoo Models ทั้งหมดใน addon นี้

### 1. itx_info_vehicle_brand
ยี่ห้อรถยนต์

| Field | Type | คำอธิบาย |
|---|---|---|
| name | Char (required) | ชื่อยี่ห้อ เช่น Honda, Toyota, Isuzu |
| country_id | Many2one res.country | ประเทศผู้ผลิต |
| logo | Image | โลโก้ยี่ห้อ |
| active | Boolean | default=True |
| model_ids | One2many itx_info_vehicle_model | รุ่นทั้งหมดของยี่ห้อนี้ |

---

### 2. itx_info_vehicle_platform
Platform / โครงสร้างพื้นฐานร่วม (ใช้ผูก Cross-compatibility)

| Field | Type | คำอธิบาย |
|---|---|---|
| name | Char (required) | ชื่อ Platform เช่น "Honda Global Small Car" |
| brand_id | Many2one itx_info_vehicle_brand | เจ้าของ Platform |
| internal_code | Char | รหัสใช้ภายใน เช่น "HGSC-B" |
| note | Text | หมายเหตุ เช่น Generation ที่รู้ว่าใช้ร่วมกัน |
| active | Boolean | default=True |
| generation_ids | One2many itx_info_vehicle_generation | Generation ที่ใช้ Platform นี้ |

---

### 3. itx_info_vehicle_model
รุ่นรถยนต์ (Model)

| Field | Type | คำอธิบาย |
|---|---|---|
| name | Char (required) | ชื่อรุ่น เช่น Civic, Accord, CR-V |
| brand_id | Many2one itx_info_vehicle_brand (required) | ยี่ห้อ |
| body_type | Selection | sedan, hatchback, suv, pickup, van, truck, other |
| active | Boolean | default=True |
| generation_ids | One2many itx_info_vehicle_generation | Generation ทั้งหมดของ Model นี้ |

---

### 4. itx_info_vehicle_generation
ยุค/รุ่นย่อยของ Model (Generation)

| Field | Type | คำอธิบาย |
|---|---|---|
| name | Char (required) | ชื่อ Generation เช่น "Gen 8 (FD)" |
| model_id | Many2one itx_info_vehicle_model (required) | สังกัด Model |
| platform_id | Many2one itx_info_vehicle_platform | Platform ที่ใช้ (สำคัญมาก) |
| chassis_code | Char | รหัส Chassis เช่น FD1/FD2 หรือ FB7 |
| year_start | Integer | ปีเริ่มผลิต |
| year_end | Integer | ปีสิ้นสุดผลิต (0 = ยังผลิตอยู่) |
| has_facelift | Boolean | มีการ Facelift กลางรุ่นหรือไม่ |
| facelift_year | Integer | ปีที่ Facelift (ถ้ามี) |
| note | Text | หมายเหตุ |
| active | Boolean | default=True |
| variant_ids | One2many itx_info_vehicle_variant | Variant ทั้งหมดของ Generation นี้ |

---

### 5. itx_info_vehicle_variant
รุ่นย่อย / Trim Level (Variant)

| Field | Type | คำอธิบาย |
|---|---|---|
| name | Char (required) | ชื่อ Variant เช่น "1.8 S i-VTEC", "2.0 EL", "Type-R" |
| generation_id | Many2one itx_info_vehicle_generation (required) | สังกัด Generation |
| engine_code | Char | รหัสเครื่องยนต์ เช่น R18A, K20A, L15B |
| engine_displacement | Float | ขนาดเครื่อง (ลิตร) เช่น 1.8, 2.0 |
| fuel_type | Selection | gasoline, diesel, hybrid, ev, other |
| transmission | Selection | manual, auto, cvt, dct, other |
| drive_type | Selection | ff (Front-wheel), fr (Rear-wheel), awd, 4wd |
| doors | Integer | จำนวนประตู |
| active | Boolean | default=True |

Computed / Related Fields:

| Field | Type | คำอธิบาย |
|---|---|---|
| brand_id | Many2one (related generation_id.model_id.brand_id, store=True) | ยี่ห้อ |
| model_id | Many2one (related generation_id.model_id, store=True) | Model |
| platform_id | Many2one (related generation_id.platform_id, store=True) | Platform |
| year_start | Integer (related generation_id.year_start, store=True) | ปีเริ่มต้น |
| year_end | Integer (related generation_id.year_end, store=True) | ปีสิ้นสุด |

---

### 6. itx_info_vehicle_part_category
ประเภทอะไหล่ (รองรับ Hierarchy)

| Field | Type | คำอธิบาย |
|---|---|---|
| name | Char (required) | ชื่อประเภท เช่น "เครื่องยนต์", "เกียร์", "ช่วงล่าง" |
| parent_id | Many2one itx_info_vehicle_part_category | ประเภทแม่ (สำหรับ hierarchy) |
| child_ids | One2many itx_info_vehicle_part_category | ประเภทย่อย |
| complete_name | Char (computed) | ชื่อเต็มรวม parent เช่น "เครื่องยนต์ / หัวเครื่อง" |
| active | Boolean | default=True |

---

### 7. itx_info_vehicle_compatibility
ตาราง Compatibility Matrix (กรอกครั้งเดียว ค้นข้ามรุ่นได้ตลอด)

| Field | Type | คำอธิบาย |
|---|---|---|
| part_category_id | Many2one itx_info_vehicle_part_category (required) | ประเภทอะไหล่ที่ compatible |
| from_generation_id | Many2one itx_info_vehicle_generation (required) | Generation ต้นทาง |
| to_generation_ids | Many2many itx_info_vehicle_generation | Generation ที่ใช้ร่วมได้ |
| compatibility_type | Selection | full=ใช้ได้ 100%, partial=ต้องดัดแปลง, platform=Platform เดียวกัน |
| oem_part_number | Char | OEM Part Number ที่ยืนยัน compatibility |
| note | Text | หมายเหตุ เช่น ต้องเปลี่ยน bracket, ต้องตัด harness |
| active | Boolean | default=True |

---

### 8. product.template (inherit)
เพิ่ม field รถยนต์ใน product.template เพื่อใช้กับ Inventory และ Sale

| Field | Type | คำอธิบาย |
|---|---|---|
| itx_is_vehicle_part | Boolean | เปิดใช้งาน Vehicle Part mode |
| itx_brand_id | Many2one itx_info_vehicle_brand | ยี่ห้อรถ |
| itx_model_id | Many2one itx_info_vehicle_model | Model รถ |
| itx_generation_id | Many2one itx_info_vehicle_generation | Generation |
| itx_variant_id | Many2one itx_info_vehicle_variant | Variant |
| itx_platform_id | Many2one (related generation_id.platform_id, store=True) | Platform |
| itx_part_category_id | Many2one itx_info_vehicle_part_category | ประเภทอะไหล่ |
| itx_compatible_generation_ids | Many2many itx_info_vehicle_generation | Generation ทั้งหมดที่ใช้ได้ (รวม cross-compatible) |
| itx_oem_part_number | Char | OEM Part Number |
| itx_condition_grade | Selection | A=ดีมาก, B=ดี, C=พอใช้, D=ต้องซ่อม |
| itx_salvage_car_id | Many2one itx_info_vehicle_salvage_car | ที่มาจากซากรถคันไหน |

---

### 9. itx_info_vehicle_salvage_car
ซากรถที่ซื้อเข้ามา (เพื่อติดตามที่มาของอะไหล่)

| Field | Type | คำอธิบาย |
|---|---|---|
| name | Char (computed) | รหัสซากรถ เช่น "SAL/2024/0001" |
| variant_id | Many2one itx_info_vehicle_variant (required) | รุ่นรถ |
| vin | Char | เลขตัวถัง VIN 17 หลัก |
| year | Integer | ปีของรถ (อาจต่างจาก year_start ของ Generation) |
| salvage_condition | Selection | accident, flood, engine_dead, fire, other |
| purchase_date | Date | วันที่ซื้อ |
| purchase_price | Float | ราคาที่ซื้อมา |
| state | Selection | received=รับเข้า, dismantling=กำลังแยก, completed=แยกแล้ว |
| product_id | Many2one product.product | product ที่แทนซากรถ (ใช้กับ Inventory และ MRP Unbuild) |
| bom_id | Many2one mrp.bom | BOM สำหรับ Unbuild คันนี้ |
| part_ids | One2many product.template | อะไหล่ที่แยกออกมาแล้ว |
| note | Text | หมายเหตุ |

Related fields (store=True):
- brand_id, model_id, generation_id, platform_id (มาจาก variant_id)

---

## การเชื่อมกับ MRP (Unbuild / แตกชิ้นส่วน)

### แนวคิด
- ซากรถ 1 คัน = product 1 ชิ้น (tracking=serial, serial=VIN หรือรหัสภายใน)
- สร้าง mrp.bom แบบ Disassembly: finished product = ซากรถ, components = อะไหล่แต่ละชิ้น
- ใช้ mrp.unbuild เพื่อตัดสต็อกซากรถ และเพิ่มสต็อกอะไหล่

### BOM Line เพิ่มเติม
ใน mrp.bom.line ควร inherit เพิ่ม:

| Field | Type | คำอธิบาย |
|---|---|---|
| itx_cost_weight | Float | น้ำหนักสัดส่วนต้นทุน เช่น เครื่อง=40, เกียร์=20 |
| itx_condition_grade | Selection | สภาพอะไหล่ชิ้นนี้ที่คาดว่าจะได้ |

### Cost Allocation Logic
```
ต้นทุนอะไหล่ = ราคาซากรถ × (cost_weight ของชิ้นนี้ / sum cost_weight ทั้งหมด)
```

---

## Search / Compatibility Logic

### การค้นหาของลูกค้า
ลูกค้าเลือก: Brand → Model → ปีรถ → Variant → ประเภทอะไหล่
ระบบ map ปีรถไปหา Generation อัตโนมัติ (year_start <= ปี <= year_end)

### ผลการค้นหา แบ่ง 3 ระดับ
1. **ตรงรุ่น 100%** — generation_id ตรงกัน
2. **Platform เดียวกัน** — platform_id ตรงกัน
3. **Compatible ตาม Matrix** — มีข้อมูลใน itx_info_vehicle_compatibility

### Search Method
```python
def action_search_compatible_parts(variant_id, part_category_id):
    1. หา generation และ platform จาก variant_id
    2. หา generation ที่ compatible จาก itx_info_vehicle_compatibility
    3. รวม generation จาก platform เดียวกัน
    4. search product.template ที่ itx_compatible_generation_ids มี generation เหล่านั้น
       และ itx_part_category_id ตรงกัน
       และ state = available (sale_ok=True, qty_on_hand > 0)
    5. return พร้อม flag ว่า match ระดับไหน
```

---

## โครงสร้าง Module (Full Version)

```
itx_info_vehicle/
├── __manifest__.py
│     name: "ITX Info Vehicle"
│     version: 19.0.1.0.0
│     depends: ['product', 'stock', 'mrp', 'sale']
│     category: 'ITExpert/Vehicle'
│
├── models/
│   ├── __init__.py
│   ├── itx_info_vehicle_brand.py
│   ├── itx_info_vehicle_platform.py          # Phase 2
│   ├── itx_info_vehicle_model.py
│   ├── itx_info_vehicle_generation.py
│   ├── itx_info_vehicle_variant.py
│   ├── itx_info_vehicle_part_category.py
│   ├── itx_info_vehicle_compatibility.py     # Phase 2
│   ├── itx_info_vehicle_salvage_car.py       # Phase 2
│   ├── product_template.py
│   └── mrp_bom_line.py                       # Phase 2
│
├── views/
│   └── (corresponding XML files)
│
├── security/
│   └── ir.model.access.csv
│
└── data/
    └── itx_info_vehicle_part_category_data.xml
```

---

## หมายเหตุสำหรับ Implementation

1. ~~ใช้ Odoo 17 Community Edition~~ → **Odoo 19**
2. ทุก model ใช้ prefix `itx_info_vehicle_` ทั้ง Python class และ _name
3. product.template inherit ใช้ prefix field `itx_` ทุก field
4. ทุก Many2one ที่เป็น car hierarchy ให้ทำ onchange cascade
5. itx_platform_id ใน product.template ให้ store=True เพื่อ performance
6. itx_compatible_generation_ids ควร compute อัตโนมัติจาก itx_generation_id + compatibility matrix แต่ให้ override ได้
7. salvage_car ต้องผูกกับ product (ซากรถ) เพื่อรองรับ mrp.unbuild
8. Security group: Vehicle Manager, Vehicle User แยกจากกัน

---

*Document imported from Project Owner's specification*
*Updated for Odoo 19: 2026-03-26*
