# Design Decisions - ITX Info Vehicle

**Document Type:** Architecture Decision Record (ADR)
**Created:** 2026-03-30
**Purpose:** บันทึกเหตุผลการออกแบบ เพื่ออ้างอิงในอนาคต

---

## Table of Contents

1. [Variant = Master Data (ไม่ใช่รถเป็นคัน)](#1-variant--master-data)
2. [Year Field ไม่อยู่ใน Variant](#2-year-field-ไม่อยู่ใน-variant)
3. [Body Type อยู่ใน Variant](#3-body-type-อยู่ใน-variant)
4. [Engine Fields อยู่ใน Variant (ไม่แยก Model)](#4-engine-fields-อยู่ใน-variant)
5. [Variant ต้องมีอย่างน้อย 1 ตัวต่อ Generation](#5-variant-ต้องมีอย่างน้อย-1-ตัว)
6. [Lookup Tables ใช้ Namespace `adm`](#6-lookup-tables-namespace-adm)

---

## 1. Variant = Master Data

### Decision
`vehicle.variant` เป็น **Master Data** (ข้อมูลประเภท/สเปค) ไม่ใช่ข้อมูลรถเป็นคัน

### Context
ระบบนี้จัดการ "ประเภทรถ" สำหรับ map กับอะไหล่ ไม่ใช่ระบบจัดการรถแต่ละคัน

### Rationale

```
vehicle.variant = "Honda Civic FD 1.8S i-VTEC"
                   ↑
                   "ประเภท/สเปค" ไม่ใช่รถคันใดคันหนึ่ง
```

| Data Type | ตัวอย่าง | อยู่ที่ไหน |
|-----------|---------|-----------|
| Master Data | "Civic FD 1.8S" (ประเภท) | `vehicle.variant` |
| Transaction Data | "รถคันนี้ VIN:xxx ปี 2008" | `salvage_car` (Phase 2) |

### Implications
- ไม่เก็บข้อมูลเฉพาะคัน (VIN, ปีผลิตเฉพาะ) ใน Variant
- ข้อมูลรถเป็นคันๆ อยู่ใน Salvage Car หรือ Product (Phase 2)

---

## 2. Year Field ไม่อยู่ใน Variant

### Decision
ไม่เพิ่ม `year` field ใน `vehicle.variant`

### Context
EPC Spec ต้องการ `year` ใน Variant แต่เราตัดสินใจไม่ใส่

### Rationale

| Level | Data Type | มี year? | เหตุผล |
|-------|-----------|----------|--------|
| Generation | Master | `year_start`, `year_end` | ช่วงปีผลิตของ generation |
| Variant | Master | ❌ ไม่มี | บอกแค่ "สเปค" ไม่ใช่ปีเฉพาะ |
| Salvage Car | Transaction | `year` | ปีของรถคันนั้นๆ (Phase 2) |
| Product/Part | Transaction | ผ่าน salvage_car | ปีของรถต้นทาง |

**เหตุผลหลัก:**
1. Variant = Master data บอกประเภท/สเปค
2. ปีผลิตเฉพาะคัน ใช้ตอนสร้าง Salvage Car (Phase 2)
3. ช่วงปี ดูจาก Generation ได้อยู่แล้ว (`year_start` - `year_end`)

### Date
2026-03-30

---

## 3. Body Type อยู่ใน Variant

### Decision
`body_type_id` อยู่ใน `vehicle.variant` (ไม่ใช่ Model หรือ Generation)

### Context
Body Type ควรอยู่ level ไหน? Model, Generation, หรือ Variant?

### Rationale

**ตัวอย่างจริงที่ใช้วิเคราะห์:**

```
Honda Civic (Model)
├── Gen 10 FC/FK (Generation)
│   ├── 1.8 EL Sedan        → body = Sedan
│   ├── 1.5 Turbo RS Sedan  → body = Sedan
│   └── 1.5 Turbo RS Hatch  → body = Hatchback   ← ต่างกัน!
│
Toyota Hilux (Model)
├── Vigo (Generation)
│   ├── 2.5 J Single Cab    → body = Single Cab
│   ├── 2.5 E Extra Cab     → body = Extra Cab   ← ต่างกัน!
│   └── 3.0 G Double Cab    → body = Double Cab  ← ต่างกัน!
│
Honda CR-V (Model)
├── Gen 5 (Generation)
│   └── ทุก variant         → body = SUV (เหมือนกันหมด)
```

**เปรียบเทียบแต่ละ Level:**

| Level | ข้อดี | ข้อเสีย |
|-------|------|--------|
| **Model** | ง่าย | ❌ ไม่ถูก - Civic มีทั้ง Sedan/Hatch |
| **Generation** | กลางๆ | ❌ 1 Gen มีหลาย body (ต้อง Many2many) |
| **Variant** | ตรงจุด | ✅ 1 Variant = 1 Body Type |

**เหตุผลเลือก Variant:**

1. **1 Variant = 1 Body Type** ชัดเจน
   - "Civic 1.5 RS Hatchback" ≠ "Civic 1.5 RS Sedan"
   - ทั้งสองเป็นคนละ Variant

2. **Generation มีหลาย Body ได้** โดยธรรมชาติ
   - ดูจาก Variants ที่อยู่ใต้ Generation นั้น

3. **ค้นหาง่าย**
   - หา parts สำหรับ "Hilux Double Cab" → filter ที่ `variant.body_type_id`

4. **ไม่ซับซ้อน**
   - ไม่ต้อง Many2many ที่ Generation
   - ไม่ต้อง validate ว่า variant เลือก body ที่ถูกต้อง

### Implementation

```python
# itx.info.vehicle.adm.body_type (Master/Lookup Table)
code = fields.Char(required=True)    # "DOUBLE_CAB"
name = fields.Char(required=True)    # "Double Cab"
active = fields.Boolean(default=True)

# vehicle.variant
body_type_id = fields.Many2one(
    'itx.info.vehicle.adm.body_type',
    string='Body Type',
    index=True,
    # ไม่ required - เป็นแค่ info, ไม่ใช่ key
)
```

### Note
- `body_type_id` เป็น **info only** ไม่ใช่ key ของ Variant
- ไม่อยู่ใน unique constraint
- ไม่ required

### Date
2026-03-30

---

## 4. Engine Fields อยู่ใน Variant

### Decision
เก็บ `engine_code`, `engine_displacement`, `fuel_type` ใน Variant โดยตรง
ไม่สร้าง Engine model แยก

### Context
EPC Spec ต้องการ `itx_info_vehicle.engine` model แยก แต่เราตัดสินใจไม่ทำ

### Rationale

**Option A: เก็บใน Variant (เลือกใช้)**
```
Variant
├── engine_code = "2KD-FTV"
├── engine_displacement = 2.5
└── fuel_type = diesel
```

**Option B: แยก Engine Model (EPC Spec)**
```
Engine                      Variant
├── code = "2KD"      →     └── engine_id
├── displacement_cc
└── fuel_type
```

**เหตุผลเลือก Option A:**

1. **User กรอกง่าย** - ฟอร์มเดียวจบ ไม่ต้องสร้าง Engine ก่อน
2. **เหมาะกับ Use Case** - Salvage Parts สนใจ "รถคันนี้ ติดเครื่องอะไร"
3. **ค่อยๆ เพิ่ม Variant** - เพิ่มเท่าที่ใช้ ไม่ต้อง populate ทุกรุ่น
4. **EPC อนาคต** - ถ้าต้อง map จริง เพิ่ม `engine_id` ทีหลังได้

### Date
2026-03-30

---

## 5. Variant ต้องมีอย่างน้อย 1 ตัว

### Decision
ทุก Generation ต้องมี Variant อย่างน้อย 1 record

### Context
Hierarchy: Brand → Model → Generation → Variant
ถ้า Generation ไม่มี Variant จะเลือกไม่ได้ตอนสร้าง Product

### Rationale

```
การเลือกรถสำหรับ Product:
Brand → Model → Generation → Variant (ต้องเลือก!)
                              ↑
                              ถ้าไม่มี = ไม่สามารถ specify รถได้ครบ
```

**ตัวอย่าง:**

| Generation | Variants | OK? |
|------------|----------|-----|
| Civic Gen 8 FD | 1.8S, 1.8E, 2.0EL | ✅ หลายตัว |
| CR-V Gen 5 | 2.4 EL 4WD | ✅ ตัวเดียวก็ได้ |
| Hilux Vigo | (ไม่มี) | ❌ ใช้งานไม่ได้! |

**กรณีไม่รู้ Variant เฉพาะ:**
- สร้าง Variant ชื่อ "Standard" หรือ "Base" เป็น default

### Implications
- UI ควร validate ว่า Generation มี Variant
- หรือ auto-create "Base" variant ถ้าไม่มี

### Date
2026-03-30

---

## 6. Lookup Tables Namespace `adm`

### Decision
Lookup/Master tables ใช้ namespace `itx.info.vehicle.adm.*`

### Context
แยก lookup tables ออกจาก core vehicle hierarchy

### Rationale

```
Core Hierarchy:
  itx.info.vehicle.brand
  itx.info.vehicle.model
  itx.info.vehicle.generation
  itx.info.vehicle.variant

Lookup/Admin Tables:
  itx.info.vehicle.adm.body_type
  itx.info.vehicle.adm.xxx (อื่นๆ ถ้ามี)
```

**เหตุผล:**
1. **แยกชัดเจน** - core vs lookup
2. **จัดการง่าย** - รู้ว่า `adm.*` เป็น master data ที่ต้อง populate
3. **Menu แยกได้** - Configuration → Admin Tables

### Current `adm` Tables

| Model | Purpose |
|-------|---------|
| `itx.info.vehicle.adm.body_type` | ประเภทตัวถัง |

### Potential Future `adm` Tables (ถ้าต้องการ)

| Model | Current | Decision |
|-------|---------|----------|
| `adm.fuel_type` | Selection in Variant | Keep as Selection (พอแล้ว) |
| `adm.transmission` | Selection in Variant | Keep as Selection |
| `adm.drivetrain` | Selection in Variant | Keep as Selection |

### Date
2026-03-30

---

## Summary: Field Location Matrix

| Field | Model | Generation | Variant | Reason |
|-------|-------|------------|---------|--------|
| `body_type_id` | ❌ | ❌ | ✅ | 1 variant = 1 body |
| `year` | ❌ | range | ❌ | variant = master data |
| `engine_code` | ❌ | ❌ | ✅ | simple, direct |
| `engine_displacement` | ❌ | ❌ | ✅ | simple, direct |
| `fuel_type` | ❌ | ❌ | ✅ | per variant spec |
| `transmission` | ❌ | ❌ | ✅ | per variant spec |
| `drive_type` | ❌ | ❌ | ✅ | per variant spec |

---

---

## 7. Vehicle Scope (รถที่รองรับ)

### Decision
ระบบรองรับรถยนต์และรถบรรทุก ไม่รองรับรถจักรยานยนต์

### Scope

| ประเภท | รองรับ | หมายเหตุ |
|--------|--------|---------|
| รถเก๋ง (Sedan, Hatchback) | ✅ | |
| SUV, Crossover | ✅ | |
| Pickup (Single/Extra/Double Cab) | ✅ | |
| รถ EV | ✅ | เพิ่ม `direct` transmission |
| รถ 6 ล้อ | ✅ | เพิ่ม `6x2`, `6x4` drivetrain |
| รถ 10 ล้อ / หัวลาก | ✅ | เพิ่ม `8x4`, `10x4`, `tractor` body |
| รถจักรยานยนต์ | ❌ | ไม่รองรับ |

### Date
2026-03-30

---

## 8. Selection Values (Final)

### Decision
กำหนดค่า Selection สำหรับ Transmission, Drivetrain และ Fuel Type

### 8.1 Transmission Selection

```python
TRANSMISSION_SELECTION = [
    ('mt', 'MT (Manual)'),
    ('at', 'AT (Automatic)'),
    ('cvt', 'CVT'),
    ('dct', 'DCT (Dual Clutch)'),
    ('amt', 'AMT (Automated Manual)'),
    ('direct', 'Direct Drive (EV)'),      # สำหรับรถ EV
]
```

### 8.2 Drivetrain Selection

```python
DRIVETRAIN_SELECTION = [
    # รถเก๋ง / SUV / Pickup
    ('fwd', 'FWD (ขับหน้า)'),
    ('rwd', 'RWD (ขับหลัง)'),
    ('awd', 'AWD (ขับ 4 ล้ออัตโนมัติ)'),
    ('4x2', '4x2 (2WD)'),
    ('4x4', '4x4 (4WD)'),
    # รถบรรทุก 6-10 ล้อ
    ('6x2', '6x2 (6 ล้อ ขับ 2)'),
    ('6x4', '6x4 (6 ล้อ ขับ 4)'),
    ('8x4', '8x4 (8 ล้อ ขับ 4)'),
    ('10x4', '10x4 (10 ล้อ ขับ 4)'),
]
```

### 8.3 Fuel Type Selection

```python
FUEL_TYPE_SELECTION = [
    ('gasoline', 'Gasoline (เบนซิน)'),
    ('diesel', 'Diesel (ดีเซล)'),
    ('hybrid', 'Hybrid'),
    ('phev', 'PHEV (Plug-in Hybrid)'),
    ('ev', 'EV (Electric)'),
    ('lpg', 'LPG'),
    ('cng', 'CNG'),
]
```

### Date
2026-03-30

---

## 9. Body Type Values (adm.body_type)

### Decision
Body Type เป็น Master Table (`itx.info.vehicle.adm.body_type`) รองรับทั้งรถเก๋งและรถบรรทุก

### Values

```
# รถเก๋ง / SUV / Pickup
sedan          - รถเก๋ง 4 ประตู
hatchback      - รถเก๋ง 5 ประตู
coupe          - รถเก๋ง 2 ประตู
wagon          - รถเก๋งแวน
suv            - SUV
crossover      - Crossover
van            - Van / MPV
pickup         - Pickup (ทั่วไป)
single_cab     - Pickup กระบะ (Single Cab)
extra_cab      - Pickup แค็บ (Extra Cab)
double_cab     - Pickup 4 ประตู (Double Cab)

# รถบรรทุก
tractor        - หัวลาก (Tractor Head)
rigid_truck    - รถบรรทุกตู้ติด
dump_truck     - รถดั้ม
mixer          - รถโม่ปูน
tanker         - รถบรรทุกของเหลว
cargo_truck    - รถบรรทุกทั่วไป
```

### Rationale
- ใช้ Master Table เพราะมี 15+ ค่า และอาจเพิ่มได้
- รองรับทั้งรถเก๋งและรถบรรทุกใน table เดียว

### Date
2026-03-30

---

## 10. Lookup Tables (`mgr.*`)

### Decision
ใช้ namespace `mgr` (Manager) แทน `adm` (Admin) สำหรับ lookup tables

### Rationale
- `mgr` = ผู้จัดการฝ่ายสินค้า/คลัง ดูแล (business master data)
- `adm` = IT Admin ดูแล (system config)
- Body type, Engine เป็น business data → `mgr` เหมาะกว่า

### Lookup Tables

| Model | Purpose | ทำไมต้อง Lookup |
|-------|---------|-----------------|
| `itx.info.vehicle.mgr.body_type` | ประเภทตัวถัง | 17+ ค่า, เพิ่มได้ |
| `itx.info.vehicle.mgr.engine` | รหัสเครื่องยนต์ | ป้องกัน typo (2L, 2l, 2 L) |

### Fields ที่ยังใช้ Selection

| Field | เหตุผล |
|-------|--------|
| `fuel_type` | ค่าจำกัด ไม่เปลี่ยน |
| `transmission` | ค่าจำกัด |
| `drivetrain` | ค่าจำกัด |

### Date
2026-03-30

---

## 12. Product Part Fields Location

### Decision
`part_origin` และ `condition` อยู่ใน `product.template` (ไม่ใช่ product.product variant)

### Context
ถ้าใช้ Odoo variant system (product.attribute) จะ auto-create 3×4=12 variants ต่อ template

### Rationale
- Salvage parts สร้างเฉพาะที่มีของจริง
- ไม่ต้องการ empty variants
- แต่ละชิ้นอะไหล่ที่รับเข้ามา = 1 product.template

### Date
2026-03-30

---

## 13. Product Unique Key

### Decision
Unique key ของ Vehicle Part ประกอบด้วย **6 fields** (รวม name):

```python
_sql_constraints = [
    ('vehicle_part_uniq',
     'UNIQUE(itx_variant_id, itx_part_category_id, name, itx_part_origin, itx_condition, itx_oem_part_number)',
     'Part with same vehicle, category, name, origin, condition and OEM part number already exists!')
]
```

### Key Components

| # | Field | ตัวอย่าง | Required | เหตุผล |
|---|-------|---------|----------|--------|
| 1 | `itx_variant_id` | Hilux Vigo 3.0G | ✅ | รถต่างกัน = part ต่างกัน |
| 2 | `itx_part_category_id` | Headlight | ✅ | หมวดอะไหล่ |
| 3 | `name` | ไฟหน้าซ้าย | ✅ | **พนักงานรู้ทันที** (ซ้าย/ขวา) |
| 4 | `itx_part_origin` | OEM | ✅ | แท้/เทียม ราคาต่างกัน |
| 5 | `itx_condition` | Like New | ✅ | สภาพต่างกัน ราคาต่างกัน |
| 6 | `itx_oem_part_number` | 81130-0K140 | ❌ Optional | เติมทีหลังได้ |

### Context
ระบบนี้เป็น **user-friendly** สำหรับพนักงานคลัง:
- พนักงานแกะซากรถ รู้ทันทีว่า "ไฟหน้าซ้าย" หรือ "ไฟหน้าขวา"
- ไม่ต้องเปิดหนังสือหา OEM Part Number ตอนรับเข้า
- OEM Part Number เติมทีหลังได้ (optional)
- ระบบต้อง trace back ได้ แต่ไม่บังคับข้อมูล engineering ตั้งแต่แรก

### Example

```
ไฟหน้าซ้าย + Hilux Vigo + OEM + Like New + NULL      → Record 1 (ยังไม่รู้ OEM)
ไฟหน้าขวา + Hilux Vigo + OEM + Like New + NULL      → Record 2 (ยังไม่รู้ OEM)
ไฟหน้าซ้าย + Hilux Vigo + OEM + Like New + 81130-0K140 → Record 1 (update OEM ทีหลัง)
```

### Date
2026-03-30

---

## 14. Part Origin & Condition Values

### Decision
แยก 2 fields สำหรับจัดการสภาพอะไหล่

### 14.1 Part Origin (ที่มา)

```python
PART_ORIGIN_SELECTION = [
    ('oem', 'OEM (แท้)'),
    ('aftermarket', 'Aftermarket (เทียม)'),
    ('reconditioned', 'Reconditioned (รีบิ้วท์)'),
]
```

### 14.2 Condition (สภาพ)

```python
CONDITION_SELECTION = [
    ('new', 'New (มือหนึ่ง)'),
    ('like_new', 'Like New (มือสองสภาพใหม่)'),
    ('good', 'Good (ใช้งานได้ดี)'),
    ('fair', 'Fair (ต้องซ่อม/ปรับแต่ง)'),
]
```

### Rationale
- แยก 2 fields ยืดหยุ่นกว่ารวม 1 field
- รวมกัน = 3×4 = 12 combinations (เยอะเกินถ้าเป็น 1 dropdown)
- สามารถ filter/group by แยกได้

### Date
2026-03-30

---

## 11. Implementation Plan - MGR Tables

### Step 1: สร้าง Models

```python
# models/mgr_body_type.py
class ItxInfoVehicleMgrBodyType(models.Model):
    _name = 'itx.info.vehicle.mgr.body_type'
    _description = 'Vehicle Body Type'
    _order = 'sequence, name'

    name = fields.Char(required=True)           # "Double Cab"
    code = fields.Char(required=True)           # "double_cab"
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    _sql_constraints = [('code_uniq', 'unique(code)', 'Code must be unique')]

# models/mgr_engine.py
class ItxInfoVehicleMgrEngine(models.Model):
    _name = 'itx.info.vehicle.mgr.engine'
    _description = 'Vehicle Engine'
    _order = 'name'

    name = fields.Char(required=True)           # "2KD-FTV"
    code = fields.Char(required=True)           # "2KD"
    displacement = fields.Float(digits=(4,1))   # 2.5
    fuel_type = fields.Selection([...])         # diesel, gasoline, etc.
    active = fields.Boolean(default=True)

    _sql_constraints = [('code_uniq', 'unique(code)', 'Code must be unique')]
```

### Step 2: แก้ Variant

```python
# เพิ่ม fields
body_type_id = fields.Many2one('itx.info.vehicle.mgr.body_type')
engine_id = fields.Many2one('itx.info.vehicle.mgr.engine')

# ลบ fields เดิม (ถ้ามี)
# - engine_code → ใช้ engine_id.name
# - engine_displacement → ใช้ engine_id.displacement
```

### Step 3: ลบ body_type จาก Model

### Step 4: สร้าง Views + Menu

### Step 5: สร้าง Master Data (CSV/XML)

### Date
2026-03-30

---

## Change Log

| Date | Decision | Author |
|------|----------|--------|
| 2026-03-30 | Initial decisions documented | Claude + Owner |
| 2026-03-30 | Added Vehicle Scope (6-10 wheel trucks) | Claude + Owner |
| 2026-03-30 | Finalized Selection values | Claude + Owner |
| 2026-03-30 | Defined Body Type values | Claude + Owner |
| 2026-03-30 | Changed namespace `adm` → `mgr` | Claude + Owner |
| 2026-03-30 | Added `mgr.engine` lookup table | Claude + Owner |
| 2026-03-30 | Part fields on template (not variant) | Claude + Owner |
| 2026-03-30 | Product unique key: 6 fields incl. name (OEM optional) | Claude + Owner |
| 2026-03-30 | Defined part_origin & condition selections | Claude + Owner |

---

*This document should be updated whenever design decisions are made or changed.*
