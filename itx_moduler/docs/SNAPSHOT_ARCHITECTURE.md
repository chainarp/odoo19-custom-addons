# ITX Moduler - Snapshot Architecture Design

**Date:** 2025-12-14
**Status:** Design Phase
**Version:** 1.0

---

## 🎯 Overview

ITX Moduler ใช้ **Metadata-First Architecture** โดยเก็บข้อมูลโครงสร้าง module ไว้ในตาราง snapshot (`itx_moduler_*`) ก่อน จากนั้นจึง:
- **Apply** → สร้าง ir.model จริงใน Odoo (live update)
- **Export** → Generate Python/XML files เพื่อ install แบบปกติ

---

## 🎨 Design Principles

### 1. Creator คือทั้ง SA และ AI

**System Analyst (SA):**
- สร้าง/แก้ไข module ด้วย UI (forms, wizards)
- Drag-drop fields, visual view designer
- Step-by-step workflow

**Artificial Intelligence (AI - Claude):**
- รับ natural language prompt
- Generate JSON structure
- Map to snapshot tables
- Auto-create models/fields/views

**Schema ต้อง:**
- ✅ Simple enough for AI to generate
- ✅ Rich enough for SA to fine-tune
- ✅ Validated for both inputs

---

## 🔄 State Workflow

### States

```
draft → validated → applied → exported → archived
```

| State | Description | Can Edit? | Actions Available |
|-------|-------------|-----------|-------------------|
| **draft** | กำลังสร้าง/แก้ไข | ✅ Yes | Save, Validate |
| **validated** | ผ่าน validation แล้ว | ⚠️ Limited | Apply, Edit (→draft) |
| **applied** | สร้าง ir.model จริงแล้ว | ❌ No* | Export, Archive |
| **exported** | Export เป็น ZIP แล้ว | ❌ No | Download, Archive |
| **archived** | Version เก่าที่เก็บไว้ | ❌ No | View only, Restore |

*สามารถสร้าง version ใหม่ได้

### State Transitions

```python
state = fields.Selection([
    ('draft', 'Draft'),
    ('validated', 'Validated'),
    ('applied', 'Applied'),
    ('exported', 'Exported'),
    ('archived', 'Archived'),
], default='draft', tracking=True)
```

**Workflow:**
```
Create New Model
      ↓
   [DRAFT]
      ↓ action_validate()
  [VALIDATED]
      ↓ action_apply_to_odoo()
   [APPLIED]
      ↓ action_export_module()
  [EXPORTED]
      ↓ action_archive()
  [ARCHIVED]
```

---

## 📦 Version & Revision Management

### Why Versioning?

1. **SA แก้ไขหลายรอบ** - ต้อง track changes
2. **AI regenerate** - เก็บ version เดิมไว้เปรียบเทียบ
3. **Rollback capability** - กลับไป version ที่ดีกว่า
4. **A/B Testing** - ทดสอบหลาย version พร้อมกัน

### Version Fields

```python
# In all snapshot tables
version = fields.Integer(
    string='Version',
    default=1,
    readonly=True,
    help='Auto-increment on each major change'
)

active = fields.Boolean(
    default=True,
    help='False = archived version'
)

parent_version_id = fields.Many2one(
    'itx.moduler.model',  # or respective table
    string='Previous Version',
    help='Link to version this was cloned from'
)

revision_ids = fields.One2many(
    'itx.moduler.model.revision',
    'model_id',
    string='Revision History'
)
```

### Revision History Table

```python
class ItxModulerModelRevision(models.Model):
    _name = 'itx.moduler.model.revision'
    _description = 'Model Revision History'
    _order = 'version desc, create_date desc'

    model_id = fields.Many2one(
        'itx.moduler.model',
        required=True,
        ondelete='cascade',
        index=True
    )

    version = fields.Integer(
        required=True,
        help='Version number at time of revision'
    )

    # Complete snapshot
    snapshot_data = fields.Text(
        required=True,
        help='JSON snapshot: {model: {...}, fields: [{...}], methods: [{...}]}'
    )

    change_summary = fields.Text(
        help='Human-readable summary of changes'
    )

    change_type = fields.Selection([
        ('create', 'Created'),
        ('edit', 'Edited'),
        ('ai_regen', 'AI Regenerated'),
        ('validate', 'Validated'),
        ('apply', 'Applied'),
        ('export', 'Exported'),
    ], required=True)

    # Who/When
    changed_by = fields.Many2one(
        'res.users',
        string='Changed By',
        default=lambda self: self.env.user,
        required=True
    )

    changed_date = fields.Datetime(
        default=fields.Datetime.now,
        required=True
    )

    # AI-specific
    created_by_ai = fields.Boolean(
        string='AI Generated',
        default=False
    )

    ai_prompt = fields.Text(
        string='AI Prompt',
        help='Prompt used if AI-generated'
    )

    ai_prompt_diff = fields.Text(
        string='Prompt Changes',
        help='What changed in prompt from previous version'
    )

    # Diff
    fields_added = fields.Integer(
        compute='_compute_diff_stats'
    )
    fields_removed = fields.Integer(
        compute='_compute_diff_stats'
    )
    fields_modified = fields.Integer(
        compute='_compute_diff_stats'
    )

    @api.depends('snapshot_data')
    def _compute_diff_stats(self):
        """Calculate what changed from previous revision"""
        for rev in self:
            prev_rev = self.search([
                ('model_id', '=', rev.model_id.id),
                ('version', '<', rev.version)
            ], order='version desc', limit=1)

            if prev_rev:
                # Compare snapshots and calculate diff
                # ... implementation
                pass
```

### Versioning Workflow

```python
def action_save_new_version(self):
    """Create new version when significant changes made"""
    self.ensure_one()

    # Create revision record
    self.env['itx.moduler.model.revision'].create({
        'model_id': self.id,
        'version': self.version,
        'snapshot_data': self._get_snapshot_json(),
        'change_type': 'edit',
        'change_summary': 'Manual edit by SA'
    })

    # Clone to new version
    new_version = self.copy({
        'version': self.version + 1,
        'parent_version_id': self.id,
        'state': 'draft',
        'active': True
    })

    # Archive current version
    self.write({
        'active': False,
        'state': 'archived'
    })

    return {
        'type': 'ir.actions.act_window',
        'res_model': 'itx.moduler.model',
        'res_id': new_version.id,
        'view_mode': 'form',
        'target': 'current'
    }

def action_compare_versions(self):
    """Compare current version with previous"""
    return {
        'type': 'ir.actions.act_window',
        'res_model': 'itx.moduler.version.compare.wizard',
        'view_mode': 'form',
        'target': 'new',
        'context': {
            'default_current_version_id': self.id,
            'default_compare_version_id': self.parent_version_id.id
        }
    }
```

---

## 🔒 Module Modification Rules

### Rule 1: Standard Odoo Modules - CREATE NEW MODULE ONLY

**Standard modules ห้ามแก้โดยตรง:**
```python
STANDARD_MODULES = [
    'base', 'web', 'web_studio',
    'sale', 'sale_management', 'sale_stock',
    'purchase', 'purchase_stock',
    'stock', 'stock_account',
    'account', 'account_payment',
    'hr', 'hr_attendance', 'hr_holidays', 'hr_payroll',
    'crm', 'crm_iap',
    'project', 'project_todo',
    'mrp', 'mrp_account',
    'point_of_sale',
    'website', 'website_sale',
    'mail', 'calendar', 'contacts',
    # ... add more
]

def _is_standard_module(self, module_name):
    """Check if module is standard Odoo"""
    return module_name in STANDARD_MODULES
```

**เมื่อ import standard module:**

```python
def action_import_module(self):
    """Import existing Odoo module"""
    source = self.source_module_id

    if self._is_standard_module(source.name):
        # ต้องสร้าง module ใหม่ที่ inherit
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Inheriting Module',
            'res_model': 'itx.moduler.inherit.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_source_module_name': source.name,
                'default_source_module_id': source.id,
                'mode': 'inherit_only'
            }
        }
    else:
        # Custom module - import ตรงได้
        return self._import_to_snapshot()
```

**Inherit Wizard จะสร้าง:**

```python
# ตัวอย่าง: ต้องการแก้ sale.order
# จะสร้าง module ใหม่ชื่อ: my_sale_custom

class ItxModulerInheritWizard(models.TransientModel):
    _name = 'itx.moduler.inherit.wizard'

    source_module_name = fields.Char(readonly=True)
    new_module_name = fields.Char(
        required=True,
        help='e.g., my_sale_custom'
    )

    models_to_inherit = fields.Many2many(
        'ir.model',
        string='Models to Inherit',
        domain="[('modules', 'ilike', source_module_name)]"
    )

    def action_create_inheriting_module(self):
        # สร้าง itx_moduler_module ใหม่
        new_module = self.env['itx.moduler.module'].create({
            'name': self.new_module_name,
            'shortdesc': f'Customization of {self.source_module_name}',
            'depends_ids': [(0, 0, {
                'name': self.source_module_name
            })]
        })

        # สร้าง inherited models
        for ir_model in self.models_to_inherit:
            self.env['itx.moduler.model'].create({
                'module_id': new_module.id,
                'name': ir_model.name,
                'model': ir_model.model,
                'inherit_model_names': ir_model.model,  # _inherit
                'description': f'Inherit {ir_model.model}'
            })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'itx.moduler.module',
            'res_id': new_module.id,
            'view_mode': 'form'
        }
```

### Rule 2: Custom Modules - Both Options Available

**Custom modules (ของเราเอง):**

```python
def _is_custom_module(self, module_id):
    """Check if we have write access to this module"""
    # Check if module is in our custom_addons path
    # Check if we created it via ITX Moduler
    return (
        module_id.itx_moduler_created or
        'custom_addons' in module_id.path
    )
```

**Option A: Live Update (Direct Modify ir.model)**

```python
def action_apply_to_odoo(self):
    """Apply changes to live Odoo database"""
    self.ensure_one()

    if self.state != 'validated':
        raise UserError('Must validate before applying')

    # Safety check
    if self.module_id.is_standard_module:
        raise UserError(
            'Cannot directly modify standard Odoo modules!\n'
            'Create an inheriting module instead.'
        )

    # Update/Create ir.model
    ir_model = self.env['ir.model'].search([
        ('model', '=', self.model)
    ], limit=1)

    if ir_model:
        # Update existing model
        ir_model.write({
            'name': self.name,
            'info': self.description,
        })
    else:
        # Create new model
        ir_model = self.env['ir.model'].create({
            'name': self.name,
            'model': self.model,
            'info': self.description,
            'state': 'manual',
            'transient': self.is_transient,
        })

    # Update/Create fields
    for field in self.field_ids:
        field.action_apply_to_odoo(ir_model)

    # Link and update state
    self.write({
        'ir_model_id': ir_model.id,
        'state': 'applied',
        'applied_date': fields.Datetime.now()
    })

    # Create revision
    self.env['itx.moduler.model.revision'].create({
        'model_id': self.id,
        'version': self.version,
        'snapshot_data': self._get_snapshot_json(),
        'change_type': 'apply',
        'change_summary': f'Applied to Odoo (ir.model.id: {ir_model.id})'
    })

    return True
```

**Option B: Export as Files (Safe, Recommended)**

```python
def action_export_module(self):
    """Export module as ZIP file"""
    self.ensure_one()

    if self.state not in ('validated', 'applied'):
        raise UserError('Must validate before exporting')

    # Generate all files
    files = {}

    # 1. __manifest__.py
    files['__manifest__.py'] = self._generate_manifest()

    # 2. __init__.py
    files['__init__.py'] = "from . import models\n"

    # 3. models/__init__.py
    files['models/__init__.py'] = self._generate_models_init()

    # 4. models/[model_name].py for each model
    for model in self.module_id.model_ids:
        filename = f"models/{model.model.replace('.', '_')}.py"
        files[filename] = model.action_generate_python_code()

    # 5. views/[model]_views.xml for each model
    for model in self.module_id.model_ids:
        if model.view_ids:
            filename = f"views/{model.model.replace('.', '_')}_views.xml"
            files[filename] = model._generate_views_xml()

    # 6. security/ir.model.access.csv
    files['security/ir.model.access.csv'] = self._generate_access_csv()

    # 7. data/demo.xml (if has demo data)
    if self.module_id.data_ids:
        files['data/demo.xml'] = self._generate_demo_xml()

    # Create ZIP
    import io
    from zipfile import ZipFile

    zip_buffer = io.BytesIO()
    with ZipFile(zip_buffer, 'w') as zip_file:
        for filename, content in files.items():
            full_path = f"{self.module_id.name}/{filename}"
            zip_file.writestr(full_path, content)

    # Save to database
    zip_data = base64.b64encode(zip_buffer.getvalue())

    self.module_id.write({
        'exported_file': zip_data,
        'exported_filename': f"{self.module_id.name}.zip",
        'exported_date': fields.Datetime.now(),
        'state': 'exported'
    })

    return {
        'type': 'ir.actions.act_url',
        'url': f'/web/content/itx.moduler.module/{self.module_id.id}/exported_file/{self.module_id.exported_filename}',
        'target': 'self'
    }
```

### UI Indication

```xml
<group name="module_type" string="Module Type">
    <field name="is_standard_module" readonly="1"
           widget="boolean_toggle"/>

    <div class="alert alert-warning"
         invisible="not is_standard_module">
        <i class="fa fa-warning"/> <strong>Standard Odoo Module</strong><br/>
        This module cannot be modified directly.<br/>
        You can only create a new module that inherits from it.
    </div>

    <div class="alert alert-info"
         invisible="is_standard_module">
        <i class="fa fa-info-circle"/> <strong>Custom Module</strong><br/>
        You can choose to apply changes directly or export as files.
    </div>
</group>

<group name="modification_options"
       invisible="is_standard_module or state != 'validated'">
    <label for="modification_strategy" string="How to Apply?"/>
    <div>
        <field name="modification_strategy" widget="radio" class="o_horizontal">
            <option value="live">
                <span class="fa fa-bolt"/> Live Update
                <small class="text-muted">(Modify ir.model directly)</small>
            </option>
            <option value="export">
                <span class="fa fa-download"/> Export Files
                <small class="text-muted">(Generate ZIP for installation)</small>
            </option>
        </field>
    </div>
</group>

<footer>
    <button name="action_apply_to_odoo"
            string="Apply to Odoo (Live)"
            type="object"
            class="btn-primary"
            invisible="modification_strategy != 'live' or state != 'validated'"/>

    <button name="action_export_module"
            string="Export as ZIP"
            type="object"
            class="btn-primary"
            invisible="modification_strategy != 'export' or state != 'validated'"/>

    <button name="action_create_inheriting_module"
            string="Create Inheriting Module"
            type="object"
            class="btn-primary"
            invisible="not is_standard_module"/>

    <button string="Cancel" special="cancel" class="btn-secondary"/>
</footer>
```

---

## 📋 Complete Table List

### Phase 1: Core Tables (MVP) - 16 Tables

**Module Management:**
1. ✅ `itx_moduler_module` - Module metadata
2. ✅ `itx_moduler_module_dependency` - Module dependencies

**Model & Fields:**
3. ✅ `itx_moduler_model` - Model definitions
4. ✅ `itx_moduler_model_field` - Field definitions
5. ✅ `itx_moduler_model_field_selection` - Selection field options
6. ✅ `itx_moduler_model_method` - Python methods (compute, onchange, etc.)

**Views & UI:**
7. ✅ `itx_moduler_view` - View definitions (form, tree, kanban, etc.)
8. ✅ `itx_moduler_menu` - Menu structure
9. ✅ `itx_moduler_action_window` - Window actions
10. ✅ `itx_moduler_action_server` - Server actions

**Security:**
11. ✅ `itx_moduler_model_access` - Access rights (ir.model.access)
12. ✅ `itx_moduler_rule` - Record rules (ir.rule)
13. ✅ `itx_moduler_group` - Security groups

**Constraints:**
14. ✅ `itx_moduler_constraint` - SQL constraints
15. ⚠️ `ir.model.server_constrain` - Server constraints (already exists)

**Data:**
16. ✅ `itx_moduler_data` - Demo/master data records

### Phase 2: Advanced Tables - 6 Tables

**Version Control:**
17. 🆕 `itx_moduler_model_revision` - **Version history & diff tracking**

**Wizards:**
18. 🆕 `itx_moduler_wizard` - Wizard/TransientModel definitions
19. 🆕 `itx_moduler_wizard_step` - Multi-step wizard configuration

**Automation:**
20. 🆕 `itx_moduler_cron` - Scheduled actions (ir.cron)
21. 🆕 `itx_moduler_automation` - Automated actions (base.automation)

**Communication:**
22. 🆕 `itx_moduler_email_template` - Email templates

### Phase 3: Extended Features - 4 Tables

**Reports & Templates:**
23. 🆕 `itx_moduler_report` - QWeb reports
24. 🆕 `itx_moduler_qweb_template` - QWeb templates

**Assets:**
25. 🆕 `itx_moduler_assets` - JS/CSS/SCSS files
26. 🆕 `itx_moduler_assets_bundle` - Asset bundle configuration

### Optional (Future):

27. ⚪ `itx_moduler_webhook` - Webhook/API endpoints
28. ⚪ `itx_moduler_translation` - Translation strings (i18n)
29. ⚪ `itx_moduler_test` - Unit test definitions
30. ⚪ `itx_moduler_migration` - Migration scripts

---

## 📐 Common Fields (All Snapshot Tables)

**Every snapshot table should have:**

```python
# === Module Link ===
module_id = fields.Many2one(
    'itx.moduler.module',
    string='Module',
    required=True,
    ondelete='cascade',
    index=True
)

# === State Management ===
state = fields.Selection([
    ('draft', 'Draft'),
    ('validated', 'Validated'),
    ('applied', 'Applied'),
    ('exported', 'Exported'),
    ('archived', 'Archived')
], default='draft', required=True, tracking=True, index=True)

# === Version Control ===
version = fields.Integer(
    string='Version',
    default=1,
    readonly=True,
    help='Auto-incremented version number'
)

active = fields.Boolean(
    string='Active',
    default=True,
    help='False = archived version'
)

parent_version_id = fields.Many2one(
    # Same model (self reference)
    string='Parent Version',
    help='Previous version this was cloned from'
)

# === AI Integration ===
created_by_ai = fields.Boolean(
    string='Created by AI',
    default=False,
    index=True
)

ai_prompt = fields.Text(
    string='AI Prompt',
    help='Original prompt if AI-generated'
)

ai_confidence = fields.Float(
    string='AI Confidence',
    digits=(5, 2),
    help='AI generation confidence (0-100%)'
)

# === Link to Real Odoo Record (when applied) ===
ir_*_id = fields.Many2one(
    'ir.*',  # ir.model, ir.model.fields, ir.ui.view, etc.
    string='Applied Record',
    readonly=True,
    help='Link to real Odoo record when state=applied'
)

applied_date = fields.Datetime(
    string='Applied Date',
    readonly=True
)

# === Error Tracking ===
error_message = fields.Text(
    string='Error Message',
    readonly=True
)

# === Audit Trail ===
create_uid = fields.Many2one('res.users', string='Created by')
write_uid = fields.Many2one('res.users', string='Last Modified by')
create_date = fields.Datetime(string='Created on')
write_date = fields.Datetime(string='Last Modified on')
```

---

## 🎯 Implementation Priority

### Sprint 1 (Week 1-2): Core Foundation
1. ✅ `itx_moduler_module` (already exists)
2. ✅ `itx_moduler_module_dependency` (already exists)
3. 🔨 `itx_moduler_model` (NEW - with versioning)
4. 🔨 `itx_moduler_model_field` (NEW)
5. 🔨 `itx_moduler_model_field_selection` (NEW)
6. 🔨 `itx_moduler_model_revision` (NEW - version history)

**Deliverable:** Can create/edit models with fields and track versions

### Sprint 2 (Week 3-4): Views & UI
7. 🔨 `itx_moduler_view` (NEW)
8. 🔨 `itx_moduler_menu` (NEW)
9. 🔨 `itx_moduler_action_window` (NEW)

**Deliverable:** Can design views and menus

### Sprint 3 (Week 5-6): Security & Methods
10. 🔨 `itx_moduler_model_access` (NEW)
11. 🔨 `itx_moduler_rule` (NEW)
12. 🔨 `itx_moduler_group` (NEW)
13. 🔨 `itx_moduler_model_method` (NEW)
14. 🔨 `itx_moduler_constraint` (NEW)

**Deliverable:** Full security model + custom Python code

### Sprint 4 (Week 7-8): Export & Apply
- Implement `action_validate()`
- Implement `action_apply_to_odoo()` (Option A)
- Implement `action_export_module()` (Option B)
- Standard module detection & inherit wizard

**Deliverable:** Working end-to-end flow

### Sprint 5+ (Week 9+): Advanced Features
- Remaining tables (reports, automation, etc.)
- AI integration (Claude API)
- Visual builder (Owl components)

---

## 📝 Key Decisions Summary

| # | Decision | Rationale |
|---|----------|-----------|
| 1 | Use snapshot tables instead of directly modifying ir.* | Allows validation, versioning, AI integration |
| 2 | State: draft→validated→applied→exported→archived | Clear workflow with checkpoints |
| 3 | Version tracking with revision history table | Essential for SA edits and AI regeneration |
| 4 | Standard modules → create inheriting module only | Safety: never modify core Odoo |
| 5 | Custom modules → both live update and export options | Flexibility for developers |
| 6 | 22 tables for full feature set (16 MVP + 6 advanced) | Balanced scope for Phase 1-2 |
| 7 | Common fields in all snapshot tables | Consistency, easier to manage |
| 8 | AI fields (created_by_ai, ai_prompt) in all tables | Support both SA and AI creation |

---

## 🚀 Next Steps

1. ✅ Review this document
2. ⏳ Design detailed schema for Phase 1 tables (6 tables)
3. ⏳ Create migration script to add new tables
4. ⏳ Implement `itx_moduler_model` with full versioning
5. ⏳ Implement `itx_moduler_model_field`
6. ⏳ Create UI forms for SA to create models
7. ⏳ Test end-to-end: Create → Validate → Apply → Export

---

**Document Version:** 1.0
**Last Updated:** 2025-12-14
**Authors:** Chainaris P, Claude Sonnet 4.5
**Status:** ✅ Approved for Implementation

---

## 📚 Related Documents

- [CONSOLIDATION_PLAN.md](./CONSOLIDATION_PLAN.md) - Overall project roadmap
- [OCE_MODULE_CREATOR_CONCEPT.md](./OCE_MODULE_CREATOR_CONCEPT.md) - Metadata-first philosophy
- [CLAUDE_API_INTEGRATION.md](./CLAUDE_API_INTEGRATION.md) - AI integration architecture
