# ITX Moduler - Version Control & Git Integration

**Date:** 2024-12-17
**Status:** 📋 Design Notes / Future Implementation
**Priority:** HIGH - Critical for Production Use

---

## 🔴 Problem Statement

### Real Issues Encountered

**Current Session Example:**
1. แก้ view_mode เพิ่ม kanban → Database พัง
2. พยายามแก้ DB → ยิ่งพัง (ir.ui.menu หาย)
3. สร้าง DB ใหม่ → ParseError XML
4. แก้ XML → Loading order ผิด
5. แก้อีกครั้ง → ใช้ได้ในที่สุด (ใช้เวลา 1-2 ชม.)

**ถ้ามี Git:**
```bash
git reset --hard
# กลับไปจุดเริ่มต้นทันที ใช้เวลา 5 วินาที
```

### Core Problem

ITX Moduler ปัจจุบันไม่มี **Safety Net** ทำให้:

❌ **Export แล้วพัง** → ไม่สามารถกู้คืนได้
❌ **แก้ไขหลายรอบ** → ไม่รู้ว่าอะไรเปลี่ยนไป
❌ **AI ทำพัง** → Developer ปกติแก้ไม่ได้ (โค้ดมาก + ซับซ้อน)
❌ **ไม่กล้าใช้ในงานจริง** → กลัวพังแล้วกู้ไม่ได้

---

## 💡 Solution Concepts

### Concept 1: Built-in Version Control (Time Machine)

```
┌─────────────────────────────────────┐
│ ITX Moduler Workspace               │
├─────────────────────────────────────┤
│ 📸 Snapshots (Versions)             │
│   ├─ v1.0.0 (2024-01-15 10:30)     │
│   ├─ v1.0.1 (2024-01-15 14:20) ✓   │
│   └─ v1.1.0 (2024-01-16 09:15)     │
│                                     │
│ 🔍 Diff Viewer                      │
│   Compare: v1.0.0 ↔ v1.0.1         │
│   + Added: 2 fields to model       │
│   - Removed: 1 view                │
│   ~ Modified: ACLs                 │
│                                     │
│ ⏪ Rollback Button                  │
│   Restore workspace to v1.0.1      │
└─────────────────────────────────────┘
```

**Features:**
- Auto-save ทุกครั้งที่ Export/Load
- Manual save ก่อนทำการเปลี่ยนแปลงใหญ่
- One-click restore
- View history timeline

---

## 🎯 Implementation Options

### Option 1: Export to Folder (Easiest - RECOMMENDED START)

**Concept:**
```python
def action_export_to_folder(self):
    """Export addon directly to folder (for git workflow)"""
    export_path = self.env['ir.config_parameter'].sudo().get_param(
        'itx_moduler.export_path',
        '/opt/odoo/custom_addons'
    )

    module_path = os.path.join(export_path, self.name)
    self._generate_module_files(module_path)

    return {
        'type': 'ir.actions.client',
        'tag': 'display_notification',
        'params': {
            'message': f'✅ Exported to {module_path}',
            'type': 'success',
        }
    }
```

**User Workflow:**
```bash
cd /opt/odoo/custom_addons
git init
# Export from ITX Moduler UI
git add .
git commit -m "Initial commit from ITX Moduler"
```

**Pros:**
- ✅ ง่ายที่สุด - ไม่ต้องจัดการ git ใน Odoo
- ✅ Flexible - User control commit message เอง
- ✅ Safe - ไม่มี auto commit ที่อาจผิดพลาด
- ✅ เขียนโค้ดน้อย

**Cons:**
- ❌ Manual - ต้อง commit เอง
- ❌ ไม่มี integration กับ Odoo UI

---

### Option 2: Git Integration in Settings

**Concept:**
```python
# Settings fields
git_enabled = fields.Boolean('Enable Git Integration', default=False)
git_repo_path = fields.Char('Repository Path', default='/opt/odoo/custom_addons')
git_auto_commit = fields.Boolean('Auto Commit on Export', default=True)
git_commit_template = fields.Text('Commit Message Template',
    default='[ITX Moduler] {module_name} - {action}')

def action_export_with_git(self):
    # 1. Export files to folder
    self._generate_module_files(self.git_repo_path)

    # 2. Git operations (if enabled)
    if self.git_enabled and self.git_auto_commit:
        commit_msg = self.git_commit_template.format(
            module_name=self.name,
            action='Export from workspace'
        )
        os.system(f'cd {self.git_repo_path} && git add . && git commit -m "{commit_msg}"')

    # 3. Save version to history
    self._create_version_snapshot()
```

**UI Enhancement:**
```xml
<page string="Git Settings">
    <group>
        <field name="git_enabled"/>
        <field name="git_repo_path" invisible="not git_enabled"/>
        <field name="git_auto_commit" invisible="not git_enabled"/>
        <field name="git_commit_template" invisible="not git_enabled"/>
    </group>
</page>
```

**Pros:**
- ✅ Semi-automated
- ✅ User control via settings
- ✅ Visible in Odoo UI

**Cons:**
- ❌ ต้องจัดการ git errors
- ❌ Security concerns (shell commands)

---

### Option 3: GitPython Library (Professional)

**Concept:**
```python
from git import Repo

def action_commit_to_git(self):
    """Professional git integration using GitPython"""
    try:
        repo = Repo(self.git_repo_path)

        # Export files
        self._generate_module_files(self.git_repo_path)

        # Git add
        repo.index.add('*')

        # Git commit
        commit_msg = f'[ITX Moduler] {self.name} - {self.shortdesc}'
        repo.index.commit(commit_msg)

        # Optional: Auto push
        if self.git_auto_push:
            origin = repo.remote(name='origin')
            origin.push()

    except Exception as e:
        raise ValidationError(f'Git error: {str(e)}')
```

**Pros:**
- ✅ Professional solution
- ✅ Better error handling
- ✅ Can show git status in UI
- ✅ Can implement diff viewer

**Cons:**
- ❌ External dependency (GitPython)
- ❌ More complex
- ❌ Need to handle auth/credentials

---

### Option 4: Workspace Snapshots = Git Commits

**Concept:** ทุกครั้งที่ Load/Export → auto create snapshot in DB

```python
class ItxModulerVersion(models.Model):
    _name = 'itx.moduler.version'
    _description = 'Workspace Version History'
    _order = 'created_date desc'

    module_id = fields.Many2one('itx.moduler.module', required=True, ondelete='cascade')
    version = fields.Char(required=True)  # v1.0.0
    created_date = fields.Datetime(default=fields.Datetime.now, readonly=True)
    created_by = fields.Many2one('res.users', default=lambda self: self.env.user)

    # Snapshot data (serialized JSON)
    snapshot_data = fields.Serialized()  # {models: [...], views: [...], ...}

    # Metadata
    action = fields.Selection([
        ('load', 'Loaded from Odoo'),
        ('export', 'Exported to file'),
        ('manual', 'Manual save'),
    ])
    comment = fields.Text('Notes')
    file_hash = fields.Char('SHA256 Hash')  # For integrity check
```

**Snapshot workflow:**
```python
def action_import_snapshots(self):
    # ... existing import logic ...

    # Create version snapshot
    self._create_version_snapshot(action='load', comment='Loaded from Odoo')

def _create_version_snapshot(self, action='manual', comment=''):
    """Create a point-in-time snapshot of workspace"""
    snapshot_data = {
        'models': self._serialize_models(),
        'views': self._serialize_views(),
        'menus': self._serialize_menus(),
        'actions': self._serialize_actions(),
        'groups': self._serialize_groups(),
        'acls': self._serialize_acls(),
    }

    # Generate version number
    last_version = self.env['itx.moduler.version'].search([
        ('module_id', '=', self.id)
    ], order='version desc', limit=1)

    new_version = self._increment_version(last_version.version if last_version else '0.0.0')

    self.env['itx.moduler.version'].create({
        'module_id': self.id,
        'version': new_version,
        'snapshot_data': snapshot_data,
        'action': action,
        'comment': comment,
    })
```

**Restore from snapshot:**
```python
def action_restore_version(self, version_id):
    """Restore workspace to a previous version"""
    version = self.env['itx.moduler.version'].browse(version_id)
    snapshot = version.snapshot_data

    # Clear current data
    self.o2m_models.unlink()
    self.o2m_views.unlink()
    # ...

    # Restore from snapshot
    self._restore_models(snapshot['models'])
    self._restore_views(snapshot['views'])
    # ...
```

**Pros:**
- ✅ Complete history in DB
- ✅ No external dependencies
- ✅ Fast restore
- ✅ Can implement diff viewer

**Cons:**
- ❌ DB size grows (need cleanup old versions)
- ❌ Complex serialization/deserialization

---

## 📋 Required Features for Production

### 1. Workspace Versioning (CRITICAL!)

**Must have:**
- ✅ Auto-save on Load/Export
- ✅ Manual save button
- ✅ Version history list
- ✅ One-click restore
- ✅ Version comparison (diff)

**Model:**
```python
class ItxModulerVersion(models.Model):
    _name = 'itx.moduler.version'

    module_id = fields.Many2one('itx.moduler.module')
    version = fields.Char()
    created_date = fields.Datetime()
    snapshot_data = fields.Serialized()
    comment = fields.Text()
```

---

### 2. Export Validation (CRITICAL!)

**Prevent broken exports:**
```python
def validate_before_export(self):
    """Check for common issues before export"""
    errors = []
    warnings = []

    # Critical errors (block export)
    if not self.o2m_models:
        errors.append("❌ No models defined")

    for model in self.o2m_models:
        if not model.field_ids:
            errors.append(f"❌ Model {model.model} has no fields")

    # Warnings (allow but notify)
    for model in self.o2m_models:
        acls = self.o2m_model_access.filtered(lambda a: a.model_id == model)
        if not acls:
            warnings.append(f"⚠️  Model {model.model} has no ACLs")

    if not self.o2m_views:
        warnings.append("⚠️  No views defined")

    if not self.o2m_menus:
        warnings.append("⚠️  No menus defined")

    # Show results
    if errors:
        raise ValidationError('\n'.join(errors))

    if warnings:
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Export Warnings',
                'message': '\n'.join(warnings),
                'type': 'warning',
                'sticky': True,
            }
        }
```

---

### 3. Backup Before Export (CRITICAL!)

**Auto backup workspace before any destructive operation:**
```python
def action_export_addon(self):
    # 1. Create backup first
    self._create_version_snapshot(
        action='export',
        comment='Auto-backup before export'
    )

    # 2. Validate
    self.validate_before_export()

    # 3. Export
    return self._do_export()
```

---

### 4. Diff Viewer (Nice to have)

**Compare two versions:**
```python
def action_view_diff(self, version1_id, version2_id):
    """Show differences between two versions"""
    v1 = self.env['itx.moduler.version'].browse(version1_id)
    v2 = self.env['itx.moduler.version'].browse(version2_id)

    diff = {
        'models': self._diff_models(v1.snapshot_data['models'], v2.snapshot_data['models']),
        'views': self._diff_views(v1.snapshot_data['views'], v2.snapshot_data['views']),
        # ...
    }

    return {
        'type': 'ir.actions.client',
        'tag': 'display_diff_viewer',
        'params': {'diff': diff}
    }
```

---

## 🔧 Implementation Roadmap

### Phase 1: IMMEDIATE (ก่อนส่งงาน)

**Priority:** 🔴 CRITICAL

1. ✅ **Export to Folder**
   - เพิ่มปุ่ม "📁 Export to Folder"
   - Settings → Export Path
   - แก้ code generator ให้ export ได้ทั้ง ZIP + Folder

2. ✅ **Export Validation**
   - ตรวจสอบก่อน export
   - Block ถ้ามี critical errors
   - Warn ถ้ามี warnings

3. ✅ **Auto Backup Before Export**
   - สร้าง snapshot ก่อน export ทุกครั้ง
   - เก็บ 10 backups ล่าสุด
   - Auto cleanup old backups

**Estimated time:** 2-3 hours

---

### Phase 2: SHORT-TERM (สัปดาห์หน้า)

**Priority:** 🟡 HIGH

4. ⏳ **Workspace Versioning**
   - `itx.moduler.version` model
   - Version history list view
   - Manual save button

5. ⏳ **Rollback Function**
   - One-click restore
   - Confirm dialog
   - Show what will change

**Estimated time:** 1 day

---

### Phase 3: MID-TERM (เดือนหน้า)

**Priority:** 🟢 MEDIUM

6. ⏳ **Git Auto-commit**
   - Settings → Git integration
   - Auto commit on export (optional)
   - Commit message template

7. ⏳ **Diff Viewer**
   - Compare versions side-by-side
   - Show added/removed/modified
   - Color-coded changes

**Estimated time:** 2-3 days

---

### Phase 4: LONG-TERM (Future)

**Priority:** 🔵 LOW

8. ⏳ **GitPython Integration**
   - Professional git handling
   - Show git status in UI
   - Branch management

9. ⏳ **Collaboration Features**
   - Share workspace via git
   - Merge changes
   - Conflict resolution

**Estimated time:** 1 week

---

## 🎓 Lessons Learned

### 3 Golden Rules for Working with AI

> **"การทำงานกับ AI ต้องมี Safety Net"**

1. **Never Trust AI 100%**
   - ต้อง verify ทุกครั้ง
   - Test ก่อนใช้จริง
   - มี backup เสมอ

2. **Always Keep History**
   - Rollback ได้ตลอด
   - เห็นว่าอะไรเปลี่ยนไป
   - สามารถกู้คืนได้

3. **Validate Before Apply**
   - ตรวจสอบก่อน commit
   - Block การทำงานที่อันตราย
   - Warn ถ้ามีปัญหา

---

## 💭 Why This Matters

### ITX Moduler จะมีคนใช้จริง ต้องมี:

1. ✅ **Undo/Redo** - แก้ผิด rollback ได้
2. ✅ **Export History** - เห็นว่า export ไปกี่รอบ อะไรเปลี่ยน
3. ✅ **Git Integration** - sync กับ version control
4. ✅ **Validation** - ป้องกันพัง
5. ✅ **Diff Viewer** - เปรียบเทียบ versions

### ถ้าไม่มี:

❌ **Developer กลัวใช้** เพราะ:
- ไม่กล้า export เพราะกลัวพัง
- แก้ไขไม่ได้ถ้า AI ทำผิด
- ไม่รู้ว่าอะไรเปลี่ยนไป
- ไม่มีทางกู้คืน

✅ **ถ้ามี:**
- มั่นใจใช้งาน
- ทดลองได้ไม่กลัว
- แก้ไขง่าย rollback เร็ว
- Professional workflow

---

## 📝 Next Steps

**Recommendation:**

Start with **Quick Wins** (Phase 1):
- Export to Folder
- Validation
- Auto Backup

**Benefit:**
- ✅ ได้ safety net พื้นฐาน
- ✅ ใช้เวลาไม่เกิน 2-3 ชม.
- ✅ สามารถใช้งานจริงได้ทันที
- ✅ ทำ full version control ทีหลัง

**Then:** Complete current testing → Implement Phase 1 → Plan Phase 2

---

## 🔗 Related Documents

- `TESTING_WORKFLOW.md` - Current testing procedures
- `EXPORT_VALIDATION.md` - Export validation rules
- `GIT_INTEGRATION.md` - Detailed git integration specs

---

**Author:** Claude Code + Chainarp
**Last Updated:** 2024-12-17
**Status:** 📋 Design Document
