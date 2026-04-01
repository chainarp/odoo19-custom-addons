# EPC Spec Comparison Report

**Document Type:** GAP Analysis
**Date:** 2026-03-30
**Purpose:** เปรียบเทียบ EPC-Ready Spec กับ Source Code ปัจจุบัน

---

## Executive Summary

| Category | Status |
|----------|--------|
| Models ครบ | ❌ ขาด Engine model |
| Variant fields | ❌ ต่างจาก spec มาก |
| Selection values | ⚠️ ต่างบางส่วน |
| Constraints | ❌ ขาด |
| Extra features | ⚠️ มี part_category, product inherit |

---

## 1. Model Comparison

### 1.1 Models ที่ต้องมีตาม EPC Spec

| # | Model | EPC Spec | ปัจจุบัน | Status |
|---|-------|----------|---------|--------|
| 1 | `itx_info_vehicle.brand` | ✅ | ✅ | OK (มี fields เพิ่ม) |
| 2 | `itx_info_vehicle.model` | ✅ | ✅ | OK (มี fields เพิ่ม) |
| 3 | `itx_info_vehicle.generation` | ✅ | ✅ | OK |
| 4 | `itx_info_vehicle.engine` | ✅ | ❌ | **MISSING** |
| 5 | `itx_info_vehicle.variant` | ✅ | ✅ | ⚠️ Fields ต่าง |

### 1.2 Models ที่มีเพิ่มเติม (ไม่อยู่ใน EPC Spec)

| # | Model | Purpose | Decision Needed |
|---|-------|---------|-----------------|
| 1 | `itx.info.vehicle.part.category` | ประเภทอะไหล่ | Keep for Phase 2? |
| 2 | `product.template` (inherit) | Product integration | Keep for Phase 2? |

---

## 2. Field-by-Field Comparison

### 2.1 itx_info_vehicle.brand

| Field | EPC Spec | ปัจจุบัน | Status |
|-------|----------|---------|--------|
| `name` | Char, required | Char, required | ✅ Match |
| `code` | Char | Char, required | ✅ Match (stricter) |
| `active` | Boolean, default=True | Boolean, default=True | ✅ Match |
| `desc` | - | Text | ⚠️ Extra |
| `abbr` | - | Char(10), required | ⚠️ Extra |
| `country_id` | - | Many2one res.country | ⚠️ Extra |
| `logo` | - | Image | ⚠️ Extra |
| `model_ids` | - | One2many | ⚠️ Extra (useful) |
| `model_count` | - | Integer, computed | ⚠️ Extra |

### 2.2 itx_info_vehicle.model

| Field | EPC Spec | ปัจจุบัน | Status |
|-------|----------|---------|--------|
| `name` | Char, required | Char, required | ✅ Match |
| `code` | Char | Char, required | ✅ Match |
| `brand_id` | Many2one, required | Many2one, required | ✅ Match |
| `active` | Boolean, default=True | Boolean, default=True | ✅ Match |
| `body_type` | - | Selection | ⚠️ Extra (ควรย้ายไป Variant) |
| `desc` | - | Text | ⚠️ Extra |
| `abbr` | - | Char(10), required | ⚠️ Extra |
| `generation_ids` | - | One2many | ⚠️ Extra (useful) |
| `generation_count` | - | Integer, computed | ⚠️ Extra |
| `full_name` | - | Char, computed | ⚠️ Extra |

### 2.3 itx_info_vehicle.generation

| Field | EPC Spec | ปัจจุบัน | Status |
|-------|----------|---------|--------|
| `name` | Char, required | Char, required | ✅ Match |
| `code` | Char | Char, required | ✅ Match |
| `model_id` | Many2one, required | Many2one, required | ✅ Match |
| `year_start` | Integer | Integer | ✅ Match |
| `year_end` | Integer | Integer, default=0 | ✅ Match |
| `active` | Boolean, default=True | Boolean, default=True | ✅ Match |
| `desc` | - | Text | ⚠️ Extra |
| `abbr` | - | Char(10), required | ⚠️ Extra |
| `chassis_code` | - | Char | ⚠️ Extra (useful) |
| `brand_id` | - | Many2one, related | ⚠️ Extra (useful) |
| `variant_ids` | - | One2many | ⚠️ Extra (useful) |
| `variant_count` | - | Integer, computed | ⚠️ Extra |
| `full_name` | - | Char, computed | ⚠️ Extra |
| `year_range` | - | Char, computed | ⚠️ Extra |

### 2.4 itx_info_vehicle.engine (MISSING)

**EPC Spec ต้องการ:**

```python
class ItxInfoVehicleEngine(models.Model):
    _name = 'itx_info_vehicle.engine'

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

**ปัจจุบัน:** ❌ ไม่มี model นี้ - เก็บ engine_code, engine_displacement ใน Variant โดยตรง

### 2.5 itx_info_vehicle.variant (Core Differences)

| Field | EPC Spec | ปัจจุบัน | Status |
|-------|----------|---------|--------|
| `name` | Char, required | Char, required | ✅ Match |
| `brand_id` | Many2one, **required** | Many2one, **related** | ❌ Different |
| `model_id` | Many2one, **required** | Many2one, **related** | ❌ Different |
| `generation_id` | Many2one, required | Many2one, required | ✅ Match |
| `year` | Integer, **required** | - | ❌ **MISSING** |
| `engine_id` | Many2one, **required** | - | ❌ **MISSING** |
| `transmission` | Selection, **required** | Selection, optional | ⚠️ Should be required |
| `drivetrain` | Selection, **required** | - | ❌ **MISSING** |
| `body_type` | Selection, **required** | - (in Model) | ❌ **MISSING** |
| `fuel_type` | Selection | Selection | ✅ Match |
| `has_abs` | Boolean | - | ❌ **MISSING** |
| `has_airbag` | Boolean | - | ❌ **MISSING** |
| `vin` | Char | - | ❌ **MISSING** |
| `code` | - | Char, required | ⚠️ Extra |
| `abbr` | - | Char(10), required | ⚠️ Extra |
| `desc` | - | Text | ⚠️ Extra |
| `engine_code` | - | Char | ⚠️ Extra (should be in Engine) |
| `engine_displacement` | - | Float | ⚠️ Extra (should be in Engine) |
| `drive_type` | - | Selection | ⚠️ Extra (different from drivetrain) |
| `full_name` | - | Char, computed | ⚠️ Extra |

---

## 3. Selection Values Comparison

### 3.1 Transmission

| EPC Spec Value | EPC Label | Current Value | Current Label | Status |
|----------------|-----------|---------------|---------------|--------|
| `mt` | Manual | `manual` | Manual (MT) | ❌ Value differs |
| `at` | Automatic | `auto` | Automatic (AT) | ❌ Value differs |
| `cvt` | CVT | `cvt` | CVT | ✅ Match |
| - | - | `dct` | Dual Clutch (DCT) | ⚠️ Extra |
| - | - | `amt` | Automated Manual (AMT) | ⚠️ Extra |
| - | - | `other` | Other | ⚠️ Extra |

### 3.2 Drivetrain (EPC) vs Drive Type (Current)

| EPC Spec Value | EPC Label | Current Value | Current Label | Status |
|----------------|-----------|---------------|---------------|--------|
| `4x2` | 4x2 | - | - | ❌ **MISSING** |
| `4x4` | 4x4 | `4wd` | 4WD (Four-wheel Drive) | ❌ Different |
| `fwd` | FWD | `ff` | FF (Front-wheel Drive) | ❌ Different |
| `rwd` | RWD | `fr` | FR (Rear-wheel Drive) | ❌ Different |
| - | - | `awd` | AWD (All-wheel Drive) | ⚠️ Extra |
| - | - | `rr` | RR (Rear Engine, Rear Drive) | ⚠️ Extra |
| - | - | `mr` | MR (Mid Engine, Rear Drive) | ⚠️ Extra |

### 3.3 Body Type

**EPC Spec (ควรอยู่ใน Variant):**

| Value | Label |
|-------|-------|
| `single_cab` | Single Cab |
| `extra_cab` | Extra Cab |
| `double_cab` | Double Cab |
| `sedan` | Sedan |
| `hatchback` | Hatchback |
| `suv` | SUV |

**Current (อยู่ใน Model):**

| Value | Label |
|-------|-------|
| `sedan` | Sedan |
| `hatchback` | Hatchback |
| `suv` | SUV |
| `crossover` | Crossover |
| `pickup` | Pickup Truck |
| `van` | Van/MPV |
| `coupe` | Coupe |
| `convertible` | Convertible |
| `wagon` | Wagon |
| `truck` | Truck |
| `other` | Other |

### 3.4 Fuel Type

| EPC Spec Value | EPC Label | Current Value | Current Label | Status |
|----------------|-----------|---------------|---------------|--------|
| `diesel` | Diesel | `diesel` | Diesel | ✅ Match |
| `gasoline` | Gasoline | `gasoline` | Gasoline | ✅ Match |
| `hybrid` | Hybrid | `hybrid` | Hybrid | ✅ Match |
| - | - | `phev` | Plug-in Hybrid | ⚠️ Extra |
| - | - | `ev` | Electric (EV) | ⚠️ Extra |
| - | - | `lpg` | LPG | ⚠️ Extra |
| - | - | `cng` | CNG | ⚠️ Extra |
| - | - | `other` | Other | ⚠️ Extra |

---

## 4. Constraints Comparison

### 4.1 EPC Spec Required Constraints

| Constraint | Description | ปัจจุบัน | Status |
|------------|-------------|---------|--------|
| generation.model_id = model_id | Generation ต้องตรงกับ Model | ❌ ไม่มี | **MISSING** |
| model.brand_id = brand_id | Model ต้องตรงกับ Brand | ❌ ไม่มี | **MISSING** |
| year in generation range | Year ต้องอยู่ในช่วง year_start-year_end | ❌ ไม่มี | **MISSING** |
| engine.fuel_type ~ fuel_type | Fuel type ควรสอดคล้อง | ❌ ไม่มี | **MISSING** |

### 4.2 Current Constraints

| Model | Constraint | Type |
|-------|------------|------|
| Brand | code unique | SQL |
| Brand | abbr unique | SQL |
| Model | code+brand_id unique | SQL |
| Model | abbr+brand_id unique | SQL |
| Generation | code+model_id unique | SQL |
| Generation | year_end >= year_start | Python |
| Variant | code+generation_id unique | SQL |
| Variant | engine_displacement > 0 | Python |
| Part Category | code unique | SQL |
| Part Category | abbr unique | SQL |
| Part Category | no recursion | Python |

---

## 5. Extra Features (Not in EPC Spec)

### 5.1 Part Category Model

```python
# itx.info.vehicle.part.category
- Hierarchical categories (parent_id, child_ids)
- Complete name computed
- Used for Internal Reference generation
```

**Decision:** Keep for Part Management (Phase 2)?

### 5.2 Product Template Integration

```python
# product.template (inherit)
- itx_is_vehicle_part (Boolean)
- itx_brand_id, itx_model_id, itx_generation_id, itx_variant_id
- itx_part_category_id
- itx_oem_part_number, itx_condition_grade, itx_sequence
- Auto-generate Internal Reference (default_code)
```

**Decision:** Keep for Inventory Integration (Phase 2)?

### 5.3 Abbreviation System (abbr fields)

ทุก model มี `abbr` field สำหรับสร้าง Internal Reference:
```
Format: {brand.abbr}-{model.abbr}-{gen.abbr}-{variant.abbr}-{part_cat.abbr}-{seq}
Example: HON-CIV-FD-1.8S-ENG-00001
```

**Decision:** EPC Spec ไม่ต้องการ - ลบหรือเก็บไว้?

---

## 6. Action Items

### Priority 1: Critical (Must Fix)

| # | Action | Impact |
|---|--------|--------|
| 1 | สร้าง `itx_info_vehicle.engine` model | High |
| 2 | เพิ่ม `year` field ใน Variant (required) | High |
| 3 | เพิ่ม `engine_id` Many2one ใน Variant | High |
| 4 | เพิ่ม `drivetrain` Selection ใน Variant | High |
| 5 | ย้าย `body_type` จาก Model → Variant | High |

### Priority 2: Important

| # | Action | Impact |
|---|--------|--------|
| 6 | เปลี่ยน `brand_id`, `model_id` ใน Variant จาก related → direct Many2one | Medium |
| 7 | เพิ่ม `has_abs`, `has_airbag`, `vin` fields | Medium |
| 8 | แก้ Selection values ให้ตรง EPC spec | Medium |
| 9 | เพิ่ม cascading constraints | Medium |

### Priority 3: Nice to Have

| # | Action | Impact |
|---|--------|--------|
| 10 | ลบ fields ที่เกิน (code, abbr, desc) ถ้าไม่จำเป็น | Low |
| 11 | Refactor Selection values | Low |

---

## 7. Questions for Decision

1. **Extra fields (abbr, desc, etc.):** เก็บไว้สำหรับ Internal Reference หรือลบ?
2. **Part Category:** เก็บไว้สำหรับ Phase 2 หรือลบ?
3. **Product Integration:** เก็บไว้สำหรับ Phase 2 หรือลบ?
4. **Selection values:** ใช้ค่าตาม EPC Spec หรือเก็บค่าปัจจุบัน?
5. **body_type location:** ย้ายจาก Model ไป Variant หรือมีทั้งสองที่?

---

## 8. Summary Table

| Aspect | EPC Spec | Current | Gap |
|--------|----------|---------|-----|
| Total Models | 5 | 6 (+1 extra) | +1 part_category |
| Engine Model | Required | Missing | **Critical** |
| Variant Fields | 13 | 12 | **Different** |
| Required Fields | year, engine_id, drivetrain, body_type | Missing | **Critical** |
| Transmission Values | mt/at/cvt | manual/auto/cvt/dct/amt | Different |
| Drivetrain Values | 4x2/4x4/fwd/rwd | ff/fr/awd/4wd/rr/mr | Different |
| Constraints | 4 cascading | 0 cascading | **Missing** |

---

## 9. Decisions Made (2026-03-30)

การตัดสินใจที่ได้ข้อสรุปแล้ว (ดูรายละเอียดใน [DESIGN_DECISIONS.md](./DESIGN_DECISIONS.md)):

| Item | EPC Spec | Decision | Reason |
|------|----------|----------|--------|
| Engine Model | แยก model | ❌ ไม่ทำ | เก็บใน Variant ง่ายกว่า, user กรอกฟอร์มเดียว |
| `year` in Variant | required | ❌ ไม่เพิ่ม | Variant = master data, year อยู่ใน Generation (range) |
| `body_type` | in Variant | ✅ เพิ่ม | 1 variant = 1 body type, ใช้ Many2one to `adm.body_type` |
| Body Type location | - | Variant | ไม่ใช่ Model/Generation เพราะ 1 gen มีหลาย body ได้ |
| Variant minimum | - | ต้องมี 1+ | ทุก Generation ต้องมี Variant อย่างน้อย 1 ตัว |
| Lookup namespace | - | `adm.*` | แยก lookup tables: `itx.info.vehicle.adm.body_type` |

### Updated Action Items

| # | Action | Original Priority | New Status |
|---|--------|-------------------|------------|
| 1 | สร้าง `itx_info_vehicle.engine` model | Critical | ❌ **ไม่ทำ** - เก็บใน Variant |
| 2 | เพิ่ม `year` field ใน Variant | Critical | ❌ **ไม่ทำ** - ใช้ Generation range |
| 3 | เพิ่ม `body_type_id` ใน Variant | Critical | ✅ **ทำ** - Many2one to `adm.body_type` |
| 4 | สร้าง `itx.info.vehicle.adm.body_type` | - | ✅ **ทำ** - Lookup table |
| 5 | เพิ่ม `drivetrain` Selection ใน Variant | High | ⏳ Pending review |

---

*Document created: 2026-03-30*
*Last updated: 2026-03-30*
*Author: Claude Code Assistant*
