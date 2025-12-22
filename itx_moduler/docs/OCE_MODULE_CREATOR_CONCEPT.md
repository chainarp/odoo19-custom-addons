# ITX OCE Module Creator

Visual tool for creating Odoo Community Edition modules without coding.

## Overview

ITX Module Creator allows you to create Odoo modules visually:
- **Metadata-First**: Save customizations as database records (virtual modules)
- **Export to Files**: Convert metadata to real Odoo modules when ready
- **No Coding**: Design models, fields, views, menus visually
- **Hybrid UI**: 95% XML (stable) + 5% Owl 2.x (view editor only)

## Installation

### Method 1: Update Module List (Web UI)

1. Go to Odoo Apps menu
2. Click "Update Apps List"
3. Search for "ITX Module Creator"
4. Click Install

### Method 2: Command Line

```bash
cd /home/chainarp/PycharmProjects/odoo19
.venv/bin/python odoo/odoo-bin -c odoo/debian/odoo.conf -d odoo19 -i itx_oce_module_creator --stop-after-init
```

## Usage

### 1. Create Virtual Module

1. Go to **Module Creator** menu
2. Click **Virtual Modules**
3. Click **Create** button
4. Fill in module details:
   - **Technical Name**: `my_custom_module` (lowercase, underscores only)
   - **Display Name**: "My Custom Module"
   - **Description**: What your module does
   - **Author**: Your name
   - **Version**: 1.0.0

### 2. What is a Virtual Module?

⚠️ **IMPORTANT**: Virtual modules are NOT real Odoo modules!

**Virtual Module (Metadata)**:
- Database record only
- NOT in addons path
- NOT loadable by Odoo
- Can be edited anytime
- No file conflicts

**Real Module (Files)**:
- Python/XML files on filesystem
- In addons path
- Loadable by Odoo
- Created by "Export" action

### 3. Workflow

```
1. CREATE → Save to Database (Metadata)
   - State: Draft
   - Edit as much as you want

2. MARK READY → Validate & Prepare
   - State: Ready
   - Ready for export

3. EXPORT → Generate Files
   - State: Exported
   - Creates real module files:
     * __manifest__.py
     * __init__.py
     * models/*.py
     * views/*.xml
     * security/*.csv
```

## Features

### Phase 1 (Current)
- ✅ Virtual Module Creator
- ✅ Metadata tracking (creator_mixin)
- ✅ State workflow (draft → ready → exported)
- ⏳ Model Creator
- ⏳ Field Creator
- ⏳ Menu Creator
- ⏳ Export functionality

### Phase 2 (Planned)
- View Editor (Owl 2.x)
- Access Rights Manager
- Action Creator
- Advanced export options

## Architecture

### Models

1. **itx.creator.module**: Virtual module (metadata)
   - `name`: Technical name
   - `display_name_custom`: Human-readable name
   - `state`: draft, ready, exported
   - `customization_count`: Number of customizations

2. **itx.creator.mixin**: Abstract mixin for tracking
   - `itx_creator_created`: Boolean flag
   - `itx_creator_module_id`: Link to virtual module
   - `itx_creator_xmlid`: XML ID for export

### Security Groups

- **ITX Creator User**: Can create virtual modules
- **ITX Creator Manager**: Can export to real modules

## Technical Details

### Table Naming Convention
All tables use `itx_` prefix:
- `itx.creator.module` → `itx_creator_module` table
- `itx.creator.mixin` → abstract model (no table)

### Why Metadata-First?

**Benefits:**
1. **Easy Editing**: No file conflicts, rollback anytime
2. **Version Control**: Track changes in database
3. **Validation**: Check before generating files
4. **Export Once**: Generate files only when ready

**Inspired By:**
- Oracle Forms Designer
- Odoo Enterprise Studio
- Clean room implementation (no copied code)

### Why Hybrid (XML + Owl)?

**95% XML** (Simple Forms):
- Module creator
- Model creator
- Field creator
- Menu creator
- Stable across Odoo versions

**5% Owl 2.x** (Complex UI):
- View editor only
- Syntax highlighting
- Live preview
- Adds real UX value

## Development Status

- Module: `itx_oce_module_creator`
- Version: 19.0.1.0.0
- License: LGPL-3
- Status: Phase 1 in progress

## Files Created

```
itx_oce_module_creator/
├── __init__.py
├── __manifest__.py
├── README.md
├── models/
│   ├── __init__.py
│   ├── creator_mixin.py      # Tracking mixin
│   └── creator_module.py     # Virtual module model
├── views/
│   ├── creator_menu.xml      # Main menu
│   └── creator_module_views.xml  # Form/tree/search views
├── security/
│   ├── creator_security.xml  # Security groups
│   └── ir.model.access.csv   # Access rights
├── wizard/
│   └── __init__.py           # Export wizard (Phase 2)
└── static/
    └── description/
        └── (icon.png needed)
```

## Next Steps

1. Install module
2. Test virtual module creation
3. Extend core models (ir.model, ir.model.fields)
4. Create additional views (model/field creators)
5. Implement export functionality (Phase 2)

## Notes

- All syntax validated (Python + XML)
- Ready for testing
- Icon placeholder needed
- Export wizard in Phase 2
