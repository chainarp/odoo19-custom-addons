# ITX Info Vehicle - Module Summary

**Version:** 19.0.1.2.0
**Last Updated:** 2026-04-02
**Status:** Production Ready

---

## 1. Overview

ITX Info Vehicle เป็น Odoo 19 module สำหรับจัดการข้อมูลยานพาหนะและอะไหล่รถยนต์มือสอง (Salvage Car Parts)
ออกแบบมาเพื่อธุรกิจขายอะไหล่รถยนต์ที่ต้องการติดตามว่าอะไหล่แต่ละชิ้นใช้กับรถรุ่นไหนได้บ้าง

### Business Use Case
- ร้านขายอะไหล่รถยนต์มือสอง/ซาก
- ต้องบันทึกว่าอะไหล่ชิ้นนี้มาจากรถรุ่นไหน
- ต้องค้นหาว่ามีอะไหล่รุ่นนี้ไหม
- ต้องระบุความเข้ากันได้ (Compatible) กับรถรุ่นอื่น

---

## 2. Architecture Overview

### 2.1 Data Model (ER Diagram)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           VEHICLE HIERARCHY                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌────────────┐ │
│  │    BRAND     │───►│    MODEL     │───►│  GENERATION  │───►│    SPEC    │ │
│  │  (ยี่ห้อ)     │ 1:N│   (รุ่น)     │ 1:N│    (เจน)     │ 1:N│  (สเปค)    │ │
│  └──────────────┘    └──────────────┘    └──────────────┘    └────────────┘ │
│        │                   │                   │                   │        │
│        │                   │                   │                   │        │
│   - Honda            - Civic              - Gen 8 (FD)        - 1.8 S       │
│   - Toyota           - Accord             - 2006-2011         - 2.0 EL      │
│   - Isuzu            - Vigo               - Pre-MC/Post-MC    - 3.0 G 4WD   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                           MASTER DATA (MGR)                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐         ┌──────────────┐                                  │
│  │  BODY TYPE   │         │    ENGINE    │                                  │
│  │ (ประเภทตัวถัง)│         │  (เครื่องยนต์) │                                  │
│  └──────────────┘         └──────────────┘                                  │
│        │                        │                                            │
│   - Sedan                  - 1KD-FTV (3.0L Diesel)                          │
│   - Double Cab             - 2KD-FTV (2.5L Diesel)                          │
│   - SUV                    - R18A (1.8L Gasoline)                           │
│   - Hatchback              - K20A (2.0L Gasoline)                           │
│                                                                              │
│                    ▲                ▲                                        │
│                    │                │                                        │
│                    └────────────────┘                                        │
│                           │                                                  │
│                    ┌──────────────┐                                          │
│                    │    SPEC      │  ◄── ลิงก์ไปหา Body Type + Engine        │
│                    └──────────────┘                                          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                           PRODUCT INTEGRATION                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                      PRODUCT.TEMPLATE                                 │   │
│  │                      (อะไหล่/สินค้า)                                   │   │
│  ├──────────────────────────────────────────────────────────────────────┤   │
│  │  - itx_is_vehicle_part (Boolean)     ◄── เปิด/ปิด Vehicle Part Mode  │   │
│  │  - itx_spec_id (Many2one)            ◄── สเปครถหลัก                   │   │
│  │  - itx_brand_id (Related, readonly)  ◄── ยี่ห้อ (auto จาก spec)       │   │
│  │  - itx_model_id (Related, readonly)  ◄── รุ่น (auto จาก spec)         │   │
│  │  - itx_generation_id (Related, ro)   ◄── เจน (auto จาก spec)          │   │
│  │  - itx_compatible_spec_ids (M2M)     ◄── สเปคที่เข้ากันได้             │   │
│  │  - itx_part_category_id (Many2one)   ◄── หมวดอะไหล่                   │   │
│  │  - itx_part_brand (Char)             ◄── ยี่ห้ออะไหล่ (Denso, Bosch)   │   │
│  │  - itx_part_number (Char)            ◄── เลขชิ้นส่วน                   │   │
│  │  - itx_part_origin (Selection)       ◄── OEM/Aftermarket/Recond       │   │
│  │  - itx_condition (Selection)         ◄── New/Like New/Good/Fair       │   │
│  │  - itx_oem_part_number (Char)        ◄── เลข OEM (optional)           │   │
│  │  - itx_sequence (Char)               ◄── Running number               │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                      PART CATEGORY                                    │   │
│  │                      (หมวดอะไหล่ - Hierarchical)                       │   │
│  ├──────────────────────────────────────────────────────────────────────┤   │
│  │  Engine (เครื่องยนต์)                                                  │   │
│  │    ├── Engine Assembly (เครื่องทั้งลูก)                                │   │
│  │    ├── Alternator (ไดชาร์จ)                                           │   │
│  │    └── Starter (ไดสตาร์ท)                                             │   │
│  │  Transmission (ระบบส่งกำลัง)                                           │   │
│  │    ├── Gearbox Auto                                                   │   │
│  │    └── Gearbox Manual                                                 │   │
│  │  Body (ตัวถัง)                                                         │   │
│  │    ├── Hood Front (ฝากระโปรงหน้า)                                      │   │
│  │    ├── Bumper Front (กันชนหน้า)                                        │   │
│  │    └── Door (ประตู)                                                    │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Model Summary Table

| Model | Technical Name | Description | Key Fields |
|-------|----------------|-------------|------------|
| Brand | `itx.info.vehicle.brand` | ยี่ห้อรถ | code, name, abbr, country_id, logo |
| Model | `itx.info.vehicle.model` | รุ่นรถ | code, name, abbr, brand_id |
| Generation | `itx.info.vehicle.generation` | รุ่นย่อย/เจน | code, name, abbr, model_id, chassis_code, year_start, year_end |
| Spec | `itx.info.vehicle.spec` | สเปครถ | code, name, abbr, generation_id, body_type_id, engine_id, transmission, drive_type, fuel_type |
| Body Type | `itx.info.vehicle.mgr.body.type` | ประเภทตัวถัง | code, name |
| Engine | `itx.info.vehicle.mgr.engine` | รหัสเครื่องยนต์ | code, name, displacement, fuel_type |
| Part Category | `itx.info.vehicle.part.category` | หมวดอะไหล่ | code, name, abbr, parent_id (hierarchical) |

---

## 3. Key Features

### 3.1 Vehicle Hierarchy (4 Levels)
```
Brand → Model → Generation → Spec
```
- **Brand**: Honda, Toyota, Isuzu
- **Model**: Civic, Accord, Vigo, Fortuner
- **Generation**: Gen 8 FD (2006-2011), Gen 9 FB (2012-2015)
- **Spec**: 1.8 S i-VTEC, 2.0 EL, 3.0 G 4WD Double Cab

### 3.2 Auto-Generate Internal Reference
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

### 3.3 Simplified Product Form
- **เลือกแค่ Spec** → Brand/Model/Generation จะแสดงอัตโนมัติ (read-only)
- **Compatible Specs**: Many2many สำหรับอะไหล่ที่ใช้ได้หลายรุ่น
- **Part Brand/Number**: บันทึกยี่ห้อและเลขชิ้นส่วนผู้ผลิต

### 3.4 Part Origin & Condition
```python
PART_ORIGIN = ['oem', 'aftermarket', 'reconditioned']
CONDITION = ['new', 'like_new', 'good', 'fair']
```

### 3.5 Hierarchical Part Categories
- ใช้ `_parent_store` สำหรับ tree structure
- complete_name แสดงเป็น path: "Body / Door / Door Cap"

---

## 4. Menu Structure

```
Inventory
├── Inventory Control
│   └── Vehicle Parts          ◄── รายการอะไหล่ทั้งหมด
│
└── Configuration
    └── Vehicle Info
        ├── Brands             ◄── จัดการยี่ห้อรถ
        ├── Models             ◄── จัดการรุ่นรถ
        ├── Generations        ◄── จัดการเจน/รุ่นย่อย
        ├── Specs              ◄── จัดการสเปค
        ├── Part Categories    ◄── หมวดอะไหล่
        └── Master Data
            ├── Body Types     ◄── ประเภทตัวถัง
            └── Engines        ◄── รหัสเครื่องยนต์
```

---

## 5. Security Model

| Group | Brand/Model/Gen/Spec | Part Category | Body/Engine |
|-------|---------------------|---------------|-------------|
| Stock User | Read | Read | Read |
| Stock Manager | Full CRUD | Full CRUD | Full CRUD |

---

## 6. Design Decisions Made

### 6.1 Rename: Variant → Spec
- **เหตุผล**: "Variant" ทำให้ user สับสน (Odoo มี Product Variants อยู่แล้ว)
- **เปลี่ยนเป็น**: "Vehicle Spec" ชัดเจนกว่า

### 6.2 Simplified Product Form
- **ก่อน**: เลือก Brand → Model → Generation → Spec (cascading dropdowns)
- **หลัง**: เลือก Spec อย่างเดียว → แสดง Brand/Model/Gen อัตโนมัติ
- **เหตุผล**: ใช้งานง่ายกว่า, ลด clicks

### 6.3 Related Fields (Read-only)
```python
itx_brand_id = fields.Many2one(related='itx_spec_id.brand_id', store=True, readonly=True)
```
- **เหตุผล**: เก็บไว้เพื่อ search/filter ได้ แต่ไม่ให้แก้ไขตรง

### 6.4 Compatible Specs (Many2many)
- อะไหล่บางชิ้นใช้ได้หลายรุ่น (เช่น ไฟหน้า FD ใส่ได้ทั้ง 1.8S และ 2.0EL)
- ใช้ many2many_tags widget

### 6.5 Manager Tables (Body Type, Engine)
- แยก Body Type และ Engine ออกมาเป็น master data
- ไม่ใช้ fixed Selection เพราะขยายได้ยาก

---

## 7. Sample Data Included

### 7.1 Brands (4)
- Honda, Toyota, Isuzu, Nissan

### 7.2 Models (6)
- Civic, Accord, Vigo, Fortuner, D-Max, Almera

### 7.3 Generations (5)
- Civic FD (2006-2011), Civic FB (2012-2015)
- Vigo Gen 2 Champ (2011-2015)
- Fortuner Gen 2 (2015-2023)
- D-Max Gen 3 (2019-present)

### 7.4 Specs (13)
- Toyota Vigo: 3.0G DCab, 2.5E DCab, 2.5E XCab, 2.5J SCab
- Toyota Fortuner: 2.8V 4WD, 2.4G
- Honda Civic FD: 1.8S, 1.8E, 2.0EL
- Isuzu D-Max: 1.9 V-Cross, 3.0 Hi-Lander

### 7.5 Demo Parts (16)
- ไฟหน้าซ้าย/ขวา, กันชนหน้า, หน้ากระจัง, กระจกมองข้าง
- ประตูแคป, ฝาปิดท้าย, ฝากระโปรง, ไฟท้าย
- เครื่องยนต์ทั้งลูก, เกียร์ออโต้

---

## 8. Files Structure

```
itx_info_vehicle/
├── __manifest__.py
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── vehicle_brand.py          # Brand model
│   ├── vehicle_model.py          # Model model
│   ├── vehicle_generation.py     # Generation model
│   ├── vehicle_spec.py           # Spec model
│   ├── mgr_body_type.py          # Body Type master
│   ├── mgr_engine.py             # Engine master
│   ├── part_category.py          # Part Category (hierarchical)
│   └── product_template.py       # Extends product.template
├── views/
│   ├── vehicle_brand_views.xml
│   ├── vehicle_model_views.xml
│   ├── vehicle_generation_views.xml
│   ├── vehicle_spec_views.xml
│   ├── mgr_body_type_views.xml
│   ├── mgr_engine_views.xml
│   ├── part_category_views.xml
│   ├── product_template_views.xml
│   └── menuitems.xml
├── security/
│   └── ir.model.access.csv
├── data/
│   ├── ir_sequence_data.xml      # Auto-sequence for parts
│   ├── vehicle_brand_data.xml    # Sample brands
│   ├── vehicle_model_data.xml    # Sample models
│   ├── vehicle_generation_data.xml
│   ├── vehicle_spec_data.xml
│   ├── mgr_body_type_data.xml
│   ├── mgr_engine_data.xml
│   ├── part_category_data.xml    # Part categories
│   └── demo_vehicle_parts.xml    # Demo parts
└── docs/
    ├── MODULE_SUMMARY.md         # This file
    ├── PRESENTATION.md
    └── ...
```

---

## 9. Dependencies

```python
'depends': ['base', 'product', 'stock']
```

---

## 10. Future Considerations

### 10.1 Potential Enhancements
- [ ] Year filter ในการค้นหา Spec
- [ ] Image gallery สำหรับ Spec
- [ ] Import/Export vehicle data (CSV/Excel)
- [ ] Integration กับ EPC (Electronic Parts Catalog)
- [ ] Smart search: พิมพ์ "Civic FD 1.8" → หา Spec ได้เลย

### 10.2 Known Limitations
- ต้องใช้ database ใหม่หลัง rename Variant → Spec (migration ไม่ได้)
- Part Category ยังไม่มี icon/image

---

## 11. How to Use (Quick Start)

### 11.1 Setup Vehicle Data
1. ไป Inventory → Configuration → Vehicle Info
2. สร้าง Brand (ถ้าไม่มี) → สร้าง Model → สร้าง Generation → สร้าง Spec

### 11.2 Add Vehicle Part
1. ไป Inventory → Vehicle Parts
2. กด Create
3. ติ๊ก "Vehicle Part" checkbox
4. เลือก Spec (Brand/Model/Gen จะขึ้นอัตโนมัติ)
5. เลือก Part Category, Origin, Condition
6. Save

### 11.3 Search Parts
- ค้นหาด้วย Spec, Brand, Model, Part Category
- Group by: Brand, Model, Part Origin, Condition
- Filter: OEM, Aftermarket, New, Like New, Good

---

**Document prepared for design discussion with Claude Web (พี่คลอดเวป)**
