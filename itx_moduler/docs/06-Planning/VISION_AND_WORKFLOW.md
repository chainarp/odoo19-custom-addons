# ITX Moduler - Vision & Workflow Design

**Date:** 2025-12-15
**Status:** Strategic Direction Document
**Version:** 1.0

---

## 🎯 Core Vision

**ITX Moduler เป็น Flexible Module Builder ที่ SA และ AI สามารถทำงานร่วมกันได้อย่างลื่นไหล**

### Key Principles

1. **Interchangeable Input Methods** - SA และ AI เป็น "creators" ที่ใช้แทนกันได้
2. **Single Source of Truth** - Snapshot tables เป็นศูนย์กลางเดียว
3. **Multiple Entry Points** - เริ่มต้นได้หลายวิธี
4. **Consistent Output** - Export ออกมาเป็น professional code เสมอ

---

## 🔄 Complete Workflow

```
┌─────────────────────────────────────────────────────────────┐
│              ENTRY POINTS (Flexible)                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  PATH 1: AI-First (Natural Language)                        │
│  ┌────────────────────────────────────────────────┐         │
│  │ User: "Create a CRM module with contacts,     │         │
│  │        companies, and opportunities"           │         │
│  │                                                 │         │
│  │ Claude API: Analyze → Generate SQL INSERT      │         │
│  │                                                 │         │
│  │ Output: Complete E-R structure in snapshots    │         │
│  └────────────────────────────────────────────────┘         │
│                                                              │
│  PATH 2: SA-First (Visual Designer)                         │
│  ┌────────────────────────────────────────────────┐         │
│  │ Visual E-R Designer (Owl 2.x Components)       │         │
│  │   - Drag-drop models                           │         │
│  │   - Draw relationships                         │         │
│  │   - Configure fields                           │         │
│  │                                                 │         │
│  │ Output: GUI creates snapshot records           │         │
│  └────────────────────────────────────────────────┘         │
│                                                              │
│  PATH 3: Hybrid (Collaboration)                             │
│  ┌────────────────────────────────────────────────┐         │
│  │ SA: Creates basic E-R structure (models only)  │         │
│  │  ↓                                              │         │
│  │ AI: "Add standard fields, views, security"     │         │
│  │  ↓                                              │         │
│  │ SA: Reviews & fine-tunes via GUI               │         │
│  │                                                 │         │
│  │ Output: Best of both worlds                    │         │
│  └────────────────────────────────────────────────┘         │
│                                                              │
│  PATH 4: Load from Existing (Reverse Engineering)           │
│  ┌────────────────────────────────────────────────┐         │
│  │ Load Module Wizard                             │         │
│  │   - Select installed Odoo module               │         │
│  │   - Reverse engineer: models, fields, views    │         │
│  │   - Import as snapshots                        │         │
│  │                                                 │         │
│  │ Output: Editable copy in workspace             │         │
│  └────────────────────────────────────────────────┘         │
│                                                              │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│         SINGLE SOURCE OF TRUTH (Metadata Layer)             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Database Tables (Snapshots):                               │
│                                                              │
│  Core (Phase 1):                                            │
│    ✅ itx_moduler_module              Module metadata       │
│    ✅ itx_moduler_module_dependency   Dependencies          │
│    ✅ itx_moduler_model               Models/Tables         │
│    ✅ itx_moduler_model_field         Fields/Columns        │
│    ✅ itx_moduler_view                UI Views              │
│    ✅ itx_moduler_menu                Navigation            │
│    ✅ itx_moduler_action_window      Actions               │
│    ✅ itx_moduler_model_access        Security/Access       │
│                                                              │
│  Extended (Phase 2):                                        │
│    ⏳ itx_moduler_model_method        Python methods        │
│    ⏳ itx_moduler_constraint          SQL constraints       │
│    ⏳ itx_moduler_model_revision      Version history       │
│    ⏳ itx_moduler_wizard               Wizards              │
│    ⏳ itx_moduler_report               Reports              │
│    ... (22 tables total planned)                            │
│                                                              │
│  Benefits:                                                  │
│    - Database queries (fast, SQL-based)                     │
│    - Version control (track changes)                        │
│    - Validation before export                               │
│    - AI can INSERT/UPDATE via SQL                           │
│    - GUI can CRUD via Odoo ORM                              │
│                                                              │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│         CODE GENERATION (Template-Based)                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Jinja2 Templates (Professional Output):                    │
│                                                              │
│  templates/                                                 │
│    ├── manifest.py.j2         (__manifest__.py)             │
│    ├── model.py.j2            (Python class)                │
│    ├── model_init.py.j2       (models/__init__.py)          │
│    ├── view.xml.j2            (View definitions)            │
│    ├── menu.xml.j2            (Menu structure)              │
│    ├── action.xml.j2          (Actions)                     │
│    ├── security.xml.j2        (Groups & rules)              │
│    └── access.csv.j2          (Access rights)               │
│                                                              │
│  Code Generator Service:                                    │
│    1. Read snapshot records from database                   │
│    2. Prepare context data (dict/objects)                   │
│    3. Render Jinja2 templates                               │
│    4. Post-process with Black formatter (optional)          │
│    5. Package into ZIP file                                 │
│                                                              │
│  Why Jinja2?                                                │
│    ✅ Clean, readable templates                             │
│    ✅ Separation of logic vs presentation                   │
│    ✅ Easy to maintain & modify                             │
│    ✅ Professional, consistent output                       │
│    ✅ SA can edit templates without coding                  │
│    ✅ AI can understand template structure                  │
│                                                              │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│              OUTPUT (Professional Odoo Addon)                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Generated ZIP Structure:                                   │
│                                                              │
│  module_name.zip                                            │
│  └── module_name/                                           │
│      ├── __manifest__.py          (from manifest.py.j2)     │
│      ├── __init__.py               (auto-generated)         │
│      ├── models/                                            │
│      │   ├── __init__.py           (from model_init.py.j2)  │
│      │   ├── model_1.py            (from model.py.j2)       │
│      │   └── model_2.py            (from model.py.j2)       │
│      ├── views/                                             │
│      │   ├── model_1_views.xml     (from view.xml.j2)       │
│      │   ├── model_2_views.xml     (from view.xml.j2)       │
│      │   └── menus.xml              (from menu.xml.j2)      │
│      ├── security/                                          │
│      │   ├── security.xml           (from security.xml.j2)  │
│      │   └── ir.model.access.csv    (from access.csv.j2)    │
│      ├── wizards/                   (if applicable)         │
│      ├── reports/                   (if applicable)         │
│      └── static/                    (if applicable)         │
│                                                              │
│  Ready to:                                                  │
│    - Install in Odoo (unzip → addons path → install)        │
│    - Version control (Git)                                  │
│    - Deploy to production                                   │
│    - Distribute to customers                                │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🤝 SA + AI Collaboration Scenarios

### Scenario 1: AI Kickstart → SA Refine

```
User → "Create inventory management module"
  ↓
Claude API:
  - Generates E-R diagram (products, warehouses, stock moves)
  - Creates SQL INSERT statements
  - Populates snapshot tables
  ↓
System shows preview in GUI
  ↓
SA reviews and fine-tunes:
  - Adjusts field types
  - Adds custom validations
  - Designs better views
  ↓
Export → Professional addon
```

### Scenario 2: SA Design → AI Implement

```
SA creates skeleton via GUI:
  - 3 models: Customer, Invoice, Payment
  - Basic relationships only
  ↓
SA clicks "AI Complete" button
  ↓
Claude API analyzes structure:
  - Adds standard fields (created_by, dates, etc.)
  - Generates appropriate views
  - Sets up security groups
  - Creates menus & actions
  ↓
SA reviews suggestions
  ↓
Export → Complete addon
```

### Scenario 3: Iterative Development

```
SA: Load existing module (e.g., 'sale')
  ↓
Workspace populated with snapshots
  ↓
SA: "Add delivery tracking to sale.order"
  ↓
AI: Adds fields, creates new view, updates access rights
  ↓
SA: Reviews changes
  ↓
Export → Enhanced module
```

---

## 🏗️ Technical Architecture

### Data Flow

```python
# AI Path (Natural Language → SQL)
user_prompt = "Create a CRM module with contacts and companies"
↓
claude_api.generate_sql(user_prompt)
↓
[
    "INSERT INTO itx_moduler_module (name, shortdesc) VALUES ('crm_basic', 'Basic CRM');",
    "INSERT INTO itx_moduler_model (name, model, module_id) VALUES ('Contact', 'crm.contact', 1);",
    "INSERT INTO itx_moduler_model_field (name, ttype, model_id) VALUES ('name', 'char', 1);",
    ...
]
↓
env['itx.moduler.module'].execute_sql_batch(sql_statements)
↓
Snapshots created in database
```

```python
# GUI Path (Visual Designer → ORM)
user creates model via drag-drop
↓
env['itx.moduler.model'].create({
    'name': 'Contact',
    'model': 'crm.contact',
    'module_id': module.id
})
↓
user adds fields via form
↓
env['itx.moduler.model.field'].create({
    'name': 'email',
    'ttype': 'char',
    'model_id': model.id
})
↓
Snapshots created in database
```

```python
# Export Path (Snapshots → Code)
module = env['itx.moduler.module'].browse(1)
↓
code_generator.generate_zip(module)
↓
for model in module.model_ids:
    context = prepare_model_context(model)
    python_code = jinja_env.get_template('model.py.j2').render(context)
    xml_views = jinja_env.get_template('view.xml.j2').render(context)
↓
zip_file.add('models/crm_contact.py', python_code)
zip_file.add('views/crm_contact_views.xml', xml_views)
↓
Download ZIP
```

---

## 🎨 Why Jinja2 Templates?

### Before (String Concatenation)

```python
# Hard to read, maintain, and modify
l_model_fields.append('%s%s = %s(' % (TAB4, f2export.name, _get_odoo_ttype_class(f2export.ttype)))
l_model_fields.append('%sstring=\'%s\',' % (TAB8, f2export.field_description))
if f2export.help:
    l_model_fields.append('%shelp=\'%s\',' % (TAB8, f2export.help))
```

### After (Jinja2 Template)

```jinja2
{# templates/model.py.j2 #}
# -*- coding: utf-8 -*-

from odoo import api, models, fields

class {{ model.class_name }}(models.Model):
    _name = '{{ model.model }}'
    _description = '{{ model.name }}'

    {% for field in model.fields %}
    {{ field.name }} = fields.{{ field.type | capitalize }}(
        string='{{ field.label }}',
        {% if field.required %}required=True,{% endif %}
        {% if field.readonly %}readonly=True,{% endif %}
        {% if field.help %}help='{{ field.help }}',{% endif %}
    )
    {% endfor %}
```

**Benefits:**
- ✅ Looks like actual Python code
- ✅ Syntax highlighting works
- ✅ Easy to understand and modify
- ✅ SA can edit without Python knowledge
- ✅ AI can generate/understand templates
- ✅ Reusable across all modules

---

## 📊 Implementation Roadmap

### Phase 1: Foundation ✅ (Current)
- [x] Basic snapshot tables (6 core tables)
- [x] Load from Odoo functionality
- [x] String-based code generation
- [x] Export ZIP functionality
- [ ] Test & verify completeness

### Phase 2: Template Migration 🔄 (Next)
- [ ] Create Jinja2 template structure
- [ ] Refactor code generator
- [ ] Add Black formatter integration
- [ ] Improve output quality

### Phase 3: Extend Snapshots 📋 (Q1 2026)
- [ ] Add remaining snapshot tables (16-22 total)
- [ ] Version control & revision history
- [ ] Validation & state workflow
- [ ] Advanced features (wizards, reports)

### Phase 4: Visual Designer 🎨 (Q2 2026)
- [ ] Owl 2.x component framework
- [ ] Drag-drop E-R designer
- [ ] Visual field configurator
- [ ] Real-time preview

### Phase 5: AI Integration 🤖 (Q3 2026)
- [ ] Claude API service layer
- [ ] Natural language → SQL generation
- [ ] Iterative refinement
- [ ] AI-assisted code review

### Phase 6: Commercial Launch 🚀 (Q4 2026)
- [ ] ITX Security Shield integration
- [ ] Licensing & pricing tiers
- [ ] Documentation & training
- [ ] Marketing & sales

---

## 🎯 Success Criteria

### Technical
- ✅ Export generates 100% valid Odoo addon
- ✅ All elements preserved (models, fields, views, menus, security)
- ✅ Code follows Odoo best practices
- ✅ Professional formatting (PEP8, consistent XML)

### User Experience (SA)
- ✅ Intuitive visual designer
- ✅ No coding required for basic modules
- ✅ Fast iteration (design → preview → export)
- ✅ Easy to modify templates

### AI Integration
- ✅ Accurate SQL generation from text
- ✅ Understand context and relationships
- ✅ Suggest best practices
- ✅ Iterative improvement

### Business
- ✅ Reduce module development time by 80%
- ✅ Enable non-developers to create modules
- ✅ Subscription-based revenue model
- ✅ Premium AI features drive upgrades

---

## 💡 Key Insights

1. **Flexibility is Power**
   - Multiple entry points = wider audience
   - SA and AI are tools, not requirements
   - Users choose their own workflow

2. **Snapshots are Everything**
   - Single source of truth prevents conflicts
   - Database = familiar, queryable, versionable
   - Both AI and GUI work with same data

3. **Templates = Maintainability**
   - Change template once, affect all outputs
   - SA can customize without deep coding
   - Professional, consistent results

4. **AI as Assistant, Not Replacement**
   - AI accelerates, SA validates
   - Hybrid approach is best
   - Human expertise remains valuable

---

**Document Version:** 1.0
**Last Updated:** 2025-12-15
**Author:** Claude Sonnet 4.5 (with Chainaris P vision)
**Status:** ✅ Strategic Direction Approved

---

## Related Documents

- [SNAPSHOT_ARCHITECTURE.md](./SNAPSHOT_ARCHITECTURE.md) - Database design
- [CONSOLIDATION_PLAN.md](./CONSOLIDATION_PLAN.md) - Project roadmap
- [CLAUDE_API_INTEGRATION.md](./CLAUDE_API_INTEGRATION.md) - AI integration
- [SESSION_NOTES.md](../SESSION_NOTES.md) - Development history
