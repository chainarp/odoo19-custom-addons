# Data Model - ITX Info Vehicle

**Version:** 1.2.0 (Updated: 2026-03-31)

## Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              ITX Info Vehicle - Data Model                               │
└─────────────────────────────────────────────────────────────────────────────────────────┘

                                    ┌─────────────────┐
                                    │   res.country   │
                                    │  (Odoo Core)    │
                                    └────────┬────────┘
                                             │ country_id
                                             ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                  VEHICLE HIERARCHY                                       │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                          │
│  ┌──────────────────────┐                                                               │
│  │ itx.info.vehicle     │                                                               │
│  │       .brand         │                                                               │
│  ├──────────────────────┤                                                               │
│  │ • code      (HONDA)  │                                                               │
│  │ • name      (Honda)  │                                                               │
│  │ • abbr      (HON)    │ ◄─── ตัวย่อสำหรับ Internal Ref                                │
│  │ • description        │                                                               │
│  │ • country_id         │                                                               │
│  │ • logo               │                                                               │
│  │ • active             │                                                               │
│  └──────────┬───────────┘                                                               │
│             │ 1                                                                          │
│             │                                                                            │
│             │ model_ids (One2many)                                                       │
│             │                                                                            │
│             ▼ *                                                                          │
│  ┌──────────────────────┐                                                               │
│  │ itx.info.vehicle     │                                                               │
│  │       .model         │                                                               │
│  ├──────────────────────┤                                                               │
│  │ • code      (CIVIC)  │                                                               │
│  │ • name      (Civic)  │                                                               │
│  │ • abbr      (CIV)    │ ◄─── ตัวย่อสำหรับ Internal Ref                                │
│  │ • description        │                                                               │
│  │ • brand_id      ─────┼──► FK to brand                                                │
│  │ • full_name (comp)   │ = "Honda Civic"                                               │
│  │ • active             │                                                               │
│  └──────────┬───────────┘                                                               │
│             │ 1                                                                          │
│             │                                                                            │
│             │ generation_ids (One2many)                                                  │
│             │                                                                            │
│             ▼ *                                                                          │
│  ┌──────────────────────┐                                                               │
│  │ itx.info.vehicle     │                                                               │
│  │     .generation      │                                                               │
│  ├──────────────────────┤                                                               │
│  │ • code      (FD1)    │                                                               │
│  │ • name      (Gen 8)  │                                                               │
│  │ • abbr      (FD)     │ ◄─── ตัวย่อสำหรับ Internal Ref                                │
│  │ • description        │                                                               │
│  │ • model_id      ─────┼──► FK to model                                                │
│  │ • brand_id (related) │                                                               │
│  │ • chassis_code       │                                                               │
│  │ • year_start         │                                                               │
│  │ • year_end           │                                                               │
│  │ • full_name (comp)   │ = "Honda Civic Gen 8"                                         │
│  │ • active             │                                                               │
│  └──────────┬───────────┘                                                               │
│             │ 1                                                                          │
│             │                                                                            │
│             │ variant_ids (One2many)                                                     │
│             │                                                                            │
│             ▼ *                                                                          │
│  ┌────────────────────────────┐      ┌─────────────────────────┐                        │
│  │ itx.info.vehicle.variant   │      │  MGR LOOKUP TABLES      │                        │
│  ├────────────────────────────┤      ├─────────────────────────┤                        │
│  │ • code  (1.8S-IVTEC)       │      │                         │                        │
│  │ • name  (1.8 S)            │      │  ┌───────────────────┐  │                        │
│  │ • abbr  (1.8S)             │      │  │ mgr.body.type     │  │                        │
│  │ • desc                     │      │  ├───────────────────┤  │                        │
│  │ • generation_id       ─────┼──►   │  │ • code (DCAB)     │  │                        │
│  │ • model_id (related)       │      │  │ • name (Double Cab│  │                        │
│  │ • brand_id (related)       │      │  │ • sequence        │  │                        │
│  │ ───────────────────────────│      │  │ • active          │  │                        │
│  │ • body_type_id        ─────┼──────┼──► (FK)              │  │                        │
│  │ • engine_id           ─────┼──────┼──►                   │  │                        │
│  │ • transmission (sel)       │      │  └───────────────────┘  │                        │
│  │ • drive_type (sel)         │      │                         │                        │
│  │ • fuel_type (sel)          │      │  ┌───────────────────┐  │                        │
│  │ ───────────────────────────│      │  │ mgr.engine        │  │                        │
│  │ • full_name (comp)         │      │  ├───────────────────┤  │                        │
│  │ • active                   │      │  │ • code (1KD-FTV)  │  │                        │
│  └────────────────────────────┘      │  │ • name (1KD-FTV)  │  │                        │
│                                      │  │ • displacement    │  │                        │
│                                      │  │ • fuel_type       │  │                        │
│                                      │  │ • brand_id        │  │                        │
│                                      │  │ • sequence        │  │                        │
│                                      │  │ • active          │  │                        │
│                                      │  └───────────────────┘  │                        │
│                                      └─────────────────────────┘                        │
│                                                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                  PART CATEGORY                                           │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                          │
│  ┌──────────────────────┐                                                               │
│  │ itx.info.vehicle     │ ◄──┐                                                          │
│  │   .part.category     │    │ parent_id (self-reference)                               │
│  ├──────────────────────┤    │                                                          │
│  │ • code     (ENGINE)  │    │                                                          │
│  │ • name     (เครื่องยนต์) │    │                                                          │
│  │ • abbr     (ENG)     │ ◄──┼── ตัวย่อสำหรับ Internal Ref                              │
│  │ • description        │    │                                                          │
│  │ • parent_id     ─────┼────┘                                                          │
│  │ • child_ids          │                                                               │
│  │ • complete_name(comp)│ = "เครื่องยนต์ / หัวเครื่อง"                                      │
│  │ • parent_path        │ = "/1/5/12/"                                                  │
│  │ • active             │                                                               │
│  └──────────────────────┘                                                               │
│                                                                                          │
│  Example Hierarchy:                                                                      │
│  ├── เครื่องยนต์ (ENGINE/ENG)                                                              │
│  │   ├── หัวเครื่อง (HEAD/HED)                                                           │
│  │   ├── เสื้อสูบ (BLOCK/BLK)                                                            │
│  │   └── ฝาสูบ (CVHEAD/CVH)                                                             │
│  ├── ระบบส่งกำลัง (TRANSMISSION/TRN)                                                     │
│  │   ├── เกียร์ (GEAR/GER)                                                              │
│  │   └── คลัทช์ (CLUTCH/CLT)                                                            │
│  └── ระบบไฟฟ้า (ELECTRICAL/ELE)                                                         │
│                                                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              PRODUCT INTEGRATION                                         │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                          │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐   │
│  │                        product.template (inherit)                                 │   │
│  ├──────────────────────────────────────────────────────────────────────────────────┤   │
│  │                                                                                   │   │
│  │  [Odoo Standard Fields]              [ITX Vehicle Part Fields]                    │   │
│  │  • name                               • itx_is_vehicle_part (Boolean)            │   │
│  │  • default_code ◄─────────────────────── AUTO-GENERATED ─────────────────────┐   │   │
│  │  • categ_id                           • itx_brand_id ─────► brand            │   │   │
│  │  • list_price                         • itx_model_id ─────► model            │   │   │
│  │  • standard_price                     • itx_generation_id ─► generation      │   │   │
│  │  • ...                                • itx_variant_id ────► variant         │   │   │
│  │                                       • itx_part_category_id ► part.category │   │   │
│  │                                       ─────────────────────────────────────────   │   │
│  │                                       • itx_part_origin (Selection)               │   │
│  │                                         - oem: OEM (แท้)                          │   │
│  │                                         - aftermarket: Aftermarket (เทียม)        │   │
│  │                                         - reconditioned: Reconditioned (รีบิ้วท์)  │   │
│  │                                       ─────────────────────────────────────────   │   │
│  │                                       • itx_condition (Selection)                 │   │
│  │                                         - new: New (มือหนึ่ง)                      │   │
│  │                                         - like_new: Like New (มือสองสภาพใหม่)     │   │
│  │                                         - good: Good (ใช้งานได้ดี)                 │   │
│  │                                         - fair: Fair (ต้องซ่อม/ปรับแต่ง)           │   │
│  │                                       ─────────────────────────────────────────   │   │
│  │                                       • itx_oem_part_number (Optional)        │   │   │
│  │                                       • itx_sequence ────────────────────────┘   │   │
│  │                                                                                   │   │
│  └──────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                          │
│  Internal Reference (default_code) Generation:                                          │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐   │
│  │                                                                                   │   │
│  │   {brand.abbr} - {model.abbr} - {gen.abbr} - {variant.abbr} - {cat.abbr} - {seq} │   │
│  │        │              │            │              │              │          │    │   │
│  │        ▼              ▼            ▼              ▼              ▼          ▼    │   │
│  │       HON     -     CIV    -     FD      -     1.8S     -     ENG    -   00001   │   │
│  │                                                                                   │   │
│  │   Result: HON-CIV-FD-1.8S-ENG-00001                                              │   │
│  │                                                                                   │   │
│  └──────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              UNIQUE CONSTRAINT                                           │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                          │
│  Vehicle Part ต้องไม่ซ้ำกัน โดยพิจารณาจาก 6 fields:                                       │
│                                                                                          │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐   │
│  │                                                                                   │   │
│  │   UNIQUE (                                                                        │   │
│  │       itx_variant_id,           ◄─── รถรุ่นไหน                                    │   │
│  │       itx_part_category_id,     ◄─── หมวดอะไหล่อะไร                               │   │
│  │       name,                     ◄─── ชื่อชิ้นส่วน (ซ้าย/ขวา)                       │   │
│  │       itx_part_origin,          ◄─── แท้/เทียม                                    │   │
│  │       itx_condition,            ◄─── สภาพ (New/Good/Fair)                        │   │
│  │       itx_oem_part_number       ◄─── เลข OEM (NULL ได้)                          │   │
│  │   )                                                                               │   │
│  │                                                                                   │   │
│  └──────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                          │
│  ตัวอย่าง Records ที่ต่างกัน:                                                            │
│  ┌────────────────────────────────────────────────────────────────────────────────────┐ │
│  │ Variant        │ Category   │ Name        │ Origin │ Condition │ OEM Part No      │ │
│  ├────────────────┼────────────┼─────────────┼────────┼───────────┼──────────────────┤ │
│  │ Vigo 3.0G      │ ไฟหน้า      │ ไฟหน้าซ้าย   │ OEM    │ Like New  │ 81170-0K440      │ │
│  │ Vigo 3.0G      │ ไฟหน้า      │ ไฟหน้าขวา   │ OEM    │ Like New  │ 81130-0K440      │ │ ← name ต่าง
│  │ Vigo 3.0G      │ กันชนหน้า   │ กันชนหน้า   │ OEM    │ Like New  │ NULL             │ │
│  │ Vigo 3.0G      │ กันชนหน้า   │ กันชนหน้า   │ OEM    │ Good      │ NULL             │ │ ← condition ต่าง
│  │ Vigo 3.0G      │ หน้ากระจัง  │ หน้ากระจัง   │ OEM    │ Like New  │ NULL             │ │
│  │ Vigo 3.0G      │ หน้ากระจัง  │ หน้ากระจัง   │ Afterm │ New       │ NULL             │ │ ← origin ต่าง
│  └────────────────┴────────────┴─────────────┴────────┴───────────┴──────────────────┘ │
│                                                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              FIELD VISIBILITY RULES                                      │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                          │
│  Product Form View:                                                                      │
│                                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │  [ ] Vehicle Part  ◄─── itx_is_vehicle_part checkbox                            │    │
│  │                                                                                  │    │
│  │  ┌─────────────────────────────────────────────────────────────────────────┐    │    │
│  │  │  VISIBLE ONLY WHEN itx_is_vehicle_part = True                           │    │    │
│  │  │  ─────────────────────────────────────────────────────────────────────  │    │    │
│  │  │  Brand:      [Honda          ▼]  ◄─ domain: []                          │    │    │
│  │  │  Model:      [Civic          ▼]  ◄─ domain: [('brand_id','=',brand)]    │    │    │
│  │  │  Generation: [Gen 8 (FD)     ▼]  ◄─ domain: [('model_id','=',model)]    │    │    │
│  │  │  Variant:    [1.8 S i-VTEC   ▼]  ◄─ domain: [('generation_id','=',gen)] │    │    │
│  │  │  ─────────────────────────────────────────────────────────────────────  │    │    │
│  │  │  Part Category: [ไฟหน้า        ▼]                                        │    │    │
│  │  │  Part Origin:   [OEM (แท้)    ▼]  ◄─ Selection                          │    │    │
│  │  │  Condition:     [Like New     ▼]  ◄─ Selection                          │    │    │
│  │  │  OEM Part No:   [81170-0K440   ]  ◄─ Optional, fill later               │    │    │
│  │  │  Sequence:      [00001         ]  ◄─ auto-gen, editable                 │    │    │
│  │  │                                                                          │    │    │
│  │  │  Internal Reference: [TOY-VIG-G2-3GDC-FHL-00001] (readonly, computed)   │    │    │
│  │  └─────────────────────────────────────────────────────────────────────────┘    │    │
│  │                                                                                  │    │
│  └─────────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                ONCHANGE FLOW                                             │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                          │
│  User selects Brand                                                                      │
│       │                                                                                  │
│       ▼                                                                                  │
│  ┌─────────────────┐                                                                    │
│  │ @api.onchange   │                                                                    │
│  │ ('itx_brand_id')│───► Clear: model_id, generation_id, variant_id                     │
│  └─────────────────┘     Update: model_id domain                                        │
│                                                                                          │
│  User selects Model                                                                      │
│       │                                                                                  │
│       ▼                                                                                  │
│  ┌─────────────────┐                                                                    │
│  │ @api.onchange   │                                                                    │
│  │ ('itx_model_id')│───► Clear: generation_id, variant_id                               │
│  └─────────────────┘     Update: generation_id domain                                   │
│                                                                                          │
│  User selects Generation                                                                 │
│       │                                                                                  │
│       ▼                                                                                  │
│  ┌─────────────────────┐                                                                │
│  │ @api.onchange       │                                                                │
│  │ ('itx_generation_id')│───► Clear: variant_id                                         │
│  └─────────────────────┘     Update: variant_id domain                                  │
│                                                                                          │
│  User selects Variant                                                                    │
│       │                                                                                  │
│       ▼                                                                                  │
│  [All selections complete]                                                               │
│       │                                                                                  │
│       ▼                                                                                  │
│  ┌─────────────────────┐                                                                │
│  │ @api.depends        │                                                                │
│  │ (all itx_* fields)  │───► Compute: default_code (Internal Reference)                 │
│  └─────────────────────┘     Format: HON-CIV-FD-1.8S-ENG-00001                          │
│                                                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## MGR Lookup Tables

### itx.info.vehicle.mgr.body.type

ประเภทตัวถังรถ - ใช้กับ Variant level

| Field | Type | Description |
|-------|------|-------------|
| `code` | Char | รหัส (DCAB, XCAB, SCAB, SEDAN, SUV) |
| `name` | Char | ชื่อ (Double Cab, Extra Cab, ...) |
| `sequence` | Integer | ลำดับการแสดงผล |
| `active` | Boolean | Active flag |

**Master Data:**
| code | name |
|------|------|
| DCAB | Double Cab |
| XCAB | Extra Cab |
| SCAB | Single Cab |
| SEDAN | Sedan |
| SUV | SUV |
| HATCH | Hatchback |
| WAGON | Wagon |
| COUPE | Coupe |

### itx.info.vehicle.mgr.engine

ข้อมูลเครื่องยนต์ - ใช้กับ Variant level

| Field | Type | Description |
|-------|------|-------------|
| `code` | Char | รหัสเครื่อง (1KD-FTV, R18A) |
| `name` | Char | ชื่อแสดงผล |
| `displacement` | Float | ความจุ (ลิตร) |
| `fuel_type` | Selection | gasoline/diesel/hybrid/ev/lpg |
| `brand_id` | Many2one | FK to Brand (Optional) |
| `sequence` | Integer | ลำดับการแสดงผล |
| `active` | Boolean | Active flag |

**Master Data Examples:**
| code | name | displacement | fuel_type | brand |
|------|------|-------------|-----------|-------|
| 1KD-FTV | 1KD-FTV 3.0L Diesel | 3.0 | diesel | Toyota |
| 2KD-FTV | 2KD-FTV 2.5L Diesel | 2.5 | diesel | Toyota |
| R18A | R18A 1.8L i-VTEC | 1.8 | gasoline | Honda |
| K20A | K20A 2.0L i-VTEC | 2.0 | gasoline | Honda |

---

## Relationship Summary

| From Model | Relation | To Model | Field Name | Inverse |
|------------|----------|----------|------------|---------|
| Brand | 1:N | Model | `model_ids` | `brand_id` |
| Model | N:1 | Brand | `brand_id` | `model_ids` |
| Model | 1:N | Generation | `generation_ids` | `model_id` |
| Generation | N:1 | Model | `model_id` | `generation_ids` |
| Generation | N:1 | Brand | `brand_id` | (related) |
| Generation | 1:N | Variant | `variant_ids` | `generation_id` |
| Variant | N:1 | Generation | `generation_id` | `variant_ids` |
| Variant | N:1 | Model | `model_id` | (related) |
| Variant | N:1 | Brand | `brand_id` | (related) |
| **Variant** | **N:1** | **Body Type** | **`body_type_id`** | - |
| **Variant** | **N:1** | **Engine** | **`engine_id`** | - |
| Part Category | N:1 | Part Category | `parent_id` | `child_ids` |
| Part Category | 1:N | Part Category | `child_ids` | `parent_id` |
| Product | N:1 | Brand | `itx_brand_id` | - |
| Product | N:1 | Model | `itx_model_id` | - |
| Product | N:1 | Generation | `itx_generation_id` | - |
| Product | N:1 | Variant | `itx_variant_id` | - |
| Product | N:1 | Part Category | `itx_part_category_id` | - |

---

## Index Strategy

### Primary Indexes (Automatic)

All primary keys are automatically indexed by PostgreSQL.

### Foreign Key Indexes

| Table | Column | Index Name |
|-------|--------|------------|
| `itx_info_vehicle_model` | `brand_id` | Auto (FK) |
| `itx_info_vehicle_generation` | `model_id` | Auto (FK) |
| `itx_info_vehicle_variant` | `generation_id` | Auto (FK) |
| `itx_info_vehicle_variant` | `body_type_id` | Auto (FK) |
| `itx_info_vehicle_variant` | `engine_id` | Auto (FK) |
| `itx_info_vehicle_part_category` | `parent_id` | Auto (FK) |
| `product_template` | `itx_brand_id` | Manual |
| `product_template` | `itx_model_id` | Manual |
| `product_template` | `itx_generation_id` | Manual |
| `product_template` | `itx_variant_id` | Manual |
| `product_template` | `itx_part_category_id` | Manual |

### Search Indexes

| Table | Columns | Purpose |
|-------|---------|---------|
| `itx_info_vehicle_brand` | `code`, `name`, `abbr` | Quick lookup |
| `itx_info_vehicle_model` | `code`, `name`, `abbr`, `full_name` | Quick lookup |
| `itx_info_vehicle_generation` | `code`, `name`, `abbr`, `chassis_code` | Quick lookup |
| `itx_info_vehicle_variant` | `code`, `name`, `abbr` | Quick lookup |
| `itx_info_vehicle_part_category` | `code`, `name`, `abbr` | Quick lookup |
| `product_template` | `itx_oem_part_number` | OEM search |
| `product_template` | `default_code` | Internal ref search |

---

## Data Examples

### Brand Examples

| code | name | abbr | country |
|------|------|------|---------|
| HONDA | Honda | HON | Japan |
| TOYOTA | Toyota | TOY | Japan |
| ISUZU | Isuzu | ISZ | Japan |
| NISSAN | Nissan | NIS | Japan |
| FORD | Ford | FRD | USA |
| BMW | BMW | BMW | Germany |

### Model Examples

| code | name | abbr | full_name |
|------|------|------|-----------|
| CIVIC | Civic | CIV | Honda Civic |
| HILUX | Hilux | HIL | Toyota Hilux |
| FORTUNER | Fortuner | FOR | Toyota Fortuner |
| DMAX | D-Max | DMX | Isuzu D-Max |

### Generation Examples

| code | name | abbr | chassis_code | year_start | year_end |
|------|------|------|--------------|------------|----------|
| FD1 | Gen 8 (FD) | FD | FD1/FD2 | 2006 | 2011 |
| VIGO-G2 | Vigo Gen 2 Champ | VG2 | KUN25/26 | 2011 | 2015 |
| FORTUNER-G2 | Gen 2 | FN2 | GUN155/156 | 2015 | 2023 |
| DMAX-G3 | Gen 3 | DX3 | RG01 | 2019 | 0 |

### Variant Examples (Vigo Gen 2)

| code | name | body_type | engine | transmission | drive |
|------|------|-----------|--------|--------------|-------|
| VIGO-G2-3.0G-DCAB | 3.0 G Double Cab | Double Cab | 1KD-FTV | auto | 4WD |
| VIGO-G2-2.5E-DCAB | 2.5 E Double Cab | Double Cab | 2KD-FTV | manual | FR |
| VIGO-G2-2.5E-XCAB | 2.5 E Extra Cab | Extra Cab | 2KD-FTV | manual | FR |
| VIGO-G2-2.5J-SCAB | 2.5 J Single Cab | Single Cab | 2KD-FTV | manual | FR |

### Part Category Examples

| code | name | abbr | parent | complete_name |
|------|------|------|--------|---------------|
| ENGINE | เครื่องยนต์ | ENG | - | เครื่องยนต์ |
| HEAD | หัวเครื่อง | HED | ENGINE | เครื่องยนต์ / หัวเครื่อง |
| EXTERIOR | ตัวถังภายนอก | EXT | - | ตัวถังภายนอก |
| FRONTLIGHT | ไฟหน้า | FHL | EXTERIOR | ตัวถังภายนอก / ไฟหน้า |

### Vehicle Part Product Example

| Field | Value |
|-------|-------|
| name | ไฟหน้าซ้าย |
| itx_is_vehicle_part | True |
| itx_brand_id | Toyota (TOY) |
| itx_model_id | Hilux (HIL) |
| itx_generation_id | Vigo Gen 2 Champ (VG2) |
| itx_variant_id | 3.0 G Double Cab (3GDC) |
| itx_part_category_id | ไฟหน้า (FHL) |
| **itx_part_origin** | **oem** |
| **itx_condition** | **like_new** |
| itx_oem_part_number | 81170-0K440 |
| itx_sequence | 00001 |
| **default_code** | **TOY-HIL-VG2-3GDC-FHL-00001** |

---

## Price Matrix Concept

ราคาอะไหล่ขึ้นอยู่กับ **Origin** และ **Condition**:

| Origin | Condition | Price Factor |
|--------|-----------|--------------|
| OEM | Like New | 100% (สูงสุด) |
| OEM | Good | 60-70% |
| OEM | Fair | 30-40% |
| Aftermarket | New | 15-25% |
| Aftermarket | Good | 10-15% |
| Reconditioned | Good | 40-50% |

**ตัวอย่าง กันชนหน้า Vigo:**
| Origin | Condition | Price |
|--------|-----------|-------|
| OEM | Like New | 8,500 |
| OEM | Good | 5,500 |
| OEM | Fair | 2,500 |
| Aftermarket | New | 1,500 |

---

*Document Version: 1.2.0*
*Last Updated: 2026-03-31*
*Changes: Added MGR lookup tables, moved body_type to Variant, added part_origin/condition, added unique constraint section*
