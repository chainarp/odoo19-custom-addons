# ITX Moduler - Version Compatibility Strategy

**Date:** 2025-12-16
**Status:** 📋 Future Planning (NOT IMPLEMENTING YET)
**Version:** 1.0
**Focus Now:** Odoo 19 only - Jinja2 refactor first!

---

## ⚠️ IMPORTANT: This is Future Planning Only

**Current Priority:**
1. ✅ Finish Odoo 19 implementation (Jinja2 templates)
2. ✅ Make v19 stable and feature-complete
3. ⏳ THEN consider v20 migration (when needed)

**This document exists to:**
- 🧠 Keep migration strategy in mind during v19 development
- 🏗️ Avoid architectural decisions that make future migration hard
- 📝 Document the plan so we don't have to tear everything down later

---

## 🎯 The Challenge

**Problem:** Odoo versions (19 → 20 → future) มี breaking changes:
- API changes (ORM methods)
- Field types evolution
- View architecture updates
- Python version requirements
- JavaScript framework changes (Owl versions)
- Deprecated features

**Goal:** ITX Moduler ต้องสร้าง addon ที่:
1. ✅ รองรับหลาย Odoo versions
2. ✅ Upgrade ได้ง่าย (19 → 20 → 21)
3. ✅ Maintain ได้ (แก้ที่เดียว support ทุก version)
4. ✅ Future-proof (พร้อม version ใหม่)

---

## 🎯 Chainarp's Decision: The 2C Way (Chainarp + Claude)

**Roadmap Approved:**
1. **Phase 1 (NOW):** Refactor เป็น Jinja2 (v19 only) ✅
2. **Phase 2:** เพิ่ม v20 templates (when v20 is needed)
3. **Phase 3:** Migration Wizard (with WOW effect! 🎉)
4. **Phase 4:** AI-assisted migration (Claude-powered)

**Strategy:** Hybrid approach ที่รวมทุกอย่างเข้าด้วยกัน

**Note:** เราไม่สนใจเวอร์ชันเก่า (16, 17, 18) - **เดินหน้าอย่างเดียว!**

---

## 📊 Comparison of Approaches

| Approach | Pros | Cons | Status |
|----------|------|------|--------|
| **1. Multi-Version Templates** | ✅ Clean separation<br>✅ Version-specific optimization | ⚠️ Template duplication<br>⚠️ More maintenance | Phase 2 |
| **2. Migration Wizard** | ✅ Automated conversion<br>✅ Clear upgrade path | ⚠️ Complex logic<br>⚠️ Error-prone | Phase 3 |
| **3. Version-Agnostic Code** | ✅ Write once, run anywhere<br>✅ Less templates | ⚠️ Compromised quality<br>⚠️ Compatibility layer overhead | ❌ Not chosen |
| **4. Hybrid (CHOSEN)** | ✅ Best of all worlds<br>✅ Flexible<br>✅ WOW effect potential | ⚠️ Initial setup effort | ✅ Approved |

---

## 🏆 Recommended Strategy: Hybrid Approach

### Core Concept

```
Snapshot Tables (Version-Neutral)
        ↓
Version Detection + Rules
        ↓
Template Selection (Version-Specific)
        ↓
Code Generation (Optimized per version)
```

---

## 🏗️ Architecture Design

### 1. Version-Neutral Snapshot Layer

**Snapshot tables เก็บ "intent" ไม่ใช่ "implementation"**

```python
# itx_moduler_model_field - Version neutral
{
    'name': 'partner_id',
    'ttype': 'many2one',  # Generic type
    'relation': 'res.partner',
    'required': True,
    'help': 'Related partner'
}
```

**NOT:**
```python
# Bad - Version specific
{
    'name': 'partner_id',
    'odoo19_code': "fields.Many2one('res.partner', required=True)",
    'odoo20_code': "fields.Many2one('res.partner', required=True)",
}
```

### 2. Version-Specific Templates

```
templates/
├── common/                    # Shared across versions
│   ├── _macros.j2            # Reusable template parts
│   └── _helpers.j2
│
├── v19/                       # ✅ Phase 1 - NOW
│   ├── manifest.py.j2
│   ├── model.py.j2
│   ├── view.xml.j2
│   └── version_info.yaml     # Version metadata
│
└── v20/                       # ⏳ Phase 2 - Future (when v20 comes)
    ├── manifest.py.j2        # Will add when v20 is released
    ├── model.py.j2
    ├── view.xml.j2
    └── version_info.yaml

# Note: เราไม่ทำ v16, v17, v18 - เดินหน้าอย่างเดียว!
```

### 3. Template Selection Logic

```python
class ItxModulerModule(models.Model):
    _name = 'itx.moduler.module'

    target_odoo_version = fields.Selection([
        ('19.0', 'Odoo 19'),
        ('20.0', 'Odoo 20'),
        ('21.0', 'Odoo 21'),
        ('auto', 'Auto-detect from current system'),
    ], default='auto', string='Target Odoo Version')

    def _get_template_path(self):
        """Get template directory based on target version"""
        if self.target_odoo_version == 'auto':
            version = self._detect_current_odoo_version()
        else:
            version = self.target_odoo_version

        major_version = version.split('.')[0]
        return f'templates/v{major_version}/'

    def _detect_current_odoo_version(self):
        """Detect Odoo version from release info"""
        import odoo.release
        return odoo.release.version
```

---

## 🔄 Version Migration Workflow

### Scenario: User wants to upgrade addon from v19 → v20

```
┌─────────────────────────────────────┐
│ User has addon created for Odoo 19 │
│ (stored in snapshots)               │
└────────────────┬────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│ Click "Upgrade to Odoo 20" button  │
└────────────────┬────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│ Migration Wizard Opens              │
│ - Analyzes snapshot data            │
│ - Checks for breaking changes       │
│ - Shows migration report            │
└────────────────┬────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│ Automatic Fixes Applied             │
│ - Update manifest version           │
│ - Fix deprecated field attributes   │
│ - Update view arch (if needed)      │
└────────────────┬────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│ Manual Review Required              │
│ (if breaking changes detected)      │
│ - Show diff                         │
│ - Suggest fixes                     │
│ - Allow user to adjust              │
└────────────────┬────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│ Export with v20 templates           │
│ → Ready for Odoo 20                 │
└─────────────────────────────────────┘
```

---

## 📋 Version-Specific Handling

### 1. Field Type Mapping

```yaml
# templates/v19/version_info.yaml
field_type_mapping:
  char: "fields.Char"
  text: "fields.Text"
  many2one: "fields.Many2one"
  selection: "fields.Selection"

deprecated_attributes:
  - groups  # Use groups_id instead in v20+

# templates/v20/version_info.yaml
field_type_mapping:
  char: "fields.Char"
  text: "fields.Text"
  many2one: "fields.Many2one"
  selection: "fields.Selection"  # Or could map to m2o in some cases

new_features:
  - computed_sudo  # New in v20

breaking_changes:
  - field: "groups"
    replacement: "groups_id"
    auto_fix: true
```

### 2. View Architecture Changes

```jinja2
{# templates/v19/view.xml.j2 #}
<record id="{{ view.xmlid }}" model="ir.ui.view">
    <field name="name">{{ view.name }}</field>
    <field name="model">{{ view.model }}</field>
    <field name="arch" type="xml">
        {{ view.arch | safe }}
    </field>
</record>

{# templates/v20/view.xml.j2 #}
<record id="{{ view.xmlid }}" model="ir.ui.view">
    <field name="name">{{ view.name }}</field>
    <field name="model">{{ view.model }}</field>
    {% if view.priority %}
    <field name="priority">{{ view.priority }}</field>
    {% endif %}
    <field name="arch" type="xml">
        {{ view.arch | process_v20_arch | safe }}
    </field>
</record>
```

### 3. Manifest Differences

```jinja2
{# templates/v19/manifest.py.j2 #}
{
    'name': '{{ module.shortdesc }}',
    'version': '19.0.{{ module.version }}',
    'category': '{{ module.category_id.name }}',
    'depends': {{ module.depends | tojson }},
    'data': {{ module.data_files | tojson }},
    'installable': True,
    'application': {{ module.application }},
}

{# templates/v20/manifest.py.j2 #}
{
    'name': '{{ module.shortdesc }}',
    'version': '20.0.{{ module.version }}',
    'category': '{{ module.category_id.name }}',
    'depends': {{ module.depends | tojson }},
    'data': {{ module.data_files | tojson }},
    'assets': {  # New in v20
        {% if module.has_assets %}
        'web.assets_backend': [
            {% for asset in module.backend_assets %}
            '{{ asset }}',
            {% endfor %}
        ],
        {% endif %}
    },
    'installable': True,
    'application': {{ module.application }},
    'license': '{{ module.license }}',  # Required in v20+
}
```

---

## 🛠️ Implementation Plan (2C Roadmap)

### ✅ Phase 1: Jinja2 Refactor (NOW - Focus on v19 only)

```python
# 1. Add version field to module
class ItxModulerModule(models.Model):
    _name = 'itx.moduler.module'

    target_odoo_version = fields.Selection([
        ('19.0', 'Odoo 19'),
        ('20.0', 'Odoo 20'),
        ('21.0', 'Odoo 21'),
        ('auto', 'Auto (Current System)'),
    ], default='auto')

    supports_versions = fields.Char(
        string='Version Compatibility',
        help='e.g., "19.0,20.0,21.0"',
        compute='_compute_supports_versions'
    )

# 2. Create template structure
templates/
├── common/
├── v19/
├── v20/
└── v21/

# 3. Refactor code generator
def generate_code(self, module):
    template_path = module._get_template_path()
    env = Environment(loader=FileSystemLoader(template_path))
    # ... render templates
```

### ⏳ Phase 2: v20 Support (When Odoo 20 is released)

**Triggered when:** Odoo 20 official release

**Tasks:**
1. Create `templates/v20/` directory
2. Copy v19 templates as base
3. Update for v20 breaking changes
4. Test export compatibility
5. Add version selector: `module.target_odoo_version = '20.0'`

**Estimate:** 1-2 weeks (because foundation already exists)

---

### ⏳ Phase 3: Migration Wizard (WOW Effect! 🎉)

```python
# wizards/itx_moduler_version_migration_wizard.py
class ItxModulerVersionMigrationWizard(models.TransientModel):
    _name = 'itx.moduler.version.migration.wizard'

    module_id = fields.Many2one('itx.moduler.module', required=True)
    source_version = fields.Char(readonly=True)
    target_version = fields.Selection([
        ('20.0', 'Odoo 20'),
        ('21.0', 'Odoo 21'),
    ], required=True)

    migration_report = fields.Html(
        compute='_compute_migration_report'
    )

    def _compute_migration_report(self):
        """Analyze and show what will change"""
        analyzer = self.env['itx.moduler.version.analyzer']
        changes = analyzer.analyze_migration(
            self.module_id,
            self.source_version,
            self.target_version
        )

        report = """
        <h3>Migration Summary</h3>
        <ul>
            <li>Automatic fixes: {auto_count}</li>
            <li>Manual review needed: {manual_count}</li>
            <li>Breaking changes: {breaking_count}</li>
        </ul>

        <h3>Detailed Changes</h3>
        {change_details}
        """.format(**changes)

        self.migration_report = report

    def action_migrate(self):
        """Execute migration"""
        migrator = self.env['itx.moduler.version.migrator']
        migrator.migrate(
            self.module_id,
            self.target_version
        )

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Migration Complete',
                'message': f'Module upgraded to Odoo {self.target_version}',
                'type': 'success',
            }
        }
```

### ⏳ Phase 4: AI-Assisted Migration (Claude-Powered)

**Features:**
- Claude analyzes breaking changes
- Suggests migration code
- Auto-generates migration scripts
- Interactive Q&A for complex cases

**Integration:**
```python
# Claude helps with migration
wizard.action_ai_assist()
→ Claude API analyzes changes
→ Suggests fixes
→ User reviews & applies
```

**Note:** By this time, Odoo 20 will likely have more AI features too!
We'll integrate with whatever AI capabilities Odoo 20 provides.

---

### ⏳ Phase 5: Version Analyzer (Supporting Phase 3)

```python
# models/itx_moduler_version_analyzer.py
class ItxModulerVersionAnalyzer(models.Model):
    _name = 'itx.moduler.version.analyzer'
    _description = 'Version Compatibility Analyzer'

    def analyze_migration(self, module, source_version, target_version):
        """Analyze what changes are needed for migration"""

        changes = {
            'auto_fixes': [],
            'manual_review': [],
            'breaking_changes': [],
        }

        # Load version rules
        rules = self._load_version_rules(source_version, target_version)

        # Check fields
        for model in module.model_ids:
            for field in model.field_ids:
                field_changes = self._check_field_compatibility(
                    field, rules
                )
                changes['auto_fixes'].extend(field_changes['auto'])
                changes['manual_review'].extend(field_changes['manual'])

        # Check views
        for view in module.view_ids:
            view_changes = self._check_view_compatibility(view, rules)
            changes['auto_fixes'].extend(view_changes['auto'])
            changes['manual_review'].extend(view_changes['manual'])

        # Check manifest
        manifest_changes = self._check_manifest_compatibility(
            module, rules
        )
        changes['auto_fixes'].extend(manifest_changes['auto'])

        return {
            'auto_count': len(changes['auto_fixes']),
            'manual_count': len(changes['manual_review']),
            'breaking_count': len(changes['breaking_changes']),
            'change_details': self._format_changes(changes),
        }

    def _load_version_rules(self, source, target):
        """Load migration rules from YAML files"""
        import yaml

        source_major = source.split('.')[0]
        target_major = target.split('.')[0]

        rules_path = f'templates/migration_rules/{source_major}_to_{target_major}.yaml'

        # Load rules
        with open(rules_path) as f:
            return yaml.safe_load(f)
```

---

## 📄 Migration Rules Example

```yaml
# templates/migration_rules/19_to_20.yaml
version_info:
  source: "19.0"
  target: "20.0"
  python_min: "3.10"  # Odoo 20 requires Python 3.10+

field_migrations:
  - deprecated: "groups"
    replacement: "groups_id"
    auto_fix: true
    type: "attribute_rename"

  - deprecated: "selection_add"
    replacement: "Use inheritance properly"
    auto_fix: false
    type: "breaking_change"

view_migrations:
  - pattern: '<tree.*editable="top"'
    replacement: '<tree editable="top"'
    auto_fix: true

  - pattern: 'widget="statusbar"'
    note: "Check if still supported"
    auto_fix: false

manifest_migrations:
  - required_new_fields:
      - license
    auto_fix: true
    default_value: "LGPL-3"

  - new_section: "assets"
    note: "Consider moving JS/CSS to assets"
    auto_fix: false

python_migrations:
  - deprecated: "@api.one"
    replacement: "Use @api.model or loop manually"
    auto_fix: false

  - deprecated: "@api.multi"
    replacement: "Remove decorator (default behavior)"
    auto_fix: true
```

---

## 🎯 User Experience

### Scenario 1: Create Multi-Version Compatible Addon

```python
# In ITX Moduler workspace
module = env['itx.moduler.module'].create({
    'name': 'my_crm_custom',
    'shortdesc': 'My CRM Customization',
    'target_odoo_version': 'auto',  # Current system (19.0)
})

# ... design models, fields, views ...

# Export for current version
module.action_export_addon()  # → my_crm_custom_v19.zip

# Export for future version
module.target_odoo_version = '20.0'
module.action_export_addon()  # → my_crm_custom_v20.zip

# Export for multiple versions at once
module.action_export_multi_version(['19.0', '20.0', '21.0'])
# → my_crm_custom_multi_version.zip
#    ├── v19/my_crm_custom/
#    ├── v20/my_crm_custom/
#    └── v21/my_crm_custom/
```

### Scenario 2: Upgrade Existing Addon

```python
# Load existing v19 addon
module = env['itx.moduler.module'].browse(1)
# Current: target_odoo_version = '19.0'

# Click "Upgrade to Odoo 20" button
wizard = env['itx.moduler.version.migration.wizard'].create({
    'module_id': module.id,
    'source_version': '19.0',
    'target_version': '20.0',
})

# View migration report (HTML)
"""
Migration Summary:
- Automatic fixes: 5
  ✓ Update manifest version: 19.0 → 20.0
  ✓ Add 'license' field to manifest
  ✓ Rename 'groups' → 'groups_id' (3 fields)

- Manual review needed: 2
  ⚠ Check widget="statusbar" compatibility (sale_order_view)
  ⚠ Review selection_add usage (state field)

- Breaking changes: 0
"""

# Execute migration
wizard.action_migrate()

# Module updated, ready to export for v20
module.action_export_addon()  # → Uses v20 templates
```

---

## 💡 Advanced Features (Future)

### 1. AI-Assisted Migration

```python
# Use Claude API to help with breaking changes
def ai_suggest_migration(self, breaking_change):
    """Ask Claude for migration suggestion"""

    prompt = f"""
    Odoo version migration help needed:

    Source version: {self.source_version}
    Target version: {self.target_version}

    Breaking change detected:
    {breaking_change.description}

    Current code:
    {breaking_change.current_code}

    Please suggest how to migrate this code to {self.target_version}.
    Provide the updated code and explanation.
    """

    suggestion = claude_api.complete(prompt)
    return suggestion
```

### 2. Compatibility Testing

```python
# Virtual testing in different Odoo versions
def test_compatibility(self, module, versions):
    """Test module in multiple Odoo versions"""

    results = {}
    for version in versions:
        # Export with version-specific templates
        addon_zip = module.export_for_version(version)

        # Deploy to test environment
        test_env = OdooTestEnvironment(version)
        test_env.install_module(addon_zip)

        # Run tests
        test_results = test_env.run_tests()

        results[version] = {
            'passed': test_results.passed,
            'failed': test_results.failed,
            'errors': test_results.errors,
        }

    return results
```

### 3. Version Compatibility Badge

```xml
<!-- In module readme -->
<div class="compatibility-badges">
    <span class="badge odoo-19">✓ Odoo 19</span>
    <span class="badge odoo-20">✓ Odoo 20</span>
    <span class="badge odoo-21">✓ Odoo 21</span>
</div>
```

---

## 📊 Benefits Summary

| Aspect | Benefit |
|--------|---------|
| **Development** | Write once, export for multiple versions |
| **Maintenance** | Update snapshots, re-export for all versions |
| **Future-proof** | Easy to add new Odoo version support |
| **Quality** | Version-specific optimizations |
| **Migration** | Automated upgrade path with warnings |
| **Testing** | Can test across versions before deployment |
| **Documentation** | Auto-generated compatibility matrix |

---

## 🎯 Success Criteria

1. ✅ **Single snapshot → Multiple versions**
   - Same snapshot data exports correctly for v19, v20, v21

2. ✅ **Automated migration**
   - 80%+ of version upgrades automatic
   - Clear warnings for manual review items

3. ✅ **Quality preservation**
   - Version-specific code follows best practices
   - No "lowest common denominator" compromises

4. ✅ **Easy maintenance**
   - Add new Odoo version support in < 1 week
   - Template updates don't break existing functionality

5. ✅ **User-friendly**
   - One-click version upgrade
   - Clear migration reports
   - Preview before committing

---

## 🔗 Related Documents

- [VISION_AND_WORKFLOW.md](./VISION_AND_WORKFLOW.md) - Overall architecture
- [SNAPSHOT_ARCHITECTURE.md](./SNAPSHOT_ARCHITECTURE.md) - Database design
- [SESSION_MEMO_2025-12-15.md](./SESSION_MEMO_2025-12-15.md) - Recent discussions

---

**Document Version:** 1.0
**Created:** 2025-12-16
**Author:** Claude Sonnet 4.5
**Status:** 📋 Design & Planning - Ready for Implementation

---

## ✅ Decision Made - Next Actions

### Immediate (NOW)
1. ✅ **Focus 100% on Odoo 19**
2. 🔄 Refactor code generator → Jinja2 templates
3. 🔄 Add Black formatter
4. 🔄 Test & stabilize v19 export

### Keep in Mind (While doing Phase 1)
- 🧠 Design templates to be version-flexible
- 🧠 Don't hardcode v19-specific assumptions
- 🧠 Comment where version differences might occur
- 🧠 Use `common/` for shared code

### Future (Don't do yet!)
- ⏸️ v20 templates (wait for Odoo 20 release)
- ⏸️ Migration wizard (after v20 support exists)
- ⏸️ AI integration (Phase 4)

---

## 💡 The 2C Philosophy (Chainarp + Claude)

**Principles:**
1. 🚀 **เดินหน้าอย่างเดียว** - No backwards compatibility waste
2. 🎯 **Focus สุดๆ** - v19 perfect before v20
3. 🧠 **Plan ahead** - Architecture supports future without premature implementation
4. 🤝 **SA + AI** - Human + Claude collaboration
5. 🎉 **WOW effect** - Every feature must impress

**Why this works:**
- ✅ Not wasting time on old versions nobody uses
- ✅ Solid foundation (v19) before expansion (v20)
- ✅ Architecture ready for migration when needed
- ✅ No technical debt from poor planning

---

## 🔮 Looking Ahead: Odoo 20 + AI

**Expectations for Odoo 20:**
- 🤖 More AI integration (OCA working on it)
- 📊 Better analytics tools
- 🎨 Improved UI/UX
- ⚡ Performance improvements

**ITX Moduler advantage:**
- 🧠 We already have AI (Claude) in our DNA
- 🏗️ Snapshot architecture is AI-friendly (SQL generation)
- 🎯 Can integrate with Odoo's AI or keep our own
- 💪 Competitive edge: 2C = Chainarp expertise + Claude power

---

## Next Steps

### Phase 1 Tasks (IN PROGRESS)
1. 🔄 Add Download Addon button to workspace
2. 🔄 Test Load → Export workflow completely
3. 🔄 Create Jinja2 template structure
4. 🔄 Refactor code generator
5. 🔄 Add Black formatter integration
6. 🔄 Document template customization guide

**Focus:** Make v19 export **perfect** before thinking about v20!
