# ITX OCE Module Creator - Complete Architecture Design
**Date:** December 10, 2025
**Author:** Claude Code + Chainaris P
**Purpose:** Module Creator for Odoo Community Edition 19

**Full Name:** ITX OCE Module Creator
**Display Name:** ITX Module Creator
**Module Name:** `itx_oce_module_creator`
**Short Name:** Module Creator / OMC

---

## 🎯 Executive Summary

**Goal:** Create a visual module creator for Odoo CE that provides 70% of Enterprise Studio features, focusing on the most-used functionality.

**Approach:**
- Extend Odoo CE models (same pattern as Enterprise Studio and itx_code_generator)
- Store customizations as **metadata** in database (NOT real modules)
- Export metadata to real Odoo modules when ready
- **Hybrid UI: 95% XML (stable) + 5% Owl 2.x (view editor only)**

**Timeline:** 6-8 weeks for full implementation (faster with XML approach!)

**Inspired by:**
- Odoo Enterprise Studio (web_studio)
- Oracle Forms Designer (visual design tool)
- itx_code_generator (existing custom module)

---

## 🎨 Hybrid Architecture: XML + Owl 2.x

### **Design Decision: 95% XML, 5% Owl**

```
┌─────────────────────────────────────────────────────────┐
│  Simple & Stable Parts → XML + Odoo Forms (95%)        │
│  ───────────────────────────────────────────────────    │
│  ✅ Module Creator                                      │
│  ✅ Model Creator                                       │
│  ✅ Field Creator                                       │
│  ✅ Menu Creator                                        │
│  ✅ Action Creator                                      │
│  ✅ Access Rights Manager                               │
│                                                         │
│  WHY:                                                   │
│  • Stable across Odoo versions (19 → 20 → 21)          │
│  • Faster development (use built-in forms)             │
│  • Less maintenance (standard Odoo patterns)           │
│  • Proven & reliable                                   │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  Complex & Interactive Part → Owl 2.x (5%)             │
│  ───────────────────────────────────────────────────    │
│  ✅ View Editor (XML editor with syntax highlighting)   │
│  ✅ Live Preview                                        │
│                                                         │
│  WHY:                                                   │
│  • Adds real value (better UX than plain textarea)     │
│  • Worth the complexity                                │
│  • Only where Owl makes sense                          │
└─────────────────────────────────────────────────────────┘
```

### **Benefits:**

| Benefit | Description |
|---------|-------------|
| **Easy Migration** | XML parts won't break when upgrading Odoo 19→20 |
| **Fast Development** | 4 weeks faster (6-8 weeks vs 10-14 weeks) |
| **Low Maintenance** | Less custom JavaScript = less bugs |
| **Stable** | XML views are proven, stable patterns |
| **Focus Effort** | Owl only where it truly adds value |

---

## 🔑 Core Concept: Metadata vs Real Modules

### **⚠️ IMPORTANT: Understanding Module Types**

#### **1. Virtual Module (Metadata Only)** 🗄️

```python
# What ITX Module Creator creates:
virtual_module = env['itx.creator.module'].create({
    'name': 'my_custom_module',
    'display_name': 'My Custom Module',
    'description': 'My awesome module',
})

# This creates:
# ✅ Database record (metadata)
# ❌ NO files on disk
# ❌ NOT a real Odoo module
# ❌ Odoo CANNOT load it as a module
```

**What it is:**
- Database record in `itx.creator.module` table
- Contains metadata: name, description, author
- Links to customizations (models, views, menus)
- **Lives in database only**

**What it is NOT:**
- NOT a folder in addons path
- NOT loadable by Odoo
- NO Python files, NO XML files
- NO `__manifest__.py`

**Purpose:**
- Group related customizations together
- Prepare for export
- Version control (in database)
- Easy management

---

#### **2. Real Odoo Module (Files on Disk)** 📂

```bash
# What a REAL Odoo module looks like:
my_custom_module/
├── __manifest__.py      # ✅ Required!
├── __init__.py          # ✅ Required!
├── models/
│   ├── __init__.py
│   └── my_model.py      # ✅ Python code
├── views/
│   └── my_views.xml     # ✅ XML files
└── security/
    └── ir.model.access.csv
```

**What it is:**
- Folder structure on disk
- Python files (`.py`)
- XML files (`.xml`)
- `__manifest__.py` with metadata
- **Lives in filesystem**

**How Odoo loads it:**
```python
# Odoo scans addons paths:
/odoo/addons/             # Core modules
/custom_addons/           # Custom modules
  └── my_custom_module/   # ✅ Found! Load it!
```

**Purpose:**
- Actual working Odoo module
- Can be installed/upgraded
- Contains executable code
- Version controlled (git)

---

### **💡 The Relationship**

```
┌─────────────────────────────────────────────────────────┐
│  ITX Module Creator (Database)                          │
│  ────────────────────────────────                       │
│                                                          │
│  ┌────────────────────────────────────┐                 │
│  │  Virtual Module (Metadata)         │                 │
│  │  • Name: "my_sales_extension"      │                 │
│  │  • Models: [sale.order extended]   │                 │
│  │  • Views: [form, tree]             │                 │
│  │  • Menus: [Sales / My Menu]        │                 │
│  └────────────────────────────────────┘                 │
│                    │                                     │
│                    │ Export                              │
│                    ▼                                     │
│  ┌────────────────────────────────────┐                 │
│  │  Action: Generate Files            │                 │
│  │  1. Create folder                  │                 │
│  │  2. Generate __manifest__.py       │                 │
│  │  3. Generate models.py             │                 │
│  │  4. Generate views.xml             │                 │
│  │  5. Create .zip file               │                 │
│  └────────────────────────────────────┘                 │
│                    │                                     │
└────────────────────┼─────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  Filesystem                                              │
│                                                          │
│  /custom_addons/my_sales_extension/                     │
│  ├── __manifest__.py        ✅ Real file!               │
│  ├── __init__.py                                        │
│  ├── models/                                            │
│  │   ├── __init__.py                                    │
│  │   └── sale_order.py     ✅ Real Python code!        │
│  └── views/                                             │
│      └── sale_views.xml    ✅ Real XML!                │
│                                                          │
│  NOW: This is a REAL Odoo module!                      │
│  Odoo can load it, install it, use it!                 │
└─────────────────────────────────────────────────────────┘
```

---

### **📊 Comparison Table**

| Aspect | Virtual Module (Metadata) | Real Odoo Module |
|--------|---------------------------|------------------|
| **Storage** | Database (PostgreSQL) | Filesystem (disk) |
| **Format** | Records in tables | Python/XML files |
| **Created By** | ITX Module Creator | Manual coding or Export |
| **Odoo Loads It?** | ❌ No | ✅ Yes |
| **Installable?** | ❌ No | ✅ Yes |
| **Purpose** | Design & preparation | Actual working module |
| **Edit With** | ITX Module Creator UI | Text editor / IDE |
| **Version Control** | Database backups | Git |
| **Shareable** | Export required | Copy files |

---

### **🔄 Workflow Example**

```
Step 1: Design (Database/Metadata)
─────────────────────────────────
User: "I want to create a custom sales module"

ITX Module Creator:
1. Create virtual module "my_sales_extension"
2. Add field "x_priority" to sale.order
3. Create view "sale.order.form.custom"
4. Create menu "Sales / Priority Orders"

Result: All stored as METADATA in database
       NO files created yet!

┌──────────────────────────────┐
│ Database                     │
├──────────────────────────────┤
│ itx_creator_module           │
│  ├─ id: 1                    │
│  ├─ name: my_sales_extension │
│  └─ state: draft             │
│                              │
│ ir_model_fields              │
│  ├─ name: x_priority         │
│  ├─ model: sale.order        │
│  └─ creator_module_id: 1     │
│                              │
│ ir_ui_view                   │
│  ├─ name: sale.order.form    │
│  └─ creator_module_id: 1     │
└──────────────────────────────┘


Step 2: Export (Metadata → Files)
──────────────────────────────────
User: "Export my module"

ITX Module Creator:
1. Read virtual module metadata
2. Generate __manifest__.py
3. Generate models/sale_order.py
4. Generate views/sale_views.xml
5. Create .zip file

Result: Real Odoo module created!

┌──────────────────────────────┐
│ Filesystem                   │
├──────────────────────────────┤
│ my_sales_extension/          │
│  ├── __manifest__.py         │
│  ├── __init__.py             │
│  ├── models/                 │
│  │   ├── __init__.py         │
│  │   └── sale_order.py       │
│  └── views/                  │
│      └── sale_views.xml      │
└──────────────────────────────┘


Step 3: Install (Real Module)
──────────────────────────────
User: "Install module in Odoo"

Odoo:
1. Scan addons path
2. Find my_sales_extension/
3. Load __manifest__.py
4. Install module
5. Load Python code
6. Apply views

Result: Module active in Odoo!
```

---

## 🏗️ Module Structure

```
itx_oce_module_creator/              # ← Full technical name
├── __init__.py
├── __manifest__.py                  # name: "ITX Module Creator"
│
├── models/                          # Backend (Python)
│   ├── __init__.py
│   ├── creator_mixin.py            # Base mixin for tracking
│   ├── creator_module.py           # Virtual module (METADATA!)
│   ├── ir_model.py                 # Extend ir.model
│   ├── ir_model_fields.py          # Extend ir.model.fields
│   ├── ir_ui_view.py               # Extend ir.ui.view
│   ├── ir_ui_menu.py               # Extend ir.ui.menu
│   ├── ir_actions.py               # Extend ir.actions.*
│   ├── base_automation.py          # Extend base.automation
│   ├── res_groups.py               # Extend res.groups
│   ├── ir_model_access.py          # Extend ir.model.access
│   └── ir_rule.py                  # Extend ir.rule
│
├── controllers/                     # HTTP Controllers
│   ├── __init__.py
│   └── main.py                     # API endpoints
│
├── wizard/                          # Wizards
│   ├── __init__.py
│   ├── export_module_wizard.py     # Export metadata → files
│   ├── field_creator_wizard.py
│   └── model_creator_wizard.py
│
├── static/src/                      # Frontend (JavaScript/Owl 2.x)
│   ├── js/
│   │   ├── creator_service.js      # Core service
│   │   ├── creator_menu.js         # Systray icon
│   │   ├── field_editor/           # Field creator UI
│   │   ├── view_editor/            # View editor UI
│   │   ├── menu_editor/            # Menu editor UI
│   │   ├── model_creator/          # Model creator UI
│   │   └── utils.js
│   │
│   ├── scss/
│   │   ├── creator.scss
│   │   ├── field_editor.scss
│   │   ├── view_editor.scss
│   │   └── menu_editor.scss
│   │
│   └── xml/
│       └── templates.xml
│
├── views/                           # XML Views
│   ├── assets.xml                  # Asset bundles
│   ├── creator_module_views.xml    # Virtual module views
│   ├── ir_model_views.xml
│   ├── ir_ui_view_views.xml
│   ├── ir_ui_menu_views.xml
│   ├── creator_menu.xml            # Main menu
│   └── res_config_settings_views.xml
│
├── security/
│   ├── ir.model.access.csv
│   └── creator_security.xml
│
└── data/
    └── creator_data.xml
```

---

## 📦 Core Models & Extensions

### **1. itx.creator.mixin (Abstract Model)**

**Purpose:** Track all customizations created with ITX Module Creator

```python
# models/creator_mixin.py
from odoo import models, fields, api
import uuid

class CreatorMixin(models.AbstractModel):
    """
    Mixin to track ITX Module Creator customizations.

    IMPORTANT: This tracks METADATA only!
    - Records are in DATABASE
    - NOT real Odoo module files
    - Need to EXPORT to become real module
    """
    _name = 'itx.creator.mixin'
    _description = 'ITX Module Creator Mixin'

    itx_creator_created = fields.Boolean(
        string='Created by ITX Creator',
        default=False,
        help='Indicates this record was created using ITX Module Creator'
    )

    itx_creator_module_id = fields.Many2one(
        'itx.creator.module',
        string='ITX Creator Module',
        help='The virtual module this customization belongs to',
        ondelete='cascade'
    )

    itx_creator_created_date = fields.Datetime(
        string='Creation Date',
        readonly=True
    )

    itx_creator_xmlid = fields.Char(
        string='XML ID',
        help='XML ID for export',
        readonly=True
    )

    @api.model_create_multi
    def create(self, vals_list):
        """
        Override create to track ITX Creator records.

        IMPORTANT: This creates DATABASE RECORDS (metadata) only!
        NOT creating real module files!
        """
        res = super().create(vals_list)

        if self.env.context.get('itx_creator'):
            for record in res:
                # Generate XML ID for future export
                xmlid = self._generate_creator_xmlid(record)

                record.write({
                    'itx_creator_created': True,
                    'itx_creator_created_date': fields.Datetime.now(),
                    'itx_creator_xmlid': xmlid,
                })

                # Create ir.model.data for tracking
                record._create_creator_model_data(xmlid)

        return res

    def _generate_creator_xmlid(self, record):
        """Generate unique XML ID for export"""
        module_name = record.itx_creator_module_id.name if record.itx_creator_module_id else 'itx_creator'
        unique_id = uuid.uuid4().hex[:8]
        return f"{module_name}_{self._table}_{unique_id}"

    def _create_creator_model_data(self, xmlid):
        """
        Create ir.model.data entry for tracking.
        This is METADATA for future export!
        """
        IrModelData = self.env['ir.model.data']

        module_name = self.itx_creator_module_id.name if self.itx_creator_module_id else 'itx_creator_custom'

        # Check if already exists
        existing = IrModelData.search([
            ('model', '=', self._name),
            ('res_id', '=', self.id),
        ])

        if not existing:
            IrModelData.create({
                'name': xmlid,
                'model': self._name,
                'res_id': self.id,
                'module': module_name,
                'noupdate': True,
            })
```

**Key Points:**
- ✅ Tracks customizations in DATABASE
- ✅ Generates XML IDs for future export
- ✅ Links to virtual module
- ❌ Does NOT create files
- ❌ Does NOT create real Odoo module

---

### **2. itx.creator.module (New Model - VIRTUAL MODULE!)**

**Purpose:** Manage virtual modules (metadata only!)

```python
# models/creator_module.py
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import re

class CreatorModule(models.Model):
    """
    ITX Module Creator - Virtual Module

    ⚠️ IMPORTANT: This is NOT a real Odoo module!

    What it is:
    - Database record (metadata)
    - Groups related customizations
    - Prepares for export

    What it is NOT:
    - NOT a folder in addons path
    - NOT loadable by Odoo
    - NO Python files, NO XML files

    To make it a real module: Use "Export Module" action
    """
    _name = 'itx.creator.module'
    _description = 'ITX Creator Module (Virtual)'
    _order = 'name'

    # =====================================
    # Metadata Fields
    # =====================================

    name = fields.Char(
        string='Technical Name',
        required=True,
        help='Module technical name (e.g., my_custom_sales)\n'
             'IMPORTANT: This is metadata only! Not a real module yet!'
    )

    display_name = fields.Char(
        string='Display Name',
        required=True,
        help='Human-readable name'
    )

    description = fields.Text(
        string='Description',
        help='Module description'
    )

    author = fields.Char(
        string='Author',
        default=lambda self: self.env.user.name
    )

    website = fields.Char(
        string='Website'
    )

    category = fields.Char(
        string='Category',
        default='Customizations'
    )

    version = fields.Char(
        string='Version',
        default='1.0.0'
    )

    license = fields.Selection([
        ('LGPL-3', 'LGPL-3'),
        ('GPL-3', 'GPL-3'),
        ('MIT', 'MIT'),
        ('Proprietary', 'Proprietary'),
    ], string='License', default='LGPL-3')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('ready', 'Ready for Export'),
        ('exported', 'Exported'),
    ], default='draft', required=True,
       help='State of this VIRTUAL module:\n'
            '- Draft: Still being designed\n'
            '- Ready: Can be exported to real module\n'
            '- Exported: Real module files generated')

    # =====================================
    # Relations (What this module contains)
    # =====================================

    model_ids = fields.One2many(
        'ir.model',
        'itx_creator_module_id',
        string='Custom Models',
        help='Models created in this virtual module'
    )

    field_ids = fields.One2many(
        'ir.model.fields',
        'itx_creator_module_id',
        string='Custom Fields',
        help='Fields added in this virtual module'
    )

    view_ids = fields.One2many(
        'ir.ui.view',
        'itx_creator_module_id',
        string='Custom Views',
        help='Views created in this virtual module'
    )

    menu_ids = fields.One2many(
        'ir.ui.menu',
        'itx_creator_module_id',
        string='Custom Menus',
        help='Menus created in this virtual module'
    )

    action_ids = fields.One2many(
        'ir.actions.act_window',
        'itx_creator_module_id',
        string='Custom Actions',
        help='Actions created in this virtual module'
    )

    # =====================================
    # Export Information
    # =====================================

    exported_file = fields.Binary(
        string='Exported Module File',
        readonly=True,
        help='ZIP file of exported module'
    )

    exported_filename = fields.Char(
        string='Exported Filename',
        readonly=True
    )

    exported_date = fields.Datetime(
        string='Export Date',
        readonly=True
    )

    exported_path = fields.Char(
        string='Export Path',
        help='Path where module was exported (if saved to disk)'
    )

    # Link to real Odoo module (after install)
    odoo_module_id = fields.Many2one(
        'ir.module.module',
        string='Real Odoo Module',
        readonly=True,
        help='Link to the actual Odoo module after installation'
    )

    # =====================================
    # Statistics
    # =====================================

    customization_count = fields.Integer(
        compute='_compute_customization_count',
        string='Total Customizations',
        help='Total number of customizations in this virtual module'
    )

    @api.depends('model_ids', 'field_ids', 'view_ids', 'menu_ids', 'action_ids')
    def _compute_customization_count(self):
        for record in self:
            record.customization_count = (
                len(record.model_ids) +
                len(record.field_ids) +
                len(record.view_ids) +
                len(record.menu_ids) +
                len(record.action_ids)
            )

    # =====================================
    # Constraints
    # =====================================

    @api.constrains('name')
    def _check_name(self):
        """Validate module name format"""
        for record in self:
            if not re.match(r'^[a-z][a-z0-9_]*$', record.name):
                raise ValidationError(_(
                    'Module name must:\n'
                    '- Start with lowercase letter\n'
                    '- Contain only lowercase letters, numbers, and underscores\n'
                    '- Example: my_custom_module'
                ))

    # =====================================
    # Actions
    # =====================================

    def action_export_module(self):
        """
        Export virtual module to real Odoo module.

        This generates actual files:
        - __manifest__.py
        - __init__.py
        - models/*.py
        - views/*.xml
        - security/*.csv

        Returns: Wizard to configure export
        """
        self.ensure_one()

        if self.customization_count == 0:
            raise ValidationError(_(
                'Cannot export empty module!\n'
                'Please add at least one customization (model, field, view, etc.)'
            ))

        return {
            'type': 'ir.actions.act_window',
            'name': 'Export Module',
            'res_model': 'itx.creator.export.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_creator_module_id': self.id,
                'default_module_name': self.name,
            }
        }

    def action_view_customizations(self):
        """View all customizations in this module"""
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': f'Customizations: {self.display_name}',
            'res_model': 'itx.creator.customization.view',  # Custom tree view
            'view_mode': 'tree,form',
            'domain': [('itx_creator_module_id', '=', self.id)],
            'context': {'default_itx_creator_module_id': self.id}
        }

    def action_mark_ready(self):
        """Mark module as ready for export"""
        self.write({'state': 'ready'})

    def action_reset_to_draft(self):
        """Reset module to draft state"""
        self.write({'state': 'draft'})
```

**Key Concepts:**

1. **Virtual Module = Metadata**
   ```python
   # When you create a virtual module:
   module = env['itx.creator.module'].create({
       'name': 'my_module',
       'display_name': 'My Module',
   })

   # What happens:
   # ✅ Database record created
   # ❌ NO folder created
   # ❌ NO files created
   # ❌ Odoo cannot load it
   ```

2. **Real Module = Files**
   ```python
   # When you export:
   module.action_export_module()

   # What happens:
   # ✅ Generates __manifest__.py
   # ✅ Generates Python files
   # ✅ Generates XML files
   # ✅ Creates .zip file
   # → NOW it's a real Odoo module!
   ```

---

### **3. Export Wizard (Metadata → Real Module)**

```python
# wizard/export_module_wizard.py
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import os
import zipfile
import io

class ExportModuleWizard(models.TransientModel):
    """
    Export virtual module (metadata) to real Odoo module (files).

    Process:
    1. Read metadata from database
    2. Generate Python files
    3. Generate XML files
    4. Create __manifest__.py
    5. Package as .zip file
    """
    _name = 'itx.creator.export.wizard'
    _description = 'Export Virtual Module to Real Module'

    creator_module_id = fields.Many2one(
        'itx.creator.module',
        string='Virtual Module',
        required=True,
        help='The virtual module (metadata) to export'
    )

    module_name = fields.Char(
        string='Module Name',
        required=True
    )

    export_path = fields.Char(
        string='Export Path',
        help='Path to save module (leave empty for .zip download only)'
    )

    include_demo_data = fields.Boolean(
        string='Include Demo Data',
        default=False
    )

    auto_install = fields.Boolean(
        string='Auto-install after export',
        default=False,
        help='Automatically install module after exporting to filesystem'
    )

    def action_export(self):
        """
        Main export action: Metadata → Real Module Files
        """
        self.ensure_one()

        # 1. Validate
        if not self.creator_module_id.customization_count:
            raise ValidationError(_('No customizations to export!'))

        # 2. Generate files
        module_files = self._generate_module_files()

        # 3. Create .zip
        zip_data = self._create_zip(module_files)

        # 4. Save or download
        if self.export_path:
            self._save_to_filesystem(module_files)

        # 5. Update virtual module
        self.creator_module_id.write({
            'state': 'exported',
            'exported_file': zip_data,
            'exported_filename': f'{self.module_name}.zip',
            'exported_date': fields.Datetime.now(),
            'exported_path': self.export_path or False,
        })

        # 6. Auto-install if requested
        if self.auto_install and self.export_path:
            self._install_module()

        # 7. Return download action
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/itx.creator.module/{self.creator_module_id.id}/exported_file/{self.creator_module_id.exported_filename}',
            'target': 'new',
        }

    def _generate_module_files(self):
        """
        Generate all module files from metadata.

        Returns: dict of {filename: content}
        """
        files = {}

        # 1. __manifest__.py
        files['__manifest__.py'] = self._generate_manifest()

        # 2. __init__.py (root)
        files['__init__.py'] = self._generate_root_init()

        # 3. models/__init__.py
        files['models/__init__.py'] = self._generate_models_init()

        # 4. models/*.py (for each custom model)
        for model in self.creator_module_id.model_ids:
            filename = f'models/{model.model.replace(".", "_")}.py'
            files[filename] = self._generate_model_file(model)

        # 5. views/*.xml (for each view)
        if self.creator_module_id.view_ids:
            files['views/views.xml'] = self._generate_views_xml()

        # 6. views/menus.xml (for menus)
        if self.creator_module_id.menu_ids:
            files['views/menus.xml'] = self._generate_menus_xml()

        # 7. security/ir.model.access.csv
        files['security/ir.model.access.csv'] = self._generate_access_rights()

        return files

    def _generate_manifest(self):
        """Generate __manifest__.py content"""
        module = self.creator_module_id

        return f'''# -*- coding: utf-8 -*-
{{
    'name': '{module.display_name}',
    'summary': '{module.description or ""}',
    'description': \'\'\'{module.description or ""}\'\'\',
    'author': '{module.author}',
    'website': '{module.website or ""}',
    'category': '{module.category}',
    'version': '{module.version}',
    'license': '{module.license}',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
{self._get_data_files_list()}
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}}
'''

    def _generate_model_file(self, model):
        """
        Generate Python model file from metadata.

        This converts database records (metadata) into actual Python code!
        """
        fields_code = []

        # Get all custom fields for this model
        custom_fields = self.env['ir.model.fields'].search([
            ('model_id', '=', model.id),
            ('itx_creator_created', '=', True)
        ])

        for field in custom_fields:
            field_def = self._generate_field_definition(field)
            fields_code.append(field_def)

        fields_str = '\n    '.join(fields_code)

        return f'''# -*- coding: utf-8 -*-
from odoo import models, fields, api

class {model.name.replace(".", "")}(models.Model):
    _name = '{model.model}'
    _description = '{model.name}'

    {fields_str}
'''

    def _generate_field_definition(self, field):
        """Convert field metadata to Python code"""
        field_type = field.ttype.capitalize()

        params = [f"string='{field.field_description}'"]

        if field.required:
            params.append("required=True")
        if field.readonly:
            params.append("readonly=True")
        if field.help:
            params.append(f"help='{field.help}'")

        params_str = ', '.join(params)

        return f"{field.name} = fields.{field_type}({params_str})"

    # ... more helper methods ...
```

**Key Process:**

```
Virtual Module (Database)  →  Real Module (Files)
═══════════════════════════    ═══════════════════

Database Records:              Generated Files:
├─ itx.creator.module         ├─ __manifest__.py
├─ ir.model                   ├─ __init__.py
├─ ir.model.fields           ├─ models/
├─ ir.ui.view                │   ├─ __init__.py
├─ ir.ui.menu                │   └─ my_model.py
└─ ir.actions.act_window     ├─ views/
                             │   ├─ views.xml
                             │   └─ menus.xml
                             └─ security/
                                 └─ ir.model.access.csv

     Metadata                      Real Code!
```

---

## 📊 Features Scope

### ✅ **Phase 1: MVP Features (70% coverage)**

| Feature | Priority | Complexity | Time | Notes |
|---------|----------|------------|------|-------|
| **Field Creator** | 🔴 Critical | Medium | 2 weeks | Creates metadata, not real fields yet |
| **View Editor (XML)** | 🔴 Critical | Medium | 2 weeks | Stores XML as metadata |
| **Menu Editor** | 🔴 Critical | Low | 1 week | Creates menu metadata |
| **Simple Model Creator** | 🟡 High | Medium | 2 weeks | Virtual models (metadata) |
| **Export Module** | 🔴 Critical | High | 2 weeks | **Converts metadata → real files** |
| **Basic Automated Actions** | 🟡 High | Medium | 1.5 weeks | Metadata automation rules |
| **Access Rights Manager** | 🟡 High | Low | 1 week | Metadata access rights |

### 🚧 **Phase 2: Enhanced Features (Optional)**

| Feature | Priority | Complexity | Time |
|---------|----------|------------|------|
| **Report Designer** | 🟢 Medium | High | 2 weeks |
| **Approval Workflow** | 🟢 Medium | High | 2 weeks |
| **Git Integration** | 🟢 Medium | Medium | 1.5 weeks |

---

## 🔄 Complete Workflow

### **Scenario: Creating a Custom Sales Module**

```
┌─────────────────────────────────────────────────────────────┐
│ Step 1: Create Virtual Module (METADATA ONLY)              │
└─────────────────────────────────────────────────────────────┘

User Action:
- Open "ITX Module Creator"
- Click "New Module"
- Name: "my_sales_extension"
- Display Name: "My Sales Extension"
- Click "Save"

What Happens:
┌──────────────────────────────────┐
│ Database (PostgreSQL)            │
├──────────────────────────────────┤
│ Table: itx_creator_module        │
│   id: 1                          │
│   name: my_sales_extension       │
│   state: draft                   │
│   customization_count: 0         │
└──────────────────────────────────┘

✅ Metadata saved in database
❌ NO files created
❌ NOT a real Odoo module yet


┌─────────────────────────────────────────────────────────────┐
│ Step 2: Add Custom Field (METADATA)                        │
└─────────────────────────────────────────────────────────────┘

User Action:
- Select module "my_sales_extension"
- Click "Add Field"
- Model: sale.order
- Field Name: x_priority
- Field Type: Selection
- Options: [('low', 'Low'), ('high', 'High')]
- Click "Create"

What Happens:
┌──────────────────────────────────┐
│ Database                         │
├──────────────────────────────────┤
│ Table: ir_model_fields           │
│   name: x_priority               │
│   model_id: sale.order           │
│   ttype: selection              │
│   itx_creator_created: True      │
│   itx_creator_module_id: 1       │
│                                  │
│ Table: itx_creator_module        │
│   customization_count: 1  ← +1   │
└──────────────────────────────────┘

✅ Field metadata saved
❌ Field NOT added to sale.order yet!
❌ Must export first!


┌─────────────────────────────────────────────────────────────┐
│ Step 3: Create Custom View (METADATA)                      │
└─────────────────────────────────────────────────────────────┘

User Action:
- Click "Create View"
- Model: sale.order
- Type: form
- Edit XML:
  <field name="x_priority" widget="priority"/>
- Click "Save"

What Happens:
┌──────────────────────────────────┐
│ Database                         │
├──────────────────────────────────┤
│ Table: ir_ui_view                │
│   name: sale.order.form.custom   │
│   model: sale.order              │
│   arch: <xpath>...</xpath>       │
│   itx_creator_created: True      │
│   itx_creator_module_id: 1       │
│                                  │
│ Table: itx_creator_module        │
│   customization_count: 2  ← +1   │
└──────────────────────────────────┘

✅ View XML saved as metadata
❌ View NOT applied to Odoo yet!


┌─────────────────────────────────────────────────────────────┐
│ Step 4: Export Module (METADATA → REAL FILES!) 🎉          │
└─────────────────────────────────────────────────────────────┘

User Action:
- Click "Export Module"
- Choose export path: /custom_addons/
- Click "Export"

What Happens:

1. Read Metadata from Database:
   ┌──────────────────────────────────┐
   │ Read from database:              │
   │ - Module info                    │
   │ - Fields (x_priority)            │
   │ - Views (form view)              │
   │ - Menus                          │
   └──────────────────────────────────┘

2. Generate Files:
   ┌──────────────────────────────────┐
   │ Create Python/XML files:         │
   │                                  │
   │ my_sales_extension/              │
   │ ├─ __manifest__.py  ← Generated! │
   │ ├─ __init__.py                   │
   │ ├─ models/                       │
   │ │  ├─ __init__.py                │
   │ │  └─ sale_order.py ← Generated! │
   │ └─ views/                        │
   │    └─ views.xml    ← Generated!  │
   └──────────────────────────────────┘

3. Write to Filesystem:
   /custom_addons/my_sales_extension/
   ├── __manifest__.py      ✅ REAL FILE!
   ├── __init__.py
   ├── models/
   │   ├── __init__.py
   │   └── sale_order.py   ✅ REAL PYTHON CODE!
   └── views/
       └── views.xml       ✅ REAL XML!

4. Update Database:
   ┌──────────────────────────────────┐
   │ Table: itx_creator_module        │
   │   state: exported    ← Changed!  │
   │   exported_date: 2025-12-10      │
   │   exported_file: <binary>        │
   └──────────────────────────────────┘

✅ Real Odoo module created!
✅ Files written to disk!
✅ Module ready to install!


┌─────────────────────────────────────────────────────────────┐
│ Step 5: Install Real Module in Odoo                        │
└─────────────────────────────────────────────────────────────┘

User Action:
- Go to Apps
- Update Apps List
- Search "My Sales Extension"
- Click "Install"

What Happens:

1. Odoo scans filesystem:
   ✅ Found: /custom_addons/my_sales_extension/

2. Odoo loads module:
   ✅ Read __manifest__.py
   ✅ Import models/sale_order.py
   ✅ Load views/views.xml

3. Odoo applies customizations:
   ✅ Add field x_priority to sale.order
   ✅ Apply form view inheritance
   ✅ Now sale.order has priority field!

4. Update database:
   ┌──────────────────────────────────┐
   │ Table: ir_module_module          │
   │   name: my_sales_extension       │
   │   state: installed   ✅           │
   │                                  │
   │ Table: ir_model_fields           │
   │   (x_priority now active)        │
   │                                  │
   │ Link virtual → real:             │
   │ itx_creator_module.odoo_module_id│
   │   → ir_module_module.id          │
   └──────────────────────────────────┘

🎉 SUCCESS! Real module installed and working!


┌─────────────────────────────────────────────────────────────┐
│ Final State                                                 │
└─────────────────────────────────────────────────────────────┘

Database:
┌──────────────────────────────────┐
│ Virtual Module (Metadata)        │
│ - Still exists                   │
│ - state: exported                │
│ - Linked to real module          │
└──────────────────────────────────┘

Filesystem:
┌──────────────────────────────────┐
│ Real Module (Files)              │
│ - my_sales_extension/            │
│ - Loadable by Odoo               │
│ - Installed and active           │
└──────────────────────────────────┘

Odoo Runtime:
┌──────────────────────────────────┐
│ Module Active                    │
│ - sale.order has x_priority      │
│ - Custom view applied            │
│ - Everything works!              │
└──────────────────────────────────┘
```

---

## 🎓 Key Design Decisions

### **1. Why Metadata Approach?**

**Advantages:**
- ✅ **Easy to Edit**: Change metadata in database, no file editing
- ✅ **Version Control**: Database backups = version history
- ✅ **No File Conflicts**: Multiple users can work simultaneously
- ✅ **Rollback Easy**: Restore database = restore customizations
- ✅ **Export When Ready**: Only generate files when satisfied

**Disadvantages:**
- ⚠️ Not a "real" module until exported
- ⚠️ Extra step (export) required
- ⚠️ Database-dependent

### **2. Why Not Create Real Module Directly?**

**If we created files directly:**
```python
# ❌ Bad approach:
def create_field(name, model):
    # Generate Python file immediately
    file_path = f"/addons/my_module/models/{model}.py"
    with open(file_path, 'w') as f:
        f.write(f"class {model}:\n    {name} = fields.Char()")

    # Problems:
    # - File conflicts (multiple users)
    # - No undo (file overwritten)
    # - Git conflicts
    # - Odoo reload required immediately
    # - Testing difficult
```

**With metadata approach:**
```python
# ✅ Good approach:
def create_field(name, model):
    # Save to database (metadata)
    field = env['ir.model.fields'].create({
        'name': name,
        'model_id': model,
        'itx_creator_created': True,
    })

    # Benefits:
    # + Easy to edit (database update)
    # + No file conflicts
    # + Can undo (database rollback)
    # + Export when ready
    # + Test before export
```

### **3. Hybrid Model**

```
Design Phase:              Export Phase:           Production:
──────────────            ──────────────          ──────────────
Database (Metadata)   →   Filesystem (Files)  →   Installed Module
┌─────────────────┐       ┌─────────────────┐     ┌─────────────────┐
│ Virtual Module  │       │ Real Module     │     │ Active Module   │
│ • Draft         │──────▶│ • Files created │────▶│ • Installed     │
│ • Easy to edit  │       │ • Loadable      │     │ • Working       │
│ • No conflicts  │       │ • Git-ready     │     │ • In production │
└─────────────────┘       └─────────────────┘     └─────────────────┘
     Flexible                  Standard                  Stable
```

---

## 📅 Implementation Roadmap

### **Phase 1: Foundation (Weeks 1-2)**

**Week 1:**
- ✅ Module structure (itx_oce_module_creator)
- ✅ creator.mixin (tracking metadata)
- ✅ itx.creator.module model (virtual modules)
- ✅ Basic UI (menu, forms)
- ✅ Security & access rights

**Deliverable:** Can create virtual modules (metadata) in database

---

**Week 2:**
- ✅ Extend core models (ir.model, ir.model.fields, ir.ui.view, etc.)
- ✅ API controllers (/itx_creator/*)
- ✅ Creator service (JavaScript)
- ✅ Systray menu icon

**Deliverable:** Core infrastructure complete

---

### **Phase 2: Field Creator (Weeks 3-4)**

**Week 3:**
- ✅ Field creator wizard (backend)
- ✅ Support basic types (Char, Text, Integer, Float, Boolean, Date)
- ✅ Field validation
- ✅ Metadata storage

**Week 4:**
- ✅ Field creator UI (Owl component)
- ✅ Relational fields (Many2one, One2many, Many2many)
- ✅ Field options (required, readonly, help, default)
- ✅ Testing

**Deliverable:** Can create fields (as metadata)

---

### **Phase 3: View Editor (Weeks 5-6)**

**Week 5:**
- ✅ XML editor integration (Monaco/Ace)
- ✅ Syntax highlighting for XML
- ✅ View templates (form, tree, search, kanban)
- ✅ View metadata storage

**Week 6:**
- ✅ Live preview (optional)
- ✅ XML validation
- ✅ Save & reload
- ✅ Testing

**Deliverable:** Can create/edit views (as metadata)

---

### **Phase 4: Menu & Actions (Week 7)**

- ✅ Menu creator UI
- ✅ Menu tree structure
- ✅ Action creator (act_window)
- ✅ Link menu ↔ action
- ✅ Metadata storage
- ✅ Testing

**Deliverable:** Can create menus & actions (as metadata)

---

### **Phase 5: Model Creator (Weeks 8-9)**

**Week 8:**
- ✅ Model creator wizard
- ✅ Model options (abstract, transient, etc.)
- ✅ Auto-generate default fields (name, active, sequence)
- ✅ Metadata storage

**Week 9:**
- ✅ Model creator UI
- ✅ Complete workflow: Model → Fields → Views → Menu
- ✅ Testing

**Deliverable:** Can create complete models (as metadata)

---

### **Phase 6: Export Module (Weeks 10-11)** 🎯 **CRITICAL!**

**Week 10:**
- ✅ Export wizard UI
- ✅ __manifest__.py generator
- ✅ Python code generator (models)
- ✅ XML generator (views, menus)
- ✅ CSV generator (access rights)

**Week 11:**
- ✅ ZIP file creation
- ✅ Download module
- ✅ Save to filesystem (optional)
- ✅ Auto-install (optional)
- ✅ Link virtual ↔ real module
- ✅ Testing

**Deliverable:** **Can convert metadata → real Odoo module!** ✅

---

### **Phase 7: Polish (Weeks 12-14)**

**Week 12:**
- ✅ Bug fixes
- ✅ UI/UX improvements
- ✅ Performance optimization

**Week 13:**
- ✅ Documentation (user guide)
- ✅ Developer documentation
- ✅ Video tutorials

**Week 14:**
- ✅ Final testing
- ✅ Demo environment
- ✅ Release preparation

---

## 📊 Success Metrics

| Metric | Target |
|--------|--------|
| **Virtual Module Creation** | < 1 minute |
| **Field Creation (Metadata)** | < 30 seconds |
| **View Creation (Metadata)** | < 2 minutes |
| **Menu Creation (Metadata)** | < 1 minute |
| **Export Time (Metadata → Files)** | < 10 seconds |
| **User Satisfaction** | > 4/5 stars |

---

## 🎯 Summary

### **ITX OCE Module Creator** = Metadata-First Design Tool

**What it does:**
1. ✅ Stores customizations as **metadata** (database records)
2. ✅ Provides visual UI to design modules
3. ✅ **Exports metadata to real Odoo modules** (files)

**What it does NOT do:**
1. ❌ Does NOT create real modules directly
2. ❌ Does NOT write files immediately
3. ❌ Does NOT auto-install (until export)

**Key Benefits:**
- ✅ Safe design environment (metadata)
- ✅ Easy editing (database updates)
- ✅ No file conflicts
- ✅ Export when ready
- ✅ Standard Odoo modules as output

**Ready to start implementation!** 🚀

---

**End of Architecture Document**
