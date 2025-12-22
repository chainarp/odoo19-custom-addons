# Studio CE - Complete Architecture Design
**Date:** December 10, 2025
**Author:** Claude Code + Chainaris P
**Purpose:** Community Edition Studio for Odoo 19

---

## 🎯 Executive Summary

**Goal:** Create a lightweight Studio for Odoo CE that provides 70% of Enterprise Studio features, focusing on the most-used functionality.

**Approach:** Extend Odoo CE models (same pattern as Enterprise Studio and itx_code_generator)

**Timeline:** 10-14 weeks for full implementation

**Inspired by:**
- Odoo Enterprise Studio (web_studio)
- itx_code_generator (existing custom module)

---

## 📊 Features Scope

### ✅ **Phase 1: MVP Features (70% coverage)**

| Feature | Priority | Complexity | Time |
|---------|----------|------------|------|
| **Field Creator** | 🔴 Critical | Medium | 2 weeks |
| **View Editor (XML)** | 🔴 Critical | Medium | 2 weeks |
| **Menu Editor** | 🔴 Critical | Low | 1 week |
| **Simple Model Creator** | 🟡 High | Medium | 2 weeks |
| **Basic Automated Actions** | 🟡 High | Medium | 1.5 weeks |
| **Access Rights Manager** | 🟡 High | Low | 1 week |

### 🚧 **Phase 2: Enhanced Features (Optional)**

| Feature | Priority | Complexity | Time |
|---------|----------|------------|------|
| **Report Designer** | 🟢 Medium | High | 2 weeks |
| **Approval Workflow** | 🟢 Medium | High | 2 weeks |
| **Export Module** | 🟢 Medium | Medium | 1.5 weeks |

### ❌ **Out of Scope (Too Complex)**

- Drag & Drop Visual Editor (Enterprise-only complexity)
- Real-time collaborative editing
- AI-powered suggestions
- Advanced view inheritance editor

---

## 🏗️ Module Structure

```
studio_ce/
├── __init__.py
├── __manifest__.py
│
├── models/                      # Backend (Python)
│   ├── __init__.py
│   ├── studio_mixin.py         # Base mixin for tracking
│   ├── ir_model.py             # Extend ir.model
│   ├── ir_model_fields.py      # Extend ir.model.fields
│   ├── ir_ui_view.py           # Extend ir.ui.view
│   ├── ir_ui_menu.py           # Extend ir.ui.menu
│   ├── ir_actions.py           # Extend ir.actions.*
│   ├── base_automation.py      # Extend base.automation
│   ├── res_groups.py           # Extend res.groups
│   ├── ir_model_access.py      # Extend ir.model.access
│   ├── ir_rule.py              # Extend ir.rule
│   └── studio_module.py        # Studio module management
│
├── controllers/                 # HTTP Controllers
│   ├── __init__.py
│   └── main.py                 # Studio API endpoints
│
├── static/src/                  # Frontend (JavaScript/Owl 2.x)
│   ├── js/
│   │   ├── studio_service.js   # Core Studio service
│   │   ├── studio_menu.js      # Studio systray icon
│   │   ├── field_editor/       # Field creator UI
│   │   │   ├── field_editor.js
│   │   │   └── field_editor.xml
│   │   ├── view_editor/        # View editor UI
│   │   │   ├── view_editor.js
│   │   │   ├── xml_editor.js   # Monaco/Ace editor integration
│   │   │   └── view_editor.xml
│   │   ├── menu_editor/        # Menu editor UI
│   │   │   ├── menu_editor.js
│   │   │   └── menu_editor.xml
│   │   ├── model_creator/      # Model creator UI
│   │   │   ├── model_creator.js
│   │   │   └── model_creator.xml
│   │   └── utils.js            # Helper utilities
│   │
│   ├── scss/
│   │   ├── studio.scss         # Main styles
│   │   ├── field_editor.scss
│   │   ├── view_editor.scss
│   │   └── menu_editor.scss
│   │
│   └── xml/
│       └── templates.xml       # QWeb templates
│
├── views/                       # XML Views
│   ├── assets.xml              # Asset bundles
│   ├── ir_model_views.xml      # Enhanced model views
│   ├── ir_ui_view_views.xml    # Enhanced view views
│   ├── ir_ui_menu_views.xml    # Enhanced menu views
│   ├── studio_menu.xml         # Studio main menu
│   └── res_config_settings_views.xml  # Settings
│
├── security/
│   ├── ir.model.access.csv     # Access rights
│   └── studio_security.xml     # Security groups
│
├── data/
│   └── studio_data.xml         # Default data
│
└── wizard/                      # Wizards
    ├── __init__.py
    ├── field_creator_wizard.py
    ├── model_creator_wizard.py
    └── export_module_wizard.py
```

---

## 📦 Core Models & Extensions

### **1. studio.mixin (Abstract Model)**

**Purpose:** Track all Studio CE customizations

```python
# models/studio_mixin.py
class StudioMixin(models.AbstractModel):
    """
    Mixin to track Studio CE customizations.
    Inspired by Enterprise web_studio/models/studio_mixin.py
    """
    _name = 'studio.ce.mixin'
    _description = 'Studio CE Mixin'

    studio_ce_created = fields.Boolean(
        string='Created by Studio CE',
        default=False,
        help='Indicates this record was created using Studio CE'
    )

    studio_ce_module_id = fields.Many2one(
        'studio.ce.module',
        string='Studio CE Module',
        help='The Studio module this customization belongs to',
        ondelete='cascade'
    )

    studio_ce_created_date = fields.Datetime(
        string='Studio CE Creation Date',
        readonly=True
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to track Studio CE records"""
        res = super().create(vals_list)

        if self.env.context.get('studio_ce'):
            for record in res:
                record.write({
                    'studio_ce_created': True,
                    'studio_ce_created_date': fields.Datetime.now(),
                })
                # Create ir.model.data for tracking
                record._create_studio_ce_xmlid()

        return res

    def write(self, vals):
        """Override write to update tracking"""
        res = super().write(vals)

        if self.env.context.get('studio_ce') and not self.studio_ce_created:
            for record in self:
                record.write({
                    'studio_ce_created': True,
                    'studio_ce_created_date': fields.Datetime.now(),
                })
                record._create_studio_ce_xmlid()

        return res

    def _create_studio_ce_xmlid(self):
        """Create XML ID for Studio CE tracking"""
        IrModelData = self.env['ir.model.data']

        # Check if XML ID already exists
        existing = IrModelData.search([
            ('model', '=', self._name),
            ('res_id', '=', self.id),
            ('module', '=like', 'studio_ce_%')
        ])

        if not existing:
            module_name = self.studio_ce_module_id.name if self.studio_ce_module_id else 'studio_ce_custom'

            IrModelData.create({
                'name': f'{self._table}_{self.id}',
                'model': self._name,
                'res_id': self.id,
                'module': module_name,
                'noupdate': True,
            })
```

**Key Features:**
- ✅ Track Studio CE creations
- ✅ Link to Studio CE module
- ✅ Create XML IDs for export
- ✅ Timestamp tracking

---

### **2. studio.ce.module (New Model)**

**Purpose:** Manage Studio CE customization modules

```python
# models/studio_module.py
class StudioCEModule(models.Model):
    """
    Represents a Studio CE customization module.
    Groups related customizations together for export.
    """
    _name = 'studio.ce.module'
    _description = 'Studio CE Module'
    _order = 'name'

    name = fields.Char(
        string='Module Name',
        required=True,
        help='Technical name (e.g., studio_ce_sales_custom)'
    )

    display_name = fields.Char(
        string='Display Name',
        required=True,
        help='Human-readable name'
    )

    description = fields.Text(
        string='Description'
    )

    author = fields.Char(
        string='Author',
        default=lambda self: self.env.user.name
    )

    version = fields.Char(
        string='Version',
        default='1.0.0'
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('exported', 'Exported'),
    ], default='draft', required=True)

    # Relations
    model_ids = fields.One2many(
        'ir.model',
        'studio_ce_module_id',
        string='Custom Models'
    )

    view_ids = fields.One2many(
        'ir.ui.view',
        'studio_ce_module_id',
        string='Custom Views'
    )

    menu_ids = fields.One2many(
        'ir.ui.menu',
        'studio_ce_module_id',
        string='Custom Menus'
    )

    action_ids = fields.One2many(
        'ir.actions.act_window',
        'studio_ce_module_id',
        string='Custom Actions'
    )

    # Statistics
    customization_count = fields.Integer(
        compute='_compute_customization_count',
        string='Total Customizations'
    )

    @api.depends('model_ids', 'view_ids', 'menu_ids', 'action_ids')
    def _compute_customization_count(self):
        for record in self:
            record.customization_count = (
                len(record.model_ids) +
                len(record.view_ids) +
                len(record.menu_ids) +
                len(record.action_ids)
            )

    def action_export_module(self):
        """Export Studio CE module to installable Odoo module"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Export Studio CE Module',
            'res_model': 'studio.ce.export.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_module_id': self.id}
        }
```

---

### **3. ir.model (Extended)**

**Purpose:** Add Studio CE features to model management

```python
# models/ir_model.py
class IrModel(models.Model):
    _name = 'ir.model'
    _inherit = ['studio.ce.mixin', 'ir.model']

    # Studio CE specific fields
    studio_ce_options = fields.Selection([
        ('use_mail', 'Use Mail Thread'),
        ('use_active', 'Use Active Field'),
        ('use_sequence', 'Use Sequence'),
        ('use_company', 'Multi-Company'),
    ], string='Studio CE Options')

    def studio_ce_create_model(self, name, options=None):
        """
        Create a new model with Studio CE.
        Inspired by Enterprise Studio model creation.
        """
        self = self.with_context(studio_ce=True)

        # Sanitize model name
        model_name = f'x_{name.lower().replace(" ", "_")}'

        # Create model
        model = self.create({
            'name': model_name,
            'model': model_name,
            'state': 'manual',
            'studio_ce_created': True,
        })

        # Add default fields
        model._studio_ce_add_default_fields(options or [])

        return model

    def _studio_ce_add_default_fields(self, options):
        """Add default fields based on options"""
        IrModelFields = self.env['ir.model.fields']

        fields_to_create = []

        # name field (always)
        fields_to_create.append({
            'name': 'name',
            'field_description': 'Name',
            'ttype': 'char',
            'model_id': self.id,
            'required': True,
        })

        # active field
        if 'use_active' in options:
            fields_to_create.append({
                'name': 'active',
                'field_description': 'Active',
                'ttype': 'boolean',
                'model_id': self.id,
                'default': 'True',
            })

        # sequence field
        if 'use_sequence' in options:
            fields_to_create.append({
                'name': 'sequence',
                'field_description': 'Sequence',
                'ttype': 'integer',
                'model_id': self.id,
                'default': '10',
            })

        # Create all fields
        IrModelFields.with_context(studio_ce=True).create(fields_to_create)
```

---

### **4. ir.model.fields (Extended)**

```python
# models/ir_model_fields.py
class IrModelFields(models.Model):
    _name = 'ir.model.fields'
    _inherit = ['studio.ce.mixin', 'ir.model.fields']

    studio_ce_widget = fields.Char(
        string='Widget',
        help='Display widget for this field'
    )

    studio_ce_help = fields.Text(
        string='Help Text',
        help='Tooltip help text'
    )

    def studio_ce_create_field(self, model_id, field_data):
        """
        Create a field with Studio CE.

        :param model_id: ir.model ID
        :param field_data: dict with field configuration
        """
        self = self.with_context(studio_ce=True)

        # Validate field name
        if not field_data.get('name', '').startswith('x_'):
            field_data['name'] = f"x_{field_data['name']}"

        # Create field
        field = self.create({
            'model_id': model_id,
            'name': field_data['name'],
            'field_description': field_data.get('field_description', field_data['name']),
            'ttype': field_data['ttype'],
            'required': field_data.get('required', False),
            'readonly': field_data.get('readonly', False),
            'studio_ce_created': True,
        })

        return field
```

---

### **5. ir.ui.view (Extended)**

```python
# models/ir_ui_view.py
class IrUiView(models.Model):
    _name = 'ir.ui.view'
    _inherit = ['studio.ce.mixin', 'ir.ui.view']

    studio_ce_template = fields.Selection([
        ('form', 'Form Template'),
        ('tree', 'List Template'),
        ('kanban', 'Kanban Template'),
        ('search', 'Search Template'),
    ], string='Studio CE Template')

    def studio_ce_create_view(self, model_id, view_type, arch=None):
        """Create a view with Studio CE"""
        self = self.with_context(studio_ce=True)

        model = self.env['ir.model'].browse(model_id)

        # Generate arch if not provided
        if not arch:
            arch = self._studio_ce_generate_arch(model, view_type)

        view = self.create({
            'name': f'{model.model}.{view_type}',
            'model': model.model,
            'type': view_type,
            'arch': arch,
            'studio_ce_created': True,
        })

        return view

    def _studio_ce_generate_arch(self, model, view_type):
        """Generate default view architecture"""
        if view_type == 'form':
            return f'''<?xml version="1.0"?>
<form>
    <sheet>
        <group>
            <field name="{model._rec_name_fallback()}" />
        </group>
    </sheet>
</form>'''

        elif view_type == 'tree':
            return f'''<?xml version="1.0"?>
<tree>
    <field name="{model._rec_name_fallback()}" />
</tree>'''

        elif view_type == 'search':
            return f'''<?xml version="1.0"?>
<search>
    <field name="{model._rec_name_fallback()}" />
</search>'''

        return '<tree/>'
```

---

### **6. ir.ui.menu (Extended)**

```python
# models/ir_ui_menu.py
class IrUiMenu(models.Model):
    _name = 'ir.ui.menu'
    _inherit = ['studio.ce.mixin', 'ir.ui.menu']

    def studio_ce_create_menu(self, name, parent_id=None, action_id=None):
        """Create a menu with Studio CE"""
        self = self.with_context(studio_ce=True)

        menu = self.create({
            'name': name,
            'parent_id': parent_id,
            'action': f'ir.actions.act_window,{action_id}' if action_id else False,
            'studio_ce_created': True,
        })

        return menu
```

---

### **7. ir.actions.act_window (Extended)**

```python
# models/ir_actions.py
class IrActionsActWindow(models.Model):
    _name = 'ir.actions.act_window'
    _inherit = ['studio.ce.mixin', 'ir.actions.act_window']

    def studio_ce_create_action(self, name, model, view_mode='tree,form'):
        """Create an action with Studio CE"""
        self = self.with_context(studio_ce=True)

        action = self.create({
            'name': name,
            'res_model': model,
            'view_mode': view_mode,
            'studio_ce_created': True,
        })

        return action
```

---

## 🎨 Frontend Architecture (Owl 2.x)

### **Studio Service**

```javascript
// static/src/js/studio_service.js
/** @odoo-module **/

import { registry } from "@web/core/registry";
import { browser } from "@web/core/browser/browser";

export const studioCEService = {
    dependencies: ["rpc", "notification", "action"],

    start(env, { rpc, notification, action }) {
        let studioCEActive = false;

        return {
            /**
             * Toggle Studio CE mode
             */
            toggleStudioCE() {
                studioCEActive = !studioCEActive;

                if (studioCEActive) {
                    this.enterStudioCE();
                } else {
                    this.exitStudioCE();
                }

                return studioCEActive;
            },

            /**
             * Enter Studio CE mode
             */
            enterStudioCE() {
                // Add studio_ce class to body
                document.body.classList.add('studio-ce-active');

                // Add Studio CE UI overlay
                this._showStudioCEOverlay();

                notification.add("Studio CE mode activated", {
                    type: "success"
                });
            },

            /**
             * Exit Studio CE mode
             */
            exitStudioCE() {
                document.body.classList.remove('studio-ce-active');
                this._hideStudioCEOverlay();

                notification.add("Studio CE mode deactivated", {
                    type: "info"
                });
            },

            /**
             * Create a new field
             */
            async createField(modelId, fieldData) {
                const result = await rpc("/studio_ce/create_field", {
                    model_id: modelId,
                    field_data: fieldData,
                });

                notification.add("Field created successfully", {
                    type: "success"
                });

                return result;
            },

            /**
             * Create a new model
             */
            async createModel(modelData) {
                const result = await rpc("/studio_ce/create_model", {
                    model_data: modelData,
                });

                notification.add("Model created successfully", {
                    type: "success"
                });

                return result;
            },

            /**
             * Update view XML
             */
            async updateView(viewId, arch) {
                const result = await rpc("/studio_ce/update_view", {
                    view_id: viewId,
                    arch: arch,
                });

                notification.add("View updated successfully", {
                    type: "success"
                });

                return result;
            },

            _showStudioCEOverlay() {
                // Implementation for Studio CE UI overlay
            },

            _hideStudioCEOverlay() {
                // Implementation
            },

            isActive() {
                return studioCEActive;
            }
        };
    },
};

registry.category("services").add("studio_ce", studioCEService);
```

---

## 🔌 API Endpoints (Controllers)

```python
# controllers/main.py
from odoo import http
from odoo.http import request
import json

class StudioCEController(http.Controller):

    @http.route('/studio_ce/create_field', type='json', auth='user')
    def create_field(self, model_id, field_data):
        """Create a new field via Studio CE"""
        IrModelFields = request.env['ir.model.fields'].sudo()

        field = IrModelFields.studio_ce_create_field(
            model_id=int(model_id),
            field_data=field_data
        )

        return {
            'success': True,
            'field_id': field.id,
            'field_name': field.name,
        }

    @http.route('/studio_ce/create_model', type='json', auth='user')
    def create_model(self, model_data):
        """Create a new model via Studio CE"""
        IrModel = request.env['ir.model'].sudo()

        model = IrModel.studio_ce_create_model(
            name=model_data['name'],
            options=model_data.get('options', [])
        )

        return {
            'success': True,
            'model_id': model.id,
            'model_name': model.model,
        }

    @http.route('/studio_ce/update_view', type='json', auth='user')
    def update_view(self, view_id, arch):
        """Update view XML via Studio CE"""
        IrUiView = request.env['ir.ui.view'].sudo()

        view = IrUiView.browse(int(view_id))
        view.with_context(studio_ce=True).write({'arch': arch})

        return {
            'success': True,
            'view_id': view.id,
        }

    @http.route('/studio_ce/create_menu', type='json', auth='user')
    def create_menu(self, menu_data):
        """Create a menu via Studio CE"""
        IrUiMenu = request.env['ir.ui.menu'].sudo()

        menu = IrUiMenu.studio_ce_create_menu(
            name=menu_data['name'],
            parent_id=menu_data.get('parent_id'),
            action_id=menu_data.get('action_id')
        )

        return {
            'success': True,
            'menu_id': menu.id,
        }
```

---

## 📅 Implementation Roadmap

### **Phase 1: Foundation (Weeks 1-2)**

**Week 1:**
- ✅ Setup module structure
- ✅ Create studio.ce.mixin
- ✅ Create studio.ce.module model
- ✅ Extend ir.model, ir.model.fields
- ✅ Basic security & access rights

**Week 2:**
- ✅ Extend ir.ui.view, ir.ui.menu, ir.actions
- ✅ Setup controllers & API endpoints
- ✅ Create Studio CE service (JS)
- ✅ Add systray menu icon

### **Phase 2: Field Creator (Weeks 3-4)**

**Week 3:**
- ✅ Field creator wizard (backend)
- ✅ Field types support (Char, Text, Integer, Float, Boolean, Date, Datetime)
- ✅ Field validation

**Week 4:**
- ✅ Field creator UI (Owl component)
- ✅ Field options (required, readonly, help)
- ✅ Relational fields (Many2one, One2many, Many2many)
- ✅ Testing & bug fixes

### **Phase 3: View Editor (Weeks 5-6)**

**Week 5:**
- ✅ XML editor integration (Monaco or Ace)
- ✅ Syntax highlighting
- ✅ View templates (form, tree, search)

**Week 6:**
- ✅ Live preview
- ✅ View validation
- ✅ Save & reload
- ✅ Testing

### **Phase 4: Menu & Action (Week 7)**

- ✅ Menu creator UI
- ✅ Menu tree view
- ✅ Action creator
- ✅ Link menu to action
- ✅ Testing

### **Phase 5: Model Creator (Weeks 8-9)**

**Week 8:**
- ✅ Model creator wizard
- ✅ Model options (mail, active, sequence, etc.)
- ✅ Auto-generate default fields

**Week 9:**
- ✅ Model creator UI
- ✅ Complete workflow: Model → Fields → Views → Menu
- ✅ Testing

### **Phase 6: Automated Actions (Week 10)**

- ✅ Extend base.automation
- ✅ Simple automation UI
- ✅ Trigger conditions
- ✅ Python code editor
- ✅ Testing

### **Phase 7: Access Rights (Week 11)**

- ✅ Access rights manager UI
- ✅ Extend ir.model.access
- ✅ Group permissions
- ✅ Record rules
- ✅ Testing

### **Phase 8: Polish & Testing (Weeks 12-14)**

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
- ✅ Release preparation
- ✅ Demo environment

---

## 🔒 Security

### **Security Groups**

```xml
<!-- security/studio_security.xml -->
<odoo>
    <data noupdate="1">
        <!-- Studio CE User Group -->
        <record id="group_studio_ce_user" model="res.groups">
            <field name="name">Studio CE User</field>
            <field name="comment">Can use Studio CE to customize Odoo</field>
            <field name="implied_ids" eval="[(4, ref('base.group_user'))]"/>
        </record>

        <!-- Studio CE Admin Group -->
        <record id="group_studio_ce_admin" model="res.groups">
            <field name="name">Studio CE Admin</field>
            <field name="comment">Full access to Studio CE</field>
            <field name="implied_ids" eval="[(4, ref('base.group_system'))]"/>
        </record>
    </data>
</odoo>
```

### **Access Rights**

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_studio_ce_module_user,studio.ce.module.user,model_studio_ce_module,group_studio_ce_user,1,1,1,0
access_studio_ce_module_admin,studio.ce.module.admin,model_studio_ce_module,group_studio_ce_admin,1,1,1,1
```

---

## 📈 Success Metrics

| Metric | Target |
|--------|--------|
| **Field Creation Time** | < 30 seconds |
| **View Creation Time** | < 2 minutes |
| **Menu Creation Time** | < 1 minute |
| **Model Creation Time** | < 5 minutes |
| **User Satisfaction** | > 4/5 stars |
| **Bug Report Rate** | < 5 per 100 users |

---

## 🎓 Key Design Decisions

### **1. Why Extend CE Models?**
- ✅ Reuse existing infrastructure
- ✅ Seamless integration
- ✅ Export-friendly (standard Odoo code)
- ✅ Familiar to developers

### **2. Why Mixin Pattern?**
- ✅ Track Studio CE customizations
- ✅ Enable module export
- ✅ Clean separation of concerns
- ✅ Same pattern as Enterprise

### **3. Why XML Editor (not Drag & Drop)?**
- ✅ Simpler to implement (2 weeks vs 8+ weeks)
- ✅ More powerful for developers
- ✅ Easier to maintain
- ✅ Lower complexity

### **4. Why 70% Features?**
- ✅ Focus on most-used features
- ✅ Faster time to market
- ✅ Easier to maintain
- ✅ Still very useful

---

## 🔄 Future Enhancements (Post-MVP)

1. **Visual Drag & Drop Editor** (if resources available)
2. **Report Designer**
3. **Approval Workflows**
4. **Module Export/Import**
5. **Version Control Integration**
6. **Collaboration Features**
7. **AI-Powered Suggestions**

---

## 📝 Summary

**Studio CE** provides a practical, maintainable solution for Odoo CE users who need Studio-like functionality without Enterprise license.

**Key Advantages:**
- ✅ Extends CE models (proven pattern)
- ✅ 70% of Studio features (most-used)
- ✅ 10-14 weeks implementation
- ✅ Maintainable codebase
- ✅ Export-friendly

**Ready to start implementation!** 🚀

---

**End of Architecture Document**
