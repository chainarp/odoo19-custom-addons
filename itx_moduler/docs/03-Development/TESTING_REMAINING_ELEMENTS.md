# Testing Remaining Elements

**วันที่:** 2024-12-17
**Status:** 📋 Testing Guide
**Elements ที่ยังไม่ได้ทดสอบ:** Rules, SQL Constraints, Server Constraints, Action Servers, Reports

---

## 🎯 เป้าหมาย

ทดสอบว่า ITX Moduler สามารถ **Load → Export → Install** elements ต่าง ๆ เหล่านี้ได้ถูกต้องครบถ้วน:

1. **Rules** (Record Rules / Row-level Security)
2. **SQL Constraints** (Database-level constraints)
3. **Server Constraints** (Python @api.constrains)
4. **Action Servers** (Automated Actions)
5. **Reports** (QWeb Reports, PDF)

---

## 📋 Current Status: itx_helloworld

**Elements ที่มีอยู่แล้ว:**
- ✅ Models (2): itx.helloworld, itx.license.info.wizard
- ✅ Views (4): form, list, wizard form, wizard list
- ✅ Menus (2): ITX Hello World, submenu
- ✅ Actions (2): window action, wizard action
- ✅ Groups (2): User, Manager
- ✅ ACLs (6): access control lists

**Elements ที่ยังไม่มี:**
- ❌ Rules (0)
- ❌ SQL Constraints (0)
- ❌ Server Constraints (0)
- ❌ Action Servers (0)
- ❌ Reports (0)

---

## 🔧 แนวทางการทดสอบ

### แนวทาง A: เพิ่ม Elements ใน itx_helloworld (แนะนำ)

**ข้อดี:**
- ✅ ทดสอบได้ครบทุก element ในโมดูลเดียว
- ✅ เห็นผลชัดเจนว่า Load → Export ได้ครบหรือไม่
- ✅ สามารถ compare กับ original ได้ง่าย

**ขั้นตอน:**
1. เพิ่ม elements ทั้ง 5 ประเภทใน itx_helloworld
2. Upgrade itx_helloworld
3. Load into ITX Moduler workspace
4. Export addon
5. Uninstall original
6. Install exported addon
7. ตรวจสอบว่า elements ครบถ้วน

---

### แนวทาง B: สร้าง Test Module ใหม่

**ข้อดี:**
- ✅ ไม่กระทบ itx_helloworld เดิม
- ✅ สามารถ focus แค่ elements ที่ต้องการทดสอบ

**ข้อเสีย:**
- ❌ ต้องสร้างโมดูลใหม่
- ❌ ใช้เวลานานกว่า

---

## 💡 แนะนำ: แนวทาง A

ให้เพิ่ม elements ลงใน itx_helloworld ดังนี้:

---

## 📝 1. Record Rules (Row-level Security)

**คืออะไร:** กำหนดว่า user แต่ละกลุ่มเห็น records ไหนได้บ้าง

**ตัวอย่าง:** User เห็นได้เฉพาะ records ที่ตัวเองสร้าง, Manager เห็นทั้งหมด

**สร้างไฟล์:** `security/itx_helloworld_rules.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Rule: User sees only own records -->
    <record id="itx_helloworld_user_rule" model="ir.rule">
        <field name="name">ITX Hello World: User sees own records</field>
        <field name="model_id" ref="model_itx_helloworld"/>
        <field name="domain_force">[('create_uid', '=', user.id)]</field>
        <field name="groups" eval="[(4, ref('group_itx_helloworld_user'))]"/>
    </record>

    <!-- Rule: Manager sees all records -->
    <record id="itx_helloworld_manager_rule" model="ir.rule">
        <field name="name">ITX Hello World: Manager sees all</field>
        <field name="model_id" ref="model_itx_helloworld"/>
        <field name="domain_force">[(1, '=', 1)]</field>
        <field name="groups" eval="[(4, ref('group_itx_helloworld_manager'))]"/>
    </record>
</odoo>
```

**เพิ่มใน __manifest__.py:**
```python
'data': [
    'security/itx_helloworld_groups.xml',
    'security/itx_helloworld_rules.xml',  # ← เพิ่มบรรทัดนี้
    'security/ir.model.access.csv',
    ...
],
```

---

## 📝 2. SQL Constraints

**คืออะไร:** ข้อจำกัดระดับ database (NOT NULL, UNIQUE, CHECK)

**ตัวอย่าง:** name ต้องไม่ซ้ำ, value ต้อง > 0

**แก้ไฟล์:** `models/itx_helloworld.py`

```python
class ItxHelloworld(models.Model):
    _name = 'itx.helloworld'
    _description = 'ITX Hello World'

    name = fields.Char(required=True)
    value = fields.Integer()

    # เพิ่ม SQL Constraints
    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'Name must be unique!'),
        ('value_positive', 'CHECK(value >= 0)', 'Value must be positive!'),
    ]
```

**ทดสอบ:**
```python
# Test 1: ลอง create 2 records ชื่อเดียวกัน → ควร error
record1 = env['itx.helloworld'].create({'name': 'Test'})
record2 = env['itx.helloworld'].create({'name': 'Test'})  # ← Error!

# Test 2: ลองใส่ค่าติดลบ → ควร error
record3 = env['itx.helloworld'].create({'name': 'Test2', 'value': -10})  # ← Error!
```

---

## 📝 3. Server Constraints (Python Validation)

**คืออะไร:** ตรวจสอบข้อมูลด้วย Python code

**ตัวอย่าง:** ตรวจสอบ format email, ค่าต้องอยู่ในช่วงที่กำหนด

**แก้ไฟล์:** `models/itx_helloworld.py`

```python
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ItxHelloworld(models.Model):
    _name = 'itx.helloworld'
    _description = 'ITX Hello World'

    name = fields.Char(required=True)
    email = fields.Char()
    value = fields.Integer()

    # เพิ่ม Server Constraints
    @api.constrains('email')
    def _check_email_format(self):
        """Validate email format"""
        for record in self:
            if record.email and '@' not in record.email:
                raise ValidationError('Invalid email format! Must contain @')

    @api.constrains('value')
    def _check_value_range(self):
        """Validate value is between 0 and 100"""
        for record in self:
            if record.value and not (0 <= record.value <= 100):
                raise ValidationError('Value must be between 0 and 100!')
```

**ทดสอบ:**
```python
# Test 1: Email ไม่มี @ → ควร error
record1 = env['itx.helloworld'].create({
    'name': 'Test',
    'email': 'invalid-email'  # ← Error!
})

# Test 2: Value เกิน 100 → ควร error
record2 = env['itx.helloworld'].create({
    'name': 'Test2',
    'value': 150  # ← Error!
})
```

---

## 📝 4. Action Servers (Automated Actions)

**คืออะไร:** ทำงานอัตโนมัติเมื่อเกิด event (create, write, delete)

**ตัวอย่าง:** Auto-send email เมื่อสร้าง record ใหม่, Auto-archive หลัง 30 วัน

**สร้างไฟล์:** `data/itx_helloworld_actions.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Automated Action: Set default value on create -->
    <record id="action_set_default_value" model="ir.actions.server">
        <field name="name">ITX Hello World: Set Default Value</field>
        <field name="model_id" ref="model_itx_helloworld"/>
        <field name="state">code</field>
        <field name="code">
# Set default value to 50 if not set
for record in records:
    if not record.value:
        record.value = 50
        </field>
    </record>

    <!-- Automated Action Trigger -->
    <record id="base_automation_set_value" model="base.automation">
        <field name="name">ITX Hello World: Auto Set Value</field>
        <field name="model_id" ref="model_itx_helloworld"/>
        <field name="state">code</field>
        <field name="trigger">on_create</field>
        <field name="code">
for record in records:
    if not record.value:
        record.value = 50
        </field>
    </record>
</odoo>
```

**เพิ่มใน __manifest__.py:**
```python
'data': [
    ...
    'data/itx_helloworld_actions.xml',  # ← เพิ่มบรรทัดนี้
],
```

**ทดสอบ:**
```python
# Test: Create record โดยไม่ใส่ value → ควรได้ value = 50 อัตโนมัติ
record = env['itx.helloworld'].create({'name': 'Test'})
print(record.value)  # → 50
```

---

## 📝 5. Reports (QWeb PDF)

**คืออะไร:** สร้าง PDF report จากข้อมูล

**ตัวอย่าง:** พิมพ์ใบรายงาน, Export PDF

**สร้างไฟล์:** `reports/itx_helloworld_report.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Report Action -->
    <record id="action_report_itx_helloworld" model="ir.actions.report">
        <field name="name">ITX Hello World Report</field>
        <field name="model">itx.helloworld</field>
        <field name="report_type">qweb-pdf</field>
        <field name="report_name">itx_helloworld.report_itx_helloworld_document</field>
        <field name="report_file">itx_helloworld.report_itx_helloworld_document</field>
        <field name="binding_model_id" ref="model_itx_helloworld"/>
        <field name="binding_type">report</field>
    </record>

    <!-- Report Template -->
    <template id="report_itx_helloworld_document">
        <t t-call="web.html_container">
            <t t-foreach="docs" t-as="o">
                <t t-call="web.external_layout">
                    <div class="page">
                        <h2>ITX Hello World Report</h2>
                        <div class="row">
                            <div class="col-6">
                                <strong>Name:</strong> <span t-field="o.name"/>
                            </div>
                            <div class="col-6">
                                <strong>Value:</strong> <span t-field="o.value"/>
                            </div>
                        </div>
                        <div class="row mt-3">
                            <div class="col-12">
                                <strong>Description:</strong>
                                <p t-field="o.description"/>
                            </div>
                        </div>
                    </div>
                </t>
            </t>
        </t>
    </template>
</odoo>
```

**เพิ่มใน __manifest__.py:**
```python
'data': [
    ...
    'reports/itx_helloworld_report.xml',  # ← เพิ่มบรรทัดนี้
],
```

**ทดสอบ:**
- เข้า ITX Hello World → เปิด record
- กด Print → ITX Hello World Report
- ควรได้ไฟล์ PDF

---

## ✅ Testing Checklist

### Phase 1: เพิ่ม Elements
- [ ] สร้าง `security/itx_helloworld_rules.xml`
- [ ] เพิ่ม `_sql_constraints` ใน model
- [ ] เพิ่ม `@api.constrains` ใน model
- [ ] สร้าง `data/itx_helloworld_actions.xml`
- [ ] สร้าง `reports/itx_helloworld_report.xml`
- [ ] Update `__manifest__.py`

### Phase 2: Upgrade & Test Original
- [ ] Restart Odoo
- [ ] Upgrade itx_helloworld
- [ ] ทดสอบแต่ละ element ว่าทำงานได้

### Phase 3: Load into ITX Moduler
- [ ] Load itx_helloworld into workspace
- [ ] ตรวจสอบว่า elements ครบ 5 ประเภท:
  - [ ] Rules tab มี records
  - [ ] SQL Constraints tab มี records
  - [ ] Server Constraints tab มี records
  - [ ] Action Servers tab มี records
  - [ ] Reports tab มี records

### Phase 4: Export & Install
- [ ] Download Addon (ZIP)
- [ ] Extract และตรวจสอบไฟล์:
  - [ ] `security/*_rules.xml` มีหรือไม่
  - [ ] `models/*.py` มี `_sql_constraints` หรือไม่
  - [ ] `models/*.py` มี `@api.constrains` หรือไม่
  - [ ] `data/*_actions.xml` มีหรือไม่
  - [ ] `reports/*.xml` มีหรือไม่
- [ ] Uninstall original itx_helloworld
- [ ] Install exported addon
- [ ] ทดสอบแต่ละ element ว่าทำงานเหมือนเดิม

---

## 🔍 วิธีตรวจสอบว่า Elements โหลดครบหรือไม่

### ตรวจสอบ Rules:
```python
rules = env['ir.rule'].search([('model_id.model', '=', 'itx.helloworld')])
print(f"Found {len(rules)} rules:")
for rule in rules:
    print(f"  - {rule.name}")
```

### ตรวจสอบ SQL Constraints:
```python
constraints = env['ir.model.constraint'].search([('model', '=', 'itx.helloworld')])
print(f"Found {len(constraints)} SQL constraints:")
for cons in constraints:
    print(f"  - {cons.name}: {cons.type}")
```

### ตรวจสอบ Server Constraints:
```python
# ดูใน Python code
model = env['itx.helloworld']
print(dir(model))  # หา _check_* methods
```

### ตรวจสอบ Action Servers:
```python
actions = env['ir.actions.server'].search([('model_id.model', '=', 'itx.helloworld')])
print(f"Found {len(actions)} server actions:")
for action in actions:
    print(f"  - {action.name}")
```

### ตรวจสอบ Reports:
```python
reports = env['ir.actions.report'].search([('model', '=', 'itx.helloworld')])
print(f"Found {len(reports)} reports:")
for report in reports:
    print(f"  - {report.name}")
```

---

## 📊 Expected Results

**Before (current):**
```
Models: 2 ✅
Views: 4 ✅
Menus: 2 ✅
Actions: 2 ✅
Groups: 2 ✅
ACLs: 6 ✅
Rules: 0 ❌
SQL Constraints: 0 ❌
Server Constraints: 0 ❌
Action Servers: 0 ❌
Reports: 0 ❌
```

**After (target):**
```
Models: 2 ✅
Views: 4 ✅
Menus: 2 ✅
Actions: 2 ✅
Groups: 2 ✅
ACLs: 6 ✅
Rules: 2 ✅
SQL Constraints: 2 ✅
Server Constraints: 2 ✅
Action Servers: 1 ✅
Reports: 1 ✅
```

---

## 🎯 Success Criteria

**การทดสอบสำเร็จ** เมื่อ:
1. ✅ Load ได้ครบ 5 elements
2. ✅ Export ได้ครบ (มีไฟล์และโค้ดครบ)
3. ✅ Install exported addon ได้ไม่ error
4. ✅ Elements ทำงานเหมือนเดิมทุกประการ

---

**Author:** Claude Code + Chainarp
**Last Updated:** 2024-12-17
