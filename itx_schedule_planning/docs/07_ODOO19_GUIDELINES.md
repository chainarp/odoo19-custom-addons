# Odoo 19 Development Guidelines

เอกสารนี้รวบรวมปัญหาและการเปลี่ยนแปลงใน Odoo 19 ที่พบระหว่างพัฒนา module `itx_schedule_planning`

## 1. View Type: `tree` → `list`

### ปัญหา
```
odoo.tools.convert.ParseError: Invalid view type: 'tree'.
Allowed types are: list, form, graph, pivot, calendar, kanban, search, qweb, hierarchy, timeline, activity
```

### สาเหตุ
Odoo 19 เปลี่ยนชื่อ view type จาก `tree` เป็น `list`

### วิธีแก้ไข

**ผิด (Odoo 18 และก่อนหน้า):**
```xml
<record id="my_view_tree" model="ir.ui.view">
    <field name="name">my.model.view.tree</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <tree string="My Model">
            <field name="name"/>
        </tree>
    </field>
</record>
```

**ถูก (Odoo 19):**
```xml
<record id="my_view_list" model="ir.ui.view">
    <field name="name">my.model.view.list</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <list string="My Model">
            <field name="name"/>
        </list>
    </field>
</record>
```

### สิ่งที่ต้องเปลี่ยนทั้งหมด
- `<tree>` → `<list>`
- `</tree>` → `</list>`
- `view_mode="tree,form"` → `view_mode="list,form"`
- Inline tree ใน One2many field: `<tree editable="bottom">` → `<list editable="bottom">`

---

## 2. Chatter ต้องมี mail.thread

### ปัญหา
```
odoo.tools.convert.ParseError: Invalid view definition
```

### สาเหตุ
ใช้ `<chatter/>` ใน form view แต่ model ไม่ได้ inherit จาก `mail.thread`

### วิธีแก้ไข

**ตัวเลือก 1: เพิ่ม mail.thread ใน model**
```python
class MyModel(models.Model):
    _name = 'my.model'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'My Model'
```

**ตัวเลือก 2: ลบ chatter ออกจาก view**
```xml
<!-- ลบบรรทัดนี้ออก -->
<chatter/>
```

### คำแนะนำ
- Master data (เช่น shift type, work pattern) ไม่จำเป็นต้องมี chatter
- Transaction data (เช่น schedule planning, swap request) ควรมี chatter

---

## 3. Button Context: `active_id` → `id`

### ปัญหา
```
Access Rights Inconsistency
field "active_id" does not exist in model
```

### สาเหตุ
Odoo 19 ไม่มี `active_id` ใน view context อีกต่อไป ต้องใช้ `id` แทน

### วิธีแก้ไข

**ผิด (Odoo 18 และก่อนหน้า):**
```xml
<button name="%(my_action)d"
        type="action"
        context="{'default_parent_id': active_id, 'search_default_parent_id': active_id}">
```

**ถูก (Odoo 19):**
```xml
<button name="%(my_action)d"
        type="action"
        context="{'default_parent_id': id, 'search_default_parent_id': id}">
```

---

## 4. Search View: `<group>` อาจมีปัญหา

### ปัญหา
```
Invalid view definition in search view
```

### สาเหตุ
`<group>` ใน search view อาจทำให้เกิดปัญหาใน Odoo 19

### วิธีแก้ไข

**อาจมีปัญหา:**
```xml
<search>
    <field name="name"/>
    <filter string="Archived" name="inactive" domain="[('active', '=', False)]"/>
    <group expand="0" string="Group By">
        <filter string="Status" name="group_state" context="{'group_by': 'state'}"/>
    </group>
</search>
```

**ปลอดภัยกว่า:**
```xml
<search>
    <field name="name"/>
    <filter string="Archived" name="inactive" domain="[('active', '=', False)]"/>
    <separator/>
    <filter string="Status" name="group_state" context="{'group_by': 'state'}"/>
</search>
```

---

## 5. SQL Constraints: `_sql_constraints` → `models.Constraint()`

### ปัญหา
```
Model attribute '_sql_constraints' is no longer supported, please define model.Constraint on the model
```

### สาเหตุ
Odoo 19 เลิกใช้ attribute `_sql_constraints` แล้ว ต้องใช้ `models.Constraint()` แทน

### วิธีแก้ไข

**ผิด (Odoo 18 และก่อนหน้า):**
```python
class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'

    code = fields.Char(string='Code', required=True)

    _sql_constraints = [
        ('code_uniq', 'UNIQUE(code)', 'Code must be unique!'),
        ('name_uniq', 'UNIQUE(name)', 'Name must be unique!'),
    ]
```

**ถูก (Odoo 19):**
```python
class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'

    code = fields.Char(string='Code', required=True)

    # แต่ละ constraint เป็น class attribute แยกกัน
    _code_uniq = models.Constraint(
        'UNIQUE(code)',
        'Code must be unique!',
    )
    _name_uniq = models.Constraint(
        'UNIQUE(name)',
        'Name must be unique!',
    )
```

### รูปแบบ models.Constraint()

```python
models.Constraint(
    sql_definition,     # เช่น 'UNIQUE(code)', 'CHECK(amount > 0)'
    message,            # Error message ที่จะแสดง
    warning=False,      # (optional) ถ้า True จะเป็น warning แทน error
)
```

### ตัวอย่างเพิ่มเติม

**UNIQUE constraint หลายคอลัมน์:**
```python
_employee_date_uniq = models.Constraint(
    'UNIQUE(employee_id, date)',
    'Each employee can only have one entry per date!',
)
```

**CHECK constraint:**
```python
_amount_positive = models.Constraint(
    'CHECK(amount >= 0)',
    'Amount must be positive!',
)
```

---

## 6. สรุป Checklist สำหรับ Odoo 19

เมื่อเขียน module ใหม่ ให้ตรวจสอบ:

**Views:**
- [ ] ใช้ `<list>` แทน `<tree>`
- [ ] ใช้ `view_mode="list,form"` แทน `view_mode="tree,form"`
- [ ] ถ้าใช้ `<chatter/>` ต้อง inherit `mail.thread` ใน model
- [ ] ใช้ `id` แทน `active_id` ใน button context
- [ ] หลีกเลี่ยง `<group>` ใน search view
- [ ] Inline list ใน One2many ใช้ `<list editable="bottom">`

**Models:**
- [ ] ใช้ `models.Constraint()` แทน `_sql_constraints`
- [ ] แต่ละ constraint ต้องเป็น class attribute แยกกัน (เช่น `_code_uniq = models.Constraint(...)`)

---

## 7. Dependencies ที่ควรระวัง

ถ้าใช้ chatter ต้องเพิ่ม `mail` ใน depends:
```python
"depends": [
    "mail",  # Required for chatter
],
```

---

## อ้างอิง

- Odoo 19 Release Notes
- พบปัญหาจริงระหว่างพัฒนา module `itx_schedule_planning` (January 2026)
