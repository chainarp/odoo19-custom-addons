# ITX Info Vehicle Module

**Version:** 19.0.1.2.0 | **Status:** Production Ready

## Overview

โมดูลสำหรับจัดการข้อมูลรถยนต์และอะไหล่รถยนต์มือสอง (Salvage Car Parts)
ออกแบบมาเพื่อรองรับธุรกิจซื้อ-ขายอะไหล่รถยนต์มือสองที่ต้องการความชัดเจนในการระบุ
ยี่ห้อ รุ่น ปี และสเปคของอะไหล่แต่ละชิ้น

## Key Features

### Vehicle Hierarchy (4 Levels)
```
Brand → Model → Generation → Spec
```
- **Brand**: Honda, Toyota, Isuzu
- **Model**: Civic, Accord, Vigo
- **Generation**: Gen 8 FD (2006-2011), Pre-MC/Post-MC
- **Spec**: 1.8 S i-VTEC, 3.0 G 4WD Double Cab

### Product Integration
- Extend `product.template` with vehicle compatibility fields
- **Single Spec Selection** - เลือก Spec ตัวเดียว Brand/Model/Gen แสดงอัตโนมัติ
- **Compatible Specs** - Many2many สำหรับอะไหล่ที่ใช้ได้หลายรุ่น
- **Part Brand/Number** - บันทึกยี่ห้อและเลขชิ้นส่วนผู้ผลิต
- Auto-generate Internal Reference from hierarchy

### Master Data Management
- **Body Types**: Sedan, Double Cab, SUV, Hatchback, etc.
- **Engines**: 1KD-FTV, 2KD-FTV, R18A, K20A, etc.
- **Part Categories**: Hierarchical tree structure

### Auto Internal Reference
```
HON-CIV-FD-18S-HLT-00001
 │   │   │   │   │    │
 │   │   │   │   │    └── Running Sequence
 │   │   │   │   └─────── Part Category (Headlight)
 │   │   │   └─────────── Spec Abbr (1.8S)
 │   │   └─────────────── Generation Abbr (FD)
 │   └─────────────────── Model Abbr (Civic)
 └─────────────────────── Brand Abbr (Honda)
```

## Dependencies

```python
'depends': ['base', 'product', 'stock']
```

## Module Structure

```
itx_info_vehicle/
├── __manifest__.py
├── models/
│   ├── vehicle_brand.py          # Brand model
│   ├── vehicle_model.py          # Model model
│   ├── vehicle_generation.py     # Generation model
│   ├── vehicle_spec.py           # Spec model
│   ├── mgr_body_type.py          # Body Type master
│   ├── mgr_engine.py             # Engine master
│   ├── part_category.py          # Part Category (hierarchical)
│   └── product_template.py       # Extends product.template
├── views/
│   ├── vehicle_*_views.xml       # All view definitions
│   ├── mgr_*_views.xml           # Master data views
│   ├── product_template_views.xml
│   └── menuitems.xml
├── security/
│   └── ir.model.access.csv
├── data/
│   ├── ir_sequence_data.xml      # Auto-sequence for parts
│   ├── vehicle_*_data.xml        # Sample vehicle data
│   ├── mgr_*_data.xml            # Master data
│   ├── part_category_data.xml    # Part categories
│   └── demo_vehicle_parts.xml    # Demo parts (16 records)
└── docs/
    ├── README.md                 # This file
    ├── MODULE_SUMMARY.md         # Detailed summary for design discussion
    └── ...
```

## Installation

```bash
# Install module (new database recommended)
python3 odoo/odoo-bin -c odoo.conf -d odoo19 -i itx_info_vehicle --stop-after-init

# Upgrade module
python3 odoo/odoo-bin -c odoo.conf -d odoo19 -u itx_info_vehicle --stop-after-init
```

## Usage

### 1. Setup Vehicle Hierarchy

1. Go to **Inventory → Configuration → Vehicle Info**
2. Create **Brands** (e.g., Honda, Toyota, Isuzu)
3. Create **Models** under each brand (e.g., Civic, Accord)
4. Create **Generations** for each model (e.g., Gen 8 FD 2006-2011)
5. Create **Specs** for each generation (e.g., 1.8 S i-VTEC)

### 2. Setup Part Categories

1. Go to **Inventory → Configuration → Vehicle Info → Part Categories**
2. Create hierarchical categories:
   ```
   Engine (เครื่องยนต์)
   ├── Engine Assembly (เครื่องทั้งลูก)
   ├── Alternator (ไดชาร์จ)
   └── Starter (ไดสตาร์ท)
   Body (ตัวถัง)
   ├── Hood Front (ฝากระโปรงหน้า)
   └── Bumper (กันชน)
   ```

### 3. Create Vehicle Parts

1. Go to **Inventory → Vehicle Parts**
2. Create new product
3. Enable **"Vehicle Part"** checkbox
4. Select **Spec** → Brand/Model/Generation shows automatically
5. Select Part Category, Origin (OEM/Aftermarket), Condition
6. Internal Reference auto-generates

## Menu Structure

```
Inventory
├── Inventory Control
│   └── Vehicle Parts          ← รายการอะไหล่ทั้งหมด
│
└── Configuration
    └── Vehicle Info
        ├── Brands
        ├── Models
        ├── Generations
        ├── Specs
        ├── Part Categories
        └── Master Data
            ├── Body Types
            └── Engines
```

## Product Fields

| Field | Type | Description |
|-------|------|-------------|
| `itx_is_vehicle_part` | Boolean | เปิด/ปิด Vehicle Part mode |
| `itx_spec_id` | Many2one | สเปครถหลัก |
| `itx_brand_id` | Related | ยี่ห้อ (auto จาก spec) |
| `itx_model_id` | Related | รุ่น (auto จาก spec) |
| `itx_generation_id` | Related | เจน (auto จาก spec) |
| `itx_compatible_spec_ids` | Many2many | สเปคที่เข้ากันได้ |
| `itx_part_category_id` | Many2one | หมวดอะไหล่ |
| `itx_part_brand` | Char | ยี่ห้ออะไหล่ (Denso, Bosch) |
| `itx_part_number` | Char | เลขชิ้นส่วน |
| `itx_part_origin` | Selection | OEM/Aftermarket/Reconditioned |
| `itx_condition` | Selection | New/Like New/Good/Fair |
| `itx_oem_part_number` | Char | เลข OEM (optional) |
| `itx_sequence` | Char | Running number (auto) |

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 19.0.1.2.0 | 2026-04-02 | Rename Variant→Spec, Simplify product form |
| 19.0.1.1.0 | 2026-03 | Add Body Type, Engine master tables |
| 19.0.1.0.0 | 2026-03 | Initial release - Core models |

## Author

**IT Expert Training & Outsourcing Co. (Thailand)**
https://www.itexpert.co.th

---

*For detailed design documentation, see [MODULE_SUMMARY.md](./MODULE_SUMMARY.md)*
