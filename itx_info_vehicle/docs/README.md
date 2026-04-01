# ITX Info Vehicle Module

## Overview

โมดูลสำหรับจัดการข้อมูลรถยนต์และอะไหล่รถยนต์มือสอง (Salvage Car Parts)
ออกแบบมาเพื่อรองรับธุรกิจซื้อ-ขายอะไหล่รถยนต์มือสองที่ต้องการความชัดเจนในการระบุ
ยี่ห้อ รุ่น ปี และรุ่นย่อยของอะไหล่แต่ละชิ้น

## Key Features

### Prototype A (Current Scope)

- **Vehicle Hierarchy Management**
  - Brand (ยี่ห้อ) → Model (รุ่น) → Generation (ยุค/ปี) → Variant (รุ่นย่อย)

- **Part Category Management**
  - Hierarchical part categories (ประเภทอะไหล่แบบ tree)

- **Product Integration**
  - Extend `product.template` with vehicle compatibility fields
  - Auto-generate Internal Reference from hierarchy

- **Auto Internal Reference**
  - Format: `{brand_abbr}-{model_abbr}-{gen_abbr}-{variant_abbr}-{part_cat_abbr}-{sequence}`
  - Example: `HON-CIV-FD-1.8S-ENG-00001`

### Future Phases (Not in Prototype A)

- BOM Template for common part sets
- Compatibility Matrix (cross-reference parts)
- Salvage Car Management with MRP Integration
- Advanced Search (3 modes + full-text)

## Dependencies

```python
'depends': ['base', 'product', 'stock'],
```

## Module Structure

```
itx_info_vehicle/
├── __init__.py
├── __manifest__.py
├── docs/
│   ├── README.md                 # This file
│   ├── FIELD_SPECIFICATION.md    # Detailed field specs
│   └── DATA_MODEL.md             # Entity relationships
├── models/
│   ├── __init__.py
│   ├── vehicle_brand.py
│   ├── vehicle_model.py
│   ├── vehicle_generation.py
│   ├── vehicle_variant.py
│   ├── part_category.py
│   └── product_template.py
├── views/
│   ├── vehicle_brand_views.xml
│   ├── vehicle_model_views.xml
│   ├── vehicle_generation_views.xml
│   ├── vehicle_variant_views.xml
│   ├── part_category_views.xml
│   ├── product_template_views.xml
│   └── menuitems.xml
├── security/
│   ├── ir.model.access.csv
│   └── security_groups.xml
├── data/
│   └── ir_sequence_data.xml      # Sequence for running number
└── static/
    └── description/
        └── icon.png
```

## Installation

```bash
# Install module
python3 odoo/odoo-bin -c odoo.conf -d odoo19 -i itx_info_vehicle --stop-after-init

# Upgrade module
python3 odoo/odoo-bin -c odoo.conf -d odoo19 -u itx_info_vehicle --stop-after-init
```

## Usage

### 1. Setup Vehicle Hierarchy

1. Go to **Inventory → Configuration → Vehicle Info**
2. Create **Brands** (e.g., Honda, Toyota, Nissan)
3. Create **Models** under each brand (e.g., Civic, Accord)
4. Create **Generations** for each model (e.g., Gen 8 FD 2006-2011)
5. Create **Variants** for each generation (e.g., 1.8 S i-VTEC)

### 2. Setup Part Categories

1. Go to **Inventory → Configuration → Part Categories**
2. Create hierarchical categories:
   - เครื่องยนต์ (ENGINE)
     - หัวเครื่อง (HEAD)
     - เสื้อสูบ (BLOCK)
   - ระบบส่งกำลัง (TRANS)
     - เกียร์ (GEAR)
     - คลัทช์ (CLUTCH)

### 3. Create Vehicle Parts (Products)

1. Go to **Inventory → Products**
2. Create new product
3. Enable **"Vehicle Part"** checkbox
4. Select Brand → Model → Generation → Variant → Part Category
5. Internal Reference auto-generates: `HON-CIV-FD-1.8S-ENG-00001`

## Technical Notes

### Standard Fields (All Models)

Every model includes these standard fields:

| Field | Type | Purpose |
|-------|------|---------|
| `code` | Char | Market code (ตามตลาดใช้จริง) |
| `name` | Char | Display name |
| `description` | Text | Description/notes |
| `abbr` | Char(10) | Abbreviation for Internal Ref (auto-gen, editable) |
| `active` | Boolean | Archive support |

### Internal Reference Generation

```python
# Format
default_code = f"{brand.abbr}-{model.abbr}-{gen.abbr}-{variant.abbr}-{part_cat.abbr}-{seq}"

# Example
default_code = "HON-CIV-FD-1.8S-ENG-00001"
```

### Abbreviation Auto-Generation

```python
# Logic: Take first 3-4 uppercase chars from name
"Honda" → "HON"
"Civic" → "CIV"
"Gen 8 (FD)" → "FD" (extract from parentheses if exists)
"1.8 S i-VTEC" → "1.8S"
"เครื่องยนต์" → "ENG" (from code field)
```

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 0.1.0 | 2026-03 | Prototype A - Core models (Odoo 19) |

## Author

**IT Expert Training & Outsourcing Co. (Thailand)**

---

*For detailed field specifications, see [FIELD_SPECIFICATION.md](./FIELD_SPECIFICATION.md)*
*For data model diagrams, see [DATA_MODEL.md](./DATA_MODEL.md)*
