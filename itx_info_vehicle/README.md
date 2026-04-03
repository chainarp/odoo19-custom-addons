# ITX Info Vehicle

**Version:** 19.0.1.4.4
**Odoo:** 19.0 Community Edition
**License:** LGPL-3
**Author:** IT Expert Training & Outsourcing Co. (Thailand)

## Overview

Odoo module สำหรับจัดการข้อมูลรถยนต์และอะไหล่รถยนต์มือสอง (Salvage Car Parts Business)

## Features

### 1. Vehicle Hierarchy (4 Levels)
```
Brand → Model → Generation → Spec
  │       │         │          └── รุ่นย่อย (2.4E, 2.8V, etc.)
  │       │         └── รุ่น/ปี + Minor Change (Pre-MC/Post-MC)
  │       └── รุ่นรถ (Vigo, Fortuner, Civic, etc.)
  └── ยี่ห้อ (Toyota, Honda, Isuzu, etc.)
```

### 2. Master Data Tables

| Model | Description | Records |
|-------|-------------|---------|
| `itx.info.vehicle.brand` | ยี่ห้อรถ | Toyota, Honda, Isuzu, etc. |
| `itx.info.vehicle.model` | รุ่นรถ | Vigo, Fortuner, Civic, etc. |
| `itx.info.vehicle.generation` | Generation/ปี | Gen 1, Gen 2, Pre-MC, Post-MC |
| `itx.info.vehicle.spec` | Spec รุ่นย่อย | 2.4E MT 4x2, 2.8V AT 4x4, etc. |
| `itx.info.vehicle.mgr.body.type` | ประเภทตัวถัง | Sedan, SUV, Double Cab, etc. (17 types) |
| `itx.info.vehicle.mgr.engine` | เครื่องยนต์ | 1KD-FTV, 2KD-FTV, R18A, etc. |
| `itx.info.vehicle.part.category` | หมวดหมู่อะไหล่ | Hierarchical (Body, Electrical, etc.) |
| `itx.info.vehicle.template.part` | ชื่ออะไหล่มาตรฐาน | ~79 รายการ |
| `itx.info.vehicle.template.bom` | BOM Template | 378 รายการ (7 body types) |

### 3. Product Template Extension

Extend `product.template` with vehicle part fields:

**Required Fields (when `itx_is_vehicle_part = True`):**
- `itx_spec_id` - Vehicle Spec
- `itx_part_name_id` - Part Name (Many2one to template.part)
- `itx_part_origin` - OEM / Aftermarket / Reconditioned
- `itx_condition` - New / Like New / Good / Fair

**Optional Fields:**
- `itx_part_category_id` - Part Category (auto-fill from part template)
- `itx_part_brand` - Part manufacturer (Denso, Bosch, etc.)
- `itx_part_number` - Part manufacturer number
- `itx_oem_part_number` - OEM part number
- `itx_compatible_spec_ids` - Many2many compatible specs
- `itx_sequence` - Running number (auto-generated)

**Computed/Related Fields:**
- `itx_brand_id` - Brand (from spec)
- `itx_model_id` - Model (from spec)
- `itx_generation_id` - Generation (from spec)
- `default_code` - Internal Reference (auto-generated)

### 4. Unique Constraint (UK)

```
UK: spec_id + part_name_id + origin + condition
```

**ตัวอย่าง:** สร้างได้หลาย record สำหรับ part เดียวกัน:
- Fortuner 2.8V + กันชนหน้า + OEM + Like New → Record 1
- Fortuner 2.8V + กันชนหน้า + OEM + Good → Record 2 (condition ต่าง = ราคาต่าง)
- Fortuner 2.8V + กันชนหน้า + Aftermarket + New → Record 3 (origin ต่าง)

### 5. Auto-generate Internal Reference

Format: `BRAND-MODEL-GEN-SPEC-CAT-PART-SEQ`

**ตัวอย่าง:** `TYT-VIGO-G2-30G-BDY-BMP-F-00001`

### 6. UX Features

- **Part Name Autocomplete:** พิมพ์ค้นหาจาก master table
- **Auto-fill Category:** เลือก Part Name → Category เติมอัตโนมัติ
- **Required Field Validation:** แสดง * และบังคับก่อน save
- **Duplicate Validation:** ตรวจสอบอะไหล่ซ้ำ

---

## Models Summary

### Core Models (11 models)

```
models/
├── mgr_body_type.py          # Body Type master
├── mgr_engine.py             # Engine master
├── vehicle_brand.py          # Brand
├── vehicle_model.py          # Model
├── vehicle_generation.py     # Generation
├── vehicle_spec.py           # Spec
├── part_category.py          # Part Category (hierarchical)
├── template_part.py          # Part Name master (NEW)
├── template_bom.py           # BOM Template (NEW)
└── product_template.py       # Extend product.template
```

### template_part.py - Part Name Master Table

```python
class ItxInfoVehicleTemplatePart(models.Model):
    _name = 'itx.info.vehicle.template.part'
    _description = 'Vehicle Part Template'
    _order = 'category_id, name'

    code = fields.Char(required=True, index=True)      # e.g., HEADLIGHT_LH
    name = fields.Char(required=True, index=True)      # e.g., ไฟหน้าซ้าย
    name_en = fields.Char(index=True)                  # e.g., Left Headlight
    abbr = fields.Char(required=True, size=10)         # e.g., HLT-L
    category_id = fields.Many2one('itx.info.vehicle.part.category')

    _sql_constraints = [
        ('code_uniq', 'UNIQUE(code)', '...'),
        ('abbr_uniq', 'UNIQUE(abbr)', '...'),
    ]
```

**Data:** ~79 records from user Excel (กันชนหน้า, ไฟหน้าซ้าย, ประตูหน้าซ้าย, etc.)

### template_bom.py - BOM Template

```python
class ItxInfoVehicleTemplateBom(models.Model):
    _name = 'itx.info.vehicle.template.bom'
    _description = 'Vehicle BOM Template'
    _order = 'body_type_id, sequence, part_category_id'

    body_type_id = fields.Many2one('itx.info.vehicle.mgr.body.type', required=True)
    part_category_id = fields.Many2one('itx.info.vehicle.part.category', required=True)
    part_template_id = fields.Many2one('itx.info.vehicle.template.part', required=True)
    qty = fields.Integer(default=1)
    sequence = fields.Integer(default=10)

    _sql_constraints = [
        ('unique_bom_line', 'UNIQUE(body_type_id, part_template_id)', '...'),
    ]
```

**Data:** 378 records (7 body types x ~54 parts each)

| Body Type | Parts |
|-----------|-------|
| Extra Cab (กะบะแคป) | ~54 |
| Double Cab (กะบะ 4 ประตู) | ~54 |
| SUV | ~54 |
| Van (รถตู้) | ~54 |
| VIP Van (รถตู้ VIP) | ~54 |
| 10-Wheel Truck (สิบล้อ) | ~54 |
| Sedan (รถเก๋ง) | ~54 |

---

## Data Files

| File | Records | Description |
|------|---------|-------------|
| `part_category_data.xml` | ~40 | Part categories (hierarchical) |
| `vehicle_brand_data.xml` | 10 | Toyota, Honda, Isuzu, etc. |
| `vehicle_model_data.xml` | ~30 | Vigo, Fortuner, Civic, etc. |
| `vehicle_generation_data.xml` | ~50 | Generations with chassis codes |
| `vehicle_spec_data.xml` | ~15 | Specs (2.4E, 2.8V, etc.) |
| `mgr_body_type_data.xml` | 17 | Body types |
| `mgr_engine_data.xml` | ~20 | Engines |
| `template_part_data.xml` | ~79 | Part name master |
| `template_bom_data.xml` | 378 | BOM templates |
| `demo_specs_from_excel.xml` | 8 | Demo specs from Excel |

---

## Security

Access control based on stock groups:
- **Stock User:** Read-only
- **Stock Manager:** Full CRUD

---

## Dependencies

```python
'depends': ['base', 'product', 'stock']
```

---

## Installation

```bash
# Upgrade module
python3 odoo/odoo-bin -c odoo.conf -d DATABASE -u itx_info_vehicle --stop-after-init

# Install fresh
python3 odoo/odoo-bin -c odoo.conf -d DATABASE -i itx_info_vehicle --stop-after-init
```

---

## Changelog

### v19.0.1.4.4 (Current)
- Disable demo_vehicle_parts.xml (needs itx_part_name_id)

### v19.0.1.4.3
- Add `required` attribute in views for vehicle part fields
- Double protection: View-level + Python constraint

### v19.0.1.4.2
- Fix onchange: Always update category when part name changes

### v19.0.1.4.1
- Add required fields validation in Python constraint
- UK: spec_id + part_name_id + origin + condition

### v19.0.1.4.0
- Implement Option A: Hide `name` field, show `itx_part_name_id` Many2one
- Auto-fill product name from part template

### v19.0.1.3.0
- Add `template_part.py` - Part Name master table
- Add `template_bom.py` - BOM Template
- Import ~79 part templates from user Excel
- Import 378 BOM records (7 body types)
- Add demo specs from Excel body types

---

## Developer Notes

### Validation Flow

1. **View Level:** `required="itx_is_vehicle_part"` shows * and prevents save
2. **Python Constraint:** `_check_vehicle_part_required_and_unique()` validates:
   - Required fields: spec, part_name, origin, condition
   - Unique: spec + part_name + origin + condition

### Adding New Part Templates

1. Add record to `data/template_part_data.xml`
2. Update BOM templates in `data/template_bom_data.xml`
3. Upgrade module

### Extending for New Body Types

1. Add body type to `data/mgr_body_type_data.xml`
2. Add BOM entries for new body type
3. Upgrade module
