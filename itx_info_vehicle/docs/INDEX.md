# Documentation Index - ITX Info Vehicle

**Module:** `itx_info_vehicle`
**Odoo Version:** 19.0
**Last Updated:** 2026-03-30

---

## Document Classification

เอกสารในโฟลเดอร์นี้จัดประเภทตามมาตรฐาน Software Documentation:

| Document | Type | Classification | Purpose |
|----------|------|----------------|---------|
| [INDEX.md](./INDEX.md) | Index | **DOC Index** | รายการเอกสารทั้งหมด (this file) |
| [ORIGINAL_DESIGN.md](./ORIGINAL_DESIGN.md) | Requirements | **BRD/SRS** | Original design from Project Owner |
| [EPC_READY_SPEC.md](./EPC_READY_SPEC.md) | Requirements | **BRD/SRS** | Target spec for EPC integration |
| [DESIGN_COMPARISON.md](./DESIGN_COMPARISON.md) | Analysis | **GAP Analysis** | เปรียบเทียบ Original vs Prototype A |
| [EPC_SPEC_COMPARISON.md](./EPC_SPEC_COMPARISON.md) | Analysis | **GAP Analysis** | เปรียบเทียบ EPC-Ready Spec vs Source Code |
| [DESIGN_DECISIONS.md](./DESIGN_DECISIONS.md) | Architecture | **ADR** | เหตุผลการออกแบบ (Architecture Decision Record) |
| [README.md](./README.md) | Project Documentation | **PRD** | ภาพรวมโมดูล, Features, Installation, Usage |
| [FIELD_SPECIFICATION.md](./FIELD_SPECIFICATION.md) | Technical Specification | **TSD** | Data Dictionary, Field definitions, Constraints |
| [DATA_MODEL.md](./DATA_MODEL.md) | Architecture Documentation | **SAD** | ERD, Relationships, Data flow |

---

## Document Types Explained

### 0. BRD/SRS - Business Requirements / Software Requirements Specification
**File:** `ORIGINAL_DESIGN.md`

- **วัตถุประสงค์:** เอกสาร requirements จาก Project Owner (Original)
- **ผู้อ่าน:** Developer, Project Manager, Stakeholders
- **เนื้อหา:**
  - Business Context (ที่มาและความต้องการ)
  - Domain Knowledge (ความรู้เรื่องรถยนต์)
  - Full Data Architecture (9 models)
  - MRP Integration specifications
  - Search/Compatibility Logic
  - Module Structure (full version)

### 0.0.1 BRD/SRS - EPC-Ready Specification
**File:** `EPC_READY_SPEC.md`

- **วัตถุประสงค์:** Target specification สำหรับ EPC Integration
- **ผู้อ่าน:** Developer, Project Owner
- **เนื้อหา:**
  - Design Principles (Normalization, No free-text)
  - 5 Core Models (Brand, Model, Generation, Engine, Variant)
  - Selection values (Transmission, Drivetrain, Body Type, Fuel Type)
  - Constraints requirements
  - UI/UX guidelines
  - Example data
  - Future EPC integration

### 0.1 GAP Analysis - Design Comparison
**File:** `DESIGN_COMPARISON.md`

- **วัตถุประสงค์:** เปรียบเทียบ Original Design กับ Prototype A
- **ผู้อ่าน:** Developer, Project Owner
- **เนื้อหา:**
  - Summary of differences
  - Field-by-field comparison
  - Phase planning (Prototype A vs Phase 2)
  - Questions for owner
  - Confirmed understanding

### 0.2 GAP Analysis - EPC Spec Comparison
**File:** `EPC_SPEC_COMPARISON.md`

- **วัตถุประสงค์:** เปรียบเทียบ EPC-Ready Spec กับ Source Code ปัจจุบัน
- **ผู้อ่าน:** Developer, Project Owner
- **เนื้อหา:**
  - Model comparison (EPC Spec vs Current)
  - Field-by-field comparison per model
  - Selection values differences
  - Missing constraints
  - Extra features analysis
  - Action items with priorities
  - Questions for decision

### 0.3 ADR - Architecture Decision Record
**File:** `DESIGN_DECISIONS.md`

- **วัตถุประสงค์:** บันทึกเหตุผลการออกแบบ เพื่ออ้างอิงในอนาคต
- **ผู้อ่าน:** Developer, Project Owner, Future Maintainers
- **เนื้อหา:**
  - Variant = Master Data (ไม่ใช่รถเป็นคัน)
  - Year Field ไม่อยู่ใน Variant
  - Body Type อยู่ใน Variant (พร้อมตัวอย่างจริง)
  - Engine Fields อยู่ใน Variant
  - Variant ต้องมีอย่างน้อย 1 ตัวต่อ Generation
  - Lookup Tables ใช้ Namespace `adm`

### 1. PRD - Product Requirements Document
**File:** `README.md`

- **วัตถุประสงค์:** อธิบายภาพรวมและความต้องการของโมดูล
- **ผู้อ่าน:** Developer, Project Manager, End User
- **เนื้อหา:**
  - Overview และ Business Purpose
  - Key Features (Prototype A scope)
  - Dependencies
  - Module Structure
  - Installation Guide
  - Usage Instructions
  - Version History

### 2. TSD - Technical Specification Document
**File:** `FIELD_SPECIFICATION.md`

- **วัตถุประสงค์:** กำหนด specification ของ fields ทุก model
- **ผู้อ่าน:** Developer, Database Admin
- **เนื้อหา:**
  - Field definitions (Name, Type, Size, Required, Index, Store)
  - SQL Constraints
  - Python Constraints (@api.constrains)
  - Computed Fields logic
  - Selection values
  - Onchange methods
  - Summary statistics (64 fields, 18 required, 8 computed, 3 related)

### 3. SAD - System Architecture Document
**File:** `DATA_MODEL.md`

- **วัตถุประสงค์:** แสดง architecture และ data relationships
- **ผู้อ่าน:** Developer, System Architect, DBA
- **เนื้อหา:**
  - Entity Relationship Diagram (ASCII art)
  - Vehicle Hierarchy visualization
  - Part Category tree structure
  - Product Integration flow
  - Field Visibility Rules
  - Onchange Flow diagram
  - Relationship Summary table
  - Index Strategy
  - Data Examples

---

## Understanding Verification

### Core Concept Summary

```
┌─────────────────────────────────────────────────────────────────┐
│                    ITX Info Vehicle Module                       │
│                         Odoo 19.0                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  PURPOSE: จัดการอะไหล่รถยนต์มือสอง (Salvage Car Parts)           │
│                                                                  │
│  HIERARCHY:                                                      │
│    Brand → Model → Generation → Variant                          │
│    (ยี่ห้อ)  (รุ่น)    (ยุค/ปี)     (รุ่นย่อย)                        │
│                                                                  │
│  STANDARD FIELDS (ทุก model):                                    │
│    • code  = รหัสตามตลาดใช้จริง                                  │
│    • name  = ชื่อแสดง (display_name)                             │
│    • description = คำอธิบาย (textbox)                            │
│    • abbr  = ตัวย่อสำหรับ Internal Ref (auto-gen, แก้ได้)         │
│                                                                  │
│  INTERNAL REFERENCE FORMAT:                                      │
│    {brand.abbr}-{model.abbr}-{gen.abbr}-{variant.abbr}-          │
│    {part_cat.abbr}-{sequence}                                    │
│                                                                  │
│    Example: HON-CIV-FD-1.8S-ENG-00001                            │
│                                                                  │
│  SEQUENCE: Running number (auto-gen, แก้ได้)                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Models Summary (Prototype A)

| # | Model | Technical Name | Fields | Purpose |
|---|-------|----------------|--------|---------|
| 1 | Brand | `itx.info.vehicle.brand` | 9 | ยี่ห้อรถยนต์ |
| 2 | Model | `itx.info.vehicle.model` | 10 | รุ่นรถยนต์ |
| 3 | Generation | `itx.info.vehicle.generation` | 13 | ยุค/Generation |
| 4 | Variant | `itx.info.vehicle.variant` | 14 | รุ่นย่อย/Trim |
| 5 | Part Category | `itx.info.vehicle.part.category` | 9 | ประเภทอะไหล่ (hierarchy) |
| 6 | Product | `product.template` (inherit) | +9 | เพิ่ม fields ใน product |

**Total:** 6 Models, 64 Fields

### Key Decisions Confirmed

| Decision | Value | Reason |
|----------|-------|--------|
| ตัวย่อ field name | `abbr` | สั้น กระชับ |
| abbr generation | Auto-gen (default) แก้ได้ | ยืดหยุ่น |
| Sequence | Running number แก้ได้ | ยืดหยุ่น |
| Odoo version | 19.0 | ตามโปรเจค |

### Dependencies

```python
'depends': ['base', 'product', 'stock']
```

---

## File Structure After Implementation

```
itx_info_vehicle/
├── __init__.py
├── __manifest__.py
├── docs/                           # Documentation
│   ├── INDEX.md                    # ← This file (Document index)
│   ├── README.md                   # PRD - Project documentation
│   ├── FIELD_SPECIFICATION.md     # TSD - Field specifications
│   └── DATA_MODEL.md              # SAD - Architecture & ERD
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
│   └── ir_sequence_data.xml
└── static/
    └── description/
        └── icon.png
```

---

## Checklist Before Implementation

- [x] Standard fields defined (code, name, description, abbr)
- [x] abbr = auto-generated, editable
- [x] Sequence = running number, editable
- [x] Internal Reference format confirmed
- [x] 6 Models specified (Brand, Model, Generation, Variant, Part Category, Product inherit)
- [x] 64 Fields total
- [x] Constraints defined
- [x] Onchange flow designed
- [x] ERD documented
- [x] Odoo 19 confirmed

---

## Next Steps

1. **Create module skeleton** (`__init__.py`, `__manifest__.py`)
2. **Create models** (6 Python files)
3. **Create views** (7 XML files)
4. **Create security** (ACL + groups)
5. **Create sequence data** (ir.sequence)
6. **Test installation**
7. **Insert demo data**

---

## Author

**IT Expert Training & Outsourcing Co. (Thailand)**
**Claude Code Assistant** - Odoo 19 Development

---

*Document created: 2026-03-26*
*Last reviewed: 2026-03-26*
