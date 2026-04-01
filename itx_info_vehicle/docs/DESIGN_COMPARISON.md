# Design Comparison — Original vs Prototype A

**Purpose:** เปรียบเทียบ Original Design Document กับ Prototype A Specification
**Date:** 2026-03-26

---

## Summary of Differences

| Aspect | Original Design | Prototype A (Claude) | Status |
|--------|-----------------|---------------------|--------|
| Total Models | 9 models | 6 models | Prototype A = subset |
| Platform model | Yes | No | Deferred to Phase 2 |
| Compatibility model | Yes | No | Deferred to Phase 2 |
| Salvage Car model | Yes | No | Deferred to Phase 2 |
| MRP Integration | Yes | No | Deferred to Phase 2 |
| Standard fields (code, abbr) | No | Yes | **NEW in Prototype A** |
| Internal Reference auto-gen | No | Yes | **NEW in Prototype A** |
| Sequence (running number) | No | Yes | **NEW in Prototype A** |

---

## Models Comparison

### Included in Both

| # | Model | Original | Prototype A | Notes |
|---|-------|----------|-------------|-------|
| 1 | Brand | `itx_info_vehicle_brand` | Same | +code, +abbr, +description |
| 2 | Model | `itx_info_vehicle_model` | Same | +code, +abbr, +description, +full_name |
| 3 | Generation | `itx_info_vehicle_generation` | Same | +code, +abbr, +description, +full_name, -platform_id* |
| 4 | Variant | `itx_info_vehicle_variant` | Same | +code, +abbr, +description, +full_name, -platform_id* |
| 5 | Part Category | `itx_info_vehicle_part_category` | Same | +code, +abbr, +description |
| 6 | Product Template | `product.template` (inherit) | Same | Different field set |

### Only in Original Design (Phase 2)

| # | Model | Purpose | Phase |
|---|-------|---------|-------|
| 7 | Platform | `itx_info_vehicle_platform` | Cross-compatibility | Phase 2 |
| 8 | Compatibility | `itx_info_vehicle_compatibility` | Compatibility Matrix | Phase 2 |
| 9 | Salvage Car | `itx_info_vehicle_salvage_car` | Track salvage source | Phase 2 |
| 10 | BOM Line | `mrp.bom.line` (inherit) | Cost allocation | Phase 2 |

---

## Field Differences by Model

### 1. itx_info_vehicle_brand

| Field | Original | Prototype A | Decision |
|-------|----------|-------------|----------|
| name | Yes | Yes | Keep |
| country_id | Yes | Yes | Keep |
| logo | Yes | Yes | Keep |
| active | Yes | Yes | Keep |
| model_ids | Yes | Yes | Keep |
| **code** | No | **Yes** | **ADD** - รหัสตามตลาด |
| **abbr** | No | **Yes** | **ADD** - ตัวย่อ Internal Ref |
| **description** | No | **Yes** | **ADD** - คำอธิบาย |
| **model_count** | No | **Yes** | **ADD** - computed |

### 2. itx_info_vehicle_model

| Field | Original | Prototype A | Decision |
|-------|----------|-------------|----------|
| name | Yes | Yes | Keep |
| brand_id | Yes | Yes | Keep |
| body_type | Yes | Yes | Keep |
| active | Yes | Yes | Keep |
| generation_ids | Yes | Yes | Keep |
| **code** | No | **Yes** | **ADD** |
| **abbr** | No | **Yes** | **ADD** |
| **description** | No | **Yes** | **ADD** |
| **full_name** | No | **Yes** | **ADD** - computed |
| **generation_count** | No | **Yes** | **ADD** - computed |

### 3. itx_info_vehicle_generation

| Field | Original | Prototype A | Decision |
|-------|----------|-------------|----------|
| name | Yes | Yes | Keep |
| model_id | Yes | Yes | Keep |
| chassis_code | Yes | Yes | Keep |
| year_start | Yes | Yes | Keep |
| year_end | Yes | Yes | Keep |
| has_facelift | Yes | **No** | **DEFER** to Phase 2 |
| facelift_year | Yes | **No** | **DEFER** to Phase 2 |
| note | Yes | **No** | Use `description` instead |
| active | Yes | Yes | Keep |
| variant_ids | Yes | Yes | Keep |
| **platform_id** | **Yes** | **No** | **DEFER** - Phase 2 |
| **code** | No | **Yes** | **ADD** |
| **abbr** | No | **Yes** | **ADD** |
| **description** | No | **Yes** | **ADD** |
| **full_name** | No | **Yes** | **ADD** |
| **brand_id** (related) | No | **Yes** | **ADD** |
| **variant_count** | No | **Yes** | **ADD** |

### 4. itx_info_vehicle_variant

| Field | Original | Prototype A | Decision |
|-------|----------|-------------|----------|
| name | Yes | Yes | Keep |
| generation_id | Yes | Yes | Keep |
| engine_code | Yes | Yes | Keep |
| engine_displacement | Yes | Yes | Keep |
| fuel_type | Yes | Yes | Keep |
| transmission | Yes | Yes | Keep |
| drive_type | Yes | Yes | Keep |
| doors | Yes | **No** | **DEFER** - rarely used |
| active | Yes | Yes | Keep |
| brand_id (related) | Yes | Yes | Keep |
| model_id (related) | Yes | Yes | Keep |
| platform_id (related) | Yes | **No** | **DEFER** - Phase 2 |
| year_start (related) | Yes | **No** | Not needed in Prototype |
| year_end (related) | Yes | **No** | Not needed in Prototype |
| **code** | No | **Yes** | **ADD** |
| **abbr** | No | **Yes** | **ADD** |
| **description** | No | **Yes** | **ADD** |
| **full_name** | No | **Yes** | **ADD** |

### 5. itx_info_vehicle_part_category

| Field | Original | Prototype A | Decision |
|-------|----------|-------------|----------|
| name | Yes | Yes | Keep |
| parent_id | Yes | Yes | Keep |
| child_ids | Yes | Yes | Keep |
| complete_name | Yes | Yes | Keep |
| active | Yes | Yes | Keep |
| **code** | No | **Yes** | **ADD** |
| **abbr** | No | **Yes** | **ADD** |
| **description** | No | **Yes** | **ADD** |
| **parent_path** | No | **Yes** | **ADD** - materialized path |

### 6. product.template (inherit)

| Field | Original | Prototype A | Decision |
|-------|----------|-------------|----------|
| itx_is_vehicle_part | Yes | Yes | Keep |
| itx_brand_id | Yes | Yes | Keep |
| itx_model_id | Yes | Yes | Keep |
| itx_generation_id | Yes | Yes | Keep |
| itx_variant_id | Yes | Yes | Keep |
| itx_part_category_id | Yes | Yes | Keep |
| itx_oem_part_number | Yes | Yes | Keep |
| itx_condition_grade | Yes | Yes | Keep |
| **itx_platform_id** | **Yes** | **No** | **DEFER** - Phase 2 |
| **itx_compatible_generation_ids** | **Yes** | **No** | **DEFER** - Phase 2 |
| **itx_salvage_car_id** | **Yes** | **No** | **DEFER** - Phase 2 |
| **itx_sequence** | No | **Yes** | **ADD** - running number |
| **default_code** (computed) | No | **Yes** | **ADD** - Internal Ref |

---

## Key Additions in Prototype A

### 1. Standard Fields (code, name, description, abbr)

**Reason:** สร้าง Internal Reference อัตโนมัติ

```
ทุก Model มี:
- code = รหัสตามตลาดใช้จริง (เช่น HONDA, CIVIC, FD1)
- name = ชื่อแสดง
- description = คำอธิบาย (Text)
- abbr = ตัวย่อ 3-10 ตัวอักษร (auto-gen, แก้ได้)
```

### 2. Internal Reference Auto-Generation

**Format:**
```
{brand.abbr}-{model.abbr}-{gen.abbr}-{variant.abbr}-{part_cat.abbr}-{sequence}

Example: HON-CIV-FD-1.8S-ENG-00001
```

### 3. Sequence (Running Number)

**Feature:**
- Auto-generate ตอนสร้าง product
- แก้ไขได้ (editable)
- ใช้ ir.sequence

---

## Phase Planning

### Phase 1: Prototype A (Current)

**Models:** 6
- Brand, Model, Generation, Variant, Part Category, Product (inherit)

**Features:**
- Vehicle hierarchy (Brand → Model → Generation → Variant)
- Part category hierarchy
- Internal Reference auto-generation
- Standard fields (code, abbr)
- Basic product integration

**Dependencies:**
```python
'depends': ['base', 'product', 'stock']
```

### Phase 2: Full Implementation

**Additional Models:** 4
- Platform
- Compatibility
- Salvage Car
- BOM Line (inherit)

**Additional Features:**
- Platform-based cross-compatibility
- Compatibility Matrix
- Salvage car tracking
- MRP Unbuild integration
- Cost allocation

**Dependencies:**
```python
'depends': ['base', 'product', 'stock', 'mrp', 'sale']
```

---

## Questions for Owner

### Must Decide Before Coding:

1. **Standard fields (code, abbr, description):**
   - ยืนยันว่าต้องการเพิ่ม code, abbr, description ในทุก model ใช่ไหม?
   - Original design ไม่มี fields เหล่านี้

2. **Internal Reference format:**
   - ยืนยัน format: `{brand.abbr}-{model.abbr}-{gen.abbr}-{variant.abbr}-{part_cat.abbr}-{seq}`
   - Original design ไม่มี auto-generation

3. **has_facelift, facelift_year:**
   - Defer ไป Phase 2 หรือใส่ใน Prototype A?

4. **doors field ใน Variant:**
   - Defer ไป Phase 2 หรือใส่ใน Prototype A?

5. **Platform model:**
   - Defer ไป Phase 2 ตามแผน หรือต้องการใน Prototype A?

---

## Recommendation

**ทำ Prototype A ก่อน** ตามที่วางแผนไว้ เพราะ:

1. Core hierarchy ทำงานได้ก่อน
2. ทดสอบ insert ข้อมูลจริง
3. ทดสอบ product integration
4. **Internal Reference** ช่วยระบุสินค้าได้ทันที
5. เพิ่ม Platform/Compatibility/Salvage ทีหลังได้ไม่ยาก

---

## Summary: What Claude Understands

```
┌─────────────────────────────────────────────────────────────────┐
│                    CONFIRMED UNDERSTANDING                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. Business: ซื้อซากรถ → แยกอะไหล่ → ขาย                         │
│                                                                  │
│  2. Problem: อะไหล่ใช้ข้ามรุ่นได้ (Platform sharing)               │
│                                                                  │
│  3. Hierarchy: Brand → Model → Generation → Variant              │
│                                                                  │
│  4. Platform: cross-cutting (PHASE 2)                            │
│                                                                  │
│  5. Standard Fields: code, name, description, abbr               │
│     (ADDED by Claude - owner confirmed)                          │
│                                                                  │
│  6. Internal Ref: auto-gen from abbr + sequence                  │
│     (ADDED by Claude - owner confirmed)                          │
│                                                                  │
│  7. Odoo Version: 19 (NOT 17)                                    │
│                                                                  │
│  8. Prototype A: 6 models (core)                                 │
│  9. Phase 2: +4 models (Platform, Compatibility, Salvage, BOM)   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

*Document created: 2026-03-26*
*Author: Claude Code Assistant*
