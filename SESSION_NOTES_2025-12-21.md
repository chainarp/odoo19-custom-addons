# ITX Moduler - Session Notes (2025-12-21)

## 🎉 สรุปความสำเร็จวันนี้

### ✅ **SNAPSHOT ARCHITECTURE ใช้งานได้แล้ว!**

ปัญหาหลักที่แก้ได้วันนี้: **Groups และ ACLs หายไปหลังจาก uninstall module**

**ผลการทดสอบ:**
- ก่อน uninstall: Groups(2), ACLs(6), Rules(3), Server Actions(3), Reports(1), SQL Constraints(1)
- **หลัง uninstall itx_helloworld: ข้อมูลทุกอย่างยังอยู่ครบ!** ✅

นี่หมายความว่า Snapshot Architecture ทำงานได้สมบูรณ์แล้ว!

---

## 🔧 สิ่งที่แก้ไขวันนี้

### 1. **Snapshot Architecture Implementation**

**วิธีเก่า (อันตราย):**
```python
# เปลี่ยน ownership ของ records ต้นฉบับ
ir_groups.write({'module': new_module.id})
# ⚠️ เมื่อ uninstall → records หายไปด้วย!
```

**วิธีใหม่ (Snapshot):**
```python
# สร้าง snapshot copies ใน itx.moduler.* tables
self.env['itx.moduler.group'].create({...})
# ✅ เมื่อ uninstall → snapshots ยังอยู่!
```

**ไฟล์ที่แก้:** `/home/chainarp/PycharmProjects/odoo19/custom_addons/itx_moduler/models/itx_moduler_module.py`
- **Lines 425-461**: Comment out โค้ดเก่าที่เปลี่ยน ownership
- **Lines 821-1115**: เพิ่มโค้ด import ทุก elements เข้า snapshot tables
- **Lines 1117-1184**: เพิ่มโค้ด import Python Constraints (ยังไม่ทำงาน)

### 2. **เพิ่ม Snapshot Models ทั้งหมด 7 ตัว**

Models ที่มีอยู่แล้ว:
- `itx.moduler.model` - Models
- `itx.moduler.ui.view` - Views
- `itx.moduler.menu` - Menus
- `itx.moduler.action.window` - Action Windows

**Models ใหม่ที่เพิ่มวันนี้:**
1. `itx.moduler.group` - Security Groups
2. `itx.moduler.acl` - Access Control Lists
3. `itx.moduler.rule` - Record Rules
4. `itx.moduler.server.action` - Server Actions
5. `itx.moduler.report` - Reports
6. `itx.moduler.constraint` - SQL Constraints
7. `itx.moduler.server.constraint` - Python Constraints

### 3. **อัปเดต UI Views**

**ไฟล์:** `/home/chainarp/PycharmProjects/odoo19/custom_addons/itx_moduler/views/itx_moduler.xml`

แก้ไข Elements tabs ให้ใช้ snapshot fields:
- Groups: `o2m_groups_snapshot`
- ACLs: `o2m_acls_snapshot`
- Rules: `o2m_rules_snapshot`
- Server Actions: `o2m_server_actions_snapshot`
- Reports: `o2m_reports_snapshot`
- SQL Constraints: `o2m_constraints_snapshot`
- Python Constraints: `o2m_server_constraints_snapshot`

**ไฟล์:** `/home/chainarp/PycharmProjects/odoo19/custom_addons/itx_moduler/models/itx_moduler_module.py`
- **Lines 203-250**: เพิ่ม 7 One2many fields สำหรับ snapshot relationships
- **Lines 232-279**: เพิ่ม 7 computed fields สำหรับนับจำนวน
- **Lines 321-395**: อัปเดต `_compute_workspace_stats()` ให้นับ snapshot records

### 4. **Odoo 19 Compatibility Fixes**

#### 4.1 SQL Constraints → models.Constraint

**ไฟล์ที่แก้:**
- `itx_moduler/models/itx_moduler_model.py` (line 360-363)
- `itx_moduler/models/itx_moduler_model_field.py` (3 ที่)
- `itx_helloworld/models/models.py` (line 29-33)

**เปลี่ยนจาก:**
```python
_sql_constraints = [
    ('name_unique', 'UNIQUE(name)', 'Error message'),
]
```

**เป็น:**
```python
_value_non_negative = models.Constraint(
    'CHECK(value >= 0)',
    'Value must be non-negative (>= 0)!',
)
```

#### 4.2 res.groups.category_id → privilege_id.category_id

**ไฟล์:** `itx_moduler/models/itx_moduler_module.py` (lines 843-854)

```python
# Odoo 19: res.groups.category_id moved to res.groups.privilege_id.category_id
category_id = False
try:
    if hasattr(ir_group, 'privilege_id') and ir_group.privilege_id:
        # Odoo 19+: category is under privilege
        if hasattr(ir_group.privilege_id, 'category_id') and ir_group.privilege_id.category_id:
            category_id = ir_group.privilege_id.category_id.id
    elif hasattr(ir_group, 'category_id') and ir_group.category_id:
        # Odoo 18 and earlier: category directly on group
        category_id = ir_group.category_id.id
except AttributeError:
    pass
```

#### 4.3 Comment out base.automation dependency

**ไฟล์:** `itx_moduler/models/itx_moduler_server_action.py` (lines 195-201)

```python
# TODO: Re-enable when base_automation is added to dependencies
# automation_id = fields.Many2one('base.automation', ...)
```

### 5. **เพิ่ม Elements ให้ itx_helloworld**

#### 5.1 Security Groups (2 groups)
**ไฟล์:** `itx_helloworld/security/security.xml`
- `group_itx_helloworld_user`
- `group_itx_helloworld_manager`

#### 5.2 Access Control Lists (6 ACLs)
**ไฟล์:** `itx_helloworld/security/ir.model.access.csv`
- User: read, write, create
- Manager: read, write, create, unlink

#### 5.3 Record Rules (3 rules)
**ไฟล์:** `itx_helloworld/security/ir_rule.xml`
1. Users see active records only
2. Managers see all records
3. Users see low value records (value <= 100)

#### 5.4 Server Actions (3 actions)
**ไฟล์:** `itx_helloworld/data/ir_actions_server.xml`
1. Auto-set description based on value
2. Mark high value records
3. Mark as inactive

**Important:** ต้องใช้ `record.write()` แทน `record.field = value` เพราะ Odoo 19 forbidden opcodes

#### 5.5 Report (1 report)
**ไฟล์:**
- `itx_helloworld/report/itx_helloworld_report.xml` (template)
- `itx_helloworld/data/ir_actions_report.xml` (action)

#### 5.6 SQL Constraint (1 constraint)
**ไฟล์:** `itx_helloworld/models/models.py` (lines 29-33)
```python
_value_non_negative = models.Constraint(
    'CHECK(value >= 0)',
    'Value must be non-negative (>= 0)!',
)
```

#### 5.7 Python Constraint (1 constraint)
**ไฟล์:** `itx_helloworld/models/models.py` (lines 49-54)
```python
@api.constrains('name')
def _check_name_length(self):
    """Python Constraint: Name must be at least 3 characters"""
    for record in self:
        if record.name and len(record.name) < 3:
            raise ValidationError('Name must be at least 3 characters long!')
```

### 6. **Validation Relaxation**

**ไฟล์:** `itx_moduler/models/itx_moduler_constraint.py` (lines 138-159)

ปัญหา: Constraint validation ทำให้ import ล้มเหลว

แก้ไข: Skip validation สำหรับ imported constraints
```python
# Only validate if manually creating/editing (state = draft)
# Skip validation for imported constraints from database (state = applied)
if constraint.state != 'draft':
    continue
```

---

## ❌ ปัญหาที่ยังค้างอยู่

### **Python Constraints ยังไม่แสดง (0 แทนที่จะเป็น 1)**

**สาเหตุที่เป็นไปได้:**
1. โค้ด import Python Constraints อาจมี bug
2. `_constraint_methods` attribute อาจไม่มีใน Odoo 19
3. `inspect.getsource()` อาจ fail และไม่ได้ log error

**ไฟล์ที่เกี่ยวข้อง:**
- `/home/chainarp/PycharmProjects/odoo19/custom_addons/itx_moduler/models/itx_moduler_module.py` (lines 1117-1184)

**ต้อง debug:**
1. เช็ค log หลัง import ว่ามี `✅ Imported Python Constraint` หรือไม่
2. เช็คว่า `_constraint_methods` มีค่าอะไร
3. ลองเข้าไปดู `itx.moduler.server.constraint` table ว่ามี record หรือไม่

---

## 📊 ผลลัพธ์ปัจจุบัน

### ✅ Elements ที่แสดงถูกต้อง (หลัง Load from Odoo):
- Groups: **2** ✅
- Models: **2** ✅
- ACLs: **6** ✅
- Rules: **3** ✅
- SQL Constraints: **1** ✅
- Views: **4** ✅
- Action Windows: **2** ✅
- Server Actions: **3** ✅
- Menus: **3** ✅
- Reports: **1** ✅

### ❌ Elements ที่ยังไม่แสดง:
- Python Constraints: **0** (ควรเป็น 1)

### ✅ **Snapshot Persistence Test:**
หลังจาก uninstall itx_helloworld → **ข้อมูลทุกอย่างยังอยู่ครบ!**

---

## 📁 ไฟล์ที่แก้ไขวันนี้

### ITX Moduler Module:

1. **models/itx_moduler_module.py**
   - Comment out ownership-changing code (lines 425-461)
   - เพิ่ม 7 One2many fields (lines 203-250)
   - เพิ่ม 7 computed fields (lines 232-279)
   - อัปเดต `_compute_workspace_stats()` (lines 321-395)
   - เพิ่ม import Groups (lines 821-865)
   - เพิ่ม import ACLs (lines 867-925)
   - เพิ่ม import Rules (lines 927-985)
   - เพิ่ม import Server Actions (lines 987-1040)
   - เพิ่ม import Reports (lines 1042-1076)
   - เพิ่ม import SQL Constraints (lines 1078-1115)
   - เพิ่ม import Python Constraints (lines 1117-1184) - **ยังไม่ทำงาน**
   - Fix res.groups.category_id compatibility (lines 843-854)

2. **models/itx_moduler_model.py**
   - Convert `_sql_constraints` to `models.Constraint` (lines 360-363)

3. **models/itx_moduler_model_field.py**
   - Convert `_sql_constraints` to `models.Constraint` (3 ที่)

4. **models/itx_moduler_server_action.py**
   - Comment out `automation_id` field (lines 195-201)

5. **models/itx_moduler_constraint.py**
   - Relax validation for imported constraints (lines 138-159)

6. **views/itx_moduler.xml**
   - อัปเดต Elements tabs ให้ใช้ snapshot fields (lines 96-128)

### ITX HelloWorld Module:

7. **models/models.py**
   - เพิ่ม SQL Constraint (lines 29-33)
   - เพิ่ม Python Constraint (lines 49-54)

8. **security/ir_rule.xml**
   - เพิ่ม 3 record rules (ไฟล์ใหม่)

9. **data/ir_actions_server.xml**
   - เพิ่ม 3 server actions (ไฟล์ใหม่)

10. **report/itx_helloworld_report.xml**
    - เพิ่ม report template (ไฟล์ใหม่)

11. **data/ir_actions_report.xml**
    - เพิ่ม report action (ไฟล์ใหม่)

12. **__manifest__.py**
    - เพิ่ม data files สำหรับ rules, server actions, reports

---

## 🎯 ขั้นตอนต่อไป (สำหรับ Session ถัดไป)

### 1. **แก้ไข Python Constraints ให้แสดงผล**

**Debug steps:**
```bash
# 1. เช็ค log
grep "Python Constraint" /var/log/odoo/odoo.log

# 2. เช็ค database
psql -U odoo19 -d odoo19 -c "SELECT * FROM itx_moduler_server_constraint;"

# 3. ทดสอบ _constraint_methods
# ใน Python shell:
model = env['itx.helloworld']
print(hasattr(model, '_constraint_methods'))
print(model._constraint_methods if hasattr(model, '_constraint_methods') else 'No attribute')
```

**แนวทางแก้ไข:**
- ลอง hardcode test ดูว่า create record ได้หรือไม่
- เช็คว่า field `code` เป็น required หรือไม่
- ลอง import ด้วยวิธีอื่นแทน `_constraint_methods`

### 2. **ทดสอบ Export Module**

เมื่อ Python Constraints แสดงแล้ว ให้ทดสอบ:
1. Export itx_helloworld เป็น ZIP
2. ตรวจสอบไฟล์ที่ generate:
   - `models/models.py` ควรมี `_check_name_length()`
   - `security/ir_rule.xml` ควรมี 3 rules
   - `data/ir_actions_server.xml` ควรมี 3 server actions
   - `report/` ควรมี report files

### 3. **ทดสอบ Install Module ที่ Export**

1. ลบ itx_helloworld ออก
2. Install module ที่ export มา
3. เช็คว่าทุกอย่างทำงานถูกต้อง

### 4. **Code Cleanup**

- ลบ commented code ที่ไม่ใช้แล้ว
- ปรับ logging ให้ดีขึ้น
- เพิ่ม error handling

---

## 💡 บันทึกสำคัญ

### Odoo 19 Breaking Changes:
1. `_sql_constraints` deprecated → ใช้ `models.Constraint`
2. `res.groups.category_id` → `res.groups.privilege_id.category_id`
3. Server action forbidden opcodes: ห้ามใช้ `record.field = value`, ต้องใช้ `record.write()`
4. `base.automation` ไม่ได้ install default

### Snapshot Architecture Design:
- **ห้าม** เปลี่ยน ownership ของ records ต้นฉบับ
- **ต้อง** สร้าง copies ใน snapshot tables
- **ประโยชน์**: Module workspace เป็นอิสระจากโมดูลต้นฉบับ สามารถ uninstall ได้โดยไม่เสียข้อมูล

### Import Strategy:
1. Import จาก `ir.model.data` เพื่อหา records ที่ belongs to module
2. สร้าง snapshot records ใน `itx.moduler.*` tables
3. Link กับ original records ผ่าน `ir_*_id` fields
4. Set state = 'applied' เพื่อ skip validation

---

## 🎉 สรุป

**วันนี้ประสบความสำเร็จอย่างมาก!** ปัญหาหลักที่ติดอยู่ทั้งวัน (Groups & ACLs หายหลัง uninstall) **ได้รับการแก้ไขเรียบร้อยแล้ว**

Snapshot Architecture ทำงานได้ตามที่ออกแบบไว้ และ ITX Moduler พร้อมใช้งานสำหรับ:
- ✅ Import modules from Odoo
- ✅ Edit in workspace (isolated from original)
- ✅ Persist data after uninstall
- 🚧 Export as new module (ต้องทดสอบเพิ่ม)

เหลือแค่ Python Constraints ที่ต้อง debug ให้แสดงผล แล้ว ITX Moduler จะพร้อมใช้งานเต็มรูปแบบ! 🚀

---

**Written by:** Claude Code (Sonnet 4.5)
**Date:** 2025-12-21
**Session Duration:** ~2 hours
**Token Used:** ~54,000 / 200,000
