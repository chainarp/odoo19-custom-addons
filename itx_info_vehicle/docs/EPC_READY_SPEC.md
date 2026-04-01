# SPEC: Vehicle Spec Module (EPC-Ready) for Odoo

**Document Type:** Requirements Specification
**Date:** 2026-03-30
**Source:** Project Owner
**Purpose:** Target specification for EPC (Electronic Parts Catalog) integration

---

## Objective

สร้างโมดูล `itx_info_vehicle` เพื่อเก็บ "Vehicle Spec" แบบ **normalized**
ให้สามารถ:

* ใช้ค้นหา/กรองรถได้จากมุมผู้ใช้ (ช่าง)
* พร้อมนำไป map กับ EPC (หา model_code/part) ในอนาคต

---

## Design Principles (สำคัญมาก)

1. **ห้ามใช้ free-text เป็นตัวหลัก** → ใช้ Selection / Many2one
2. **1 field = 1 ความหมาย** (atomic)
3. **มี code สำหรับ map EPC** (แม้ยังไม่ใช้ตอนนี้)
4. **User-friendly label + System code แยกกัน**
5. **รองรับการเพิ่มค่าใหม่ได้ (extendable)**

---

## Data Model (หลัก)

### 1) itx_info_vehicle.brand

```python
name = fields.Char(required=True)        # "Toyota"
code = fields.Char()                     # "TOYOTA"
active = fields.Boolean(default=True)
```

---

### 2) itx_info_vehicle.model

```python
name = fields.Char(required=True)        # "Hilux"
code = fields.Char()                     # "HILUX"
brand_id = fields.Many2one('itx_info_vehicle.brand', required=True)
active = fields.Boolean(default=True)
```

---

### 3) itx_info_vehicle.generation

```python
name = fields.Char(required=True)        # "Vigo"
code = fields.Char()                     # "VIGO"
model_id = fields.Many2one('itx_info_vehicle.model', required=True)

year_start = fields.Integer()            # 2005
year_end = fields.Integer()              # 2015
active = fields.Boolean(default=True)
```

---

### 4) itx_info_vehicle.engine

```python
name = fields.Char(required=True)        # "2KD-FTV"
code = fields.Char(required=True)        # "2KD"
fuel_type = fields.Selection([
    ('diesel', 'Diesel'),
    ('gasoline', 'Gasoline'),
    ('hybrid', 'Hybrid'),
])
displacement_cc = fields.Integer()       # 2500
active = fields.Boolean(default=True)
```

---

### 5) itx_info_vehicle.variant (หัวใจระบบ)

```python
name = fields.Char(required=True)
# เช่น "Vigo 2012 2KD MT 4x2 Double Cab"

brand_id = fields.Many2one('itx_info_vehicle.brand', required=True)
model_id = fields.Many2one('itx_info_vehicle.model', required=True)
generation_id = fields.Many2one('itx_info_vehicle.generation', required=True)

year = fields.Integer(required=True)     # 2012

engine_id = fields.Many2one('itx_info_vehicle.engine', required=True)

transmission = fields.Selection([
    ('mt', 'Manual'),
    ('at', 'Automatic'),
    ('cvt', 'CVT'),
], required=True)

drivetrain = fields.Selection([
    ('4x2', '4x2'),
    ('4x4', '4x4'),
    ('fwd', 'FWD'),
    ('rwd', 'RWD'),
], required=True)

body_type = fields.Selection([
    ('single_cab', 'Single Cab'),
    ('extra_cab', 'Extra Cab'),
    ('double_cab', 'Double Cab'),
    ('sedan', 'Sedan'),
    ('hatchback', 'Hatchback'),
    ('suv', 'SUV'),
], required=True)

fuel_type = fields.Selection([
    ('diesel', 'Diesel'),
    ('gasoline', 'Gasoline'),
    ('hybrid', 'Hybrid'),
])

# Optional (Refinement)
has_abs = fields.Boolean()
has_airbag = fields.Boolean()

# Future EPC (ยังไม่ใช้ แต่ต้องมีไว้)
vin = fields.Char()                      # 17 chars
```

---

## Constraints (สำคัญ)

* generation.model_id ต้องตรงกับ model_id
* model.brand_id ต้องตรงกับ brand_id
* year ต้องอยู่ในช่วง generation (ถ้ามี)
* engine.fuel_type ควรสอดคล้องกับ fuel_type (ถ้ามี)

---

## Normalization Rules (ห้ามพลาด)

### ห้ามเก็บแบบนี้

```text
"เครื่อง 2.5 ดีเซล เกียร์ธรรมดา"
```

### ต้องเก็บแยก field

```text
engine = 2KD
fuel_type = diesel
transmission = MT
```

---

## UI/UX (สำหรับผู้ใช้)

### Form: Vehicle Variant

* Brand → Model → Generation (cascade)
* Year (input)
* Engine (dropdown)
* Transmission (dropdown)
* Drivetrain (dropdown)
* Body Type (dropdown)

**Optional:**

* ABS checkbox
* Airbag checkbox

---

## Search Behavior

ผู้ใช้สามารถค้นโดย:

* Brand + Model + Year
* Engine
* Drivetrain

ระบบต้อง filter variant ได้

---

## Example Data

### Input (User)

```text
Toyota
Hilux
Vigo
2012
2KD
MT
4x2
Double Cab
```

### Stored Variant

```text
name: "Vigo 2012 2KD MT 4x2 Double Cab"
engine.code: 2KD
drivetrain: 4x2
body_type: double_cab
```

---

## Future (EPC Integration)

เมื่อมี EPC:

```text
Variant → (map spec) → EPC query → model_code → part list
```

---

## Common Mistakes (ห้ามทำ)

1. ใช้ free-text เยอะ
2. รวมหลาย spec ใน field เดียว
3. ไม่ normalize engine / drivetrain
4. ไม่เผื่อ field สำหรับ EPC (เช่น VIN)

---

## Summary

* Variant = ชุดของ Spec
* Spec ต้องเป็น code / structured
* ระบบนี้ = "EPC Input Layer"

---

*Document saved: 2026-03-30*
