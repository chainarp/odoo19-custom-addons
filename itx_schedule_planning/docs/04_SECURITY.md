# ITX Schedule Planning - Security & Access Rights

## 1. Security Groups

### Group Hierarchy

```
                    ┌────────────────────────┐
                    │  base.group_user       │
                    │  (All Employees)       │
                    └───────────┬────────────┘
                                │
            ┌───────────────────┼───────────────────┐
            ▼                   ▼                   ▼
┌───────────────────┐ ┌─────────────────┐ ┌─────────────────────┐
│ Schedule User     │ │Schedule Executive│ │ Schedule Supervisor │
│ (พนักงาน)          │ │ (ผู้บริหาร)       │ │ (หัวหน้าทีม)         │
└───────────────────┘ └─────────────────┘ └──────────┬──────────┘
                                                     │
                                          ┌──────────┴──────────┐
                                          ▼                     ▼
                               ┌─────────────────┐   ┌─────────────────┐
                               │Schedule Manager │   │ Constraint      │
                               │     (Manager)   │   │ Manager (HR)    │
                               └─────────────────┘   └─────────────────┘
```

---

## 2. Group Definitions

### 2.1 Schedule User (พนักงาน)

**XML ID:** `itx_schedule_planning.group_schedule_user`

**Permissions:**

| Model | Create | Read | Write | Delete |
|-------|--------|------|-------|--------|
| itx.schedule.planning | ❌ | ✅ (own + team) | ❌ | ❌ |
| itx.schedule.planning.line | ❌ | ✅ (own + team) | ❌ | ❌ |
| itx.schedule.planning.template | ❌ | ✅ | ❌ | ❌ |
| itx.employee.workrole | ❌ | ✅ | ❌ | ❌ |
| itx.employee.workteam | ❌ | ✅ | ❌ | ❌ |
| itx.schedule.swap.request | ✅ (own) | ✅ (own) | ✅ (own, draft only) | ❌ |

**Capabilities:**
- ดูตารางงานของตัวเอง
- ดูตารางงานของทีม/workrole เดียวกัน
- สร้าง Shift Swap Request
- Acknowledge รับแลกกะ (เมื่อถูกเลือกเป็นคู่แลก)

---

### 2.2 Schedule Executive (ผู้บริหาร)

**XML ID:** `itx_schedule_planning.group_schedule_executive`

**Permissions:**

| Model | Create | Read | Write | Delete |
|-------|--------|------|-------|--------|
| itx.schedule.planning | ❌ | ✅ (all) | ❌ | ❌ |
| itx.schedule.planning.line | ❌ | ✅ (all) | ❌ | ❌ |
| itx.schedule.planning.template | ❌ | ✅ | ❌ | ❌ |
| itx.employee.workrole | ❌ | ✅ | ❌ | ❌ |
| itx.employee.workteam | ❌ | ✅ | ❌ | ❌ |
| itx.schedule.swap.request | ❌ | ✅ (all) | ❌ | ❌ |
| itx.schedule.constraint | ❌ | ✅ | ❌ | ❌ |

**Capabilities:**
- ดู Schedule Planning ทั้งบริษัท (Read-only)
- ดู Reports และ Dashboard
- ไม่สามารถแก้ไขข้อมูลใดๆ

---

### 2.3 Schedule Supervisor (หัวหน้าทีม)

**XML ID:** `itx_schedule_planning.group_schedule_supervisor`

**Permissions:**

| Model | Create | Read | Write | Delete |
|-------|--------|------|-------|--------|
| itx.schedule.planning | ❌ | ✅ (team) | ❌ | ❌ |
| itx.schedule.planning.line | ❌ | ✅ (team) | ❌ | ❌ |
| itx.schedule.planning.template | ❌ | ✅ | ❌ | ❌ |
| itx.employee.workrole | ❌ | ✅ | ❌ | ❌ |
| itx.employee.workteam | ❌ | ✅ | ❌ | ❌ |
| itx.schedule.swap.request | ❌ | ✅ (team) | ✅ (approve) | ❌ |

**Capabilities:**
- ดูตารางงานของทีมตัวเอง
- Approve Shift Swap Request ระดับ Supervisor
- ไม่สามารถสร้างหรือแก้ไขตาราง

---

### 2.4 Schedule Manager

**XML ID:** `itx_schedule_planning.group_schedule_manager`

**Permissions:**

| Model | Create | Read | Write | Delete |
|-------|--------|------|-------|--------|
| itx.schedule.planning | ✅ | ✅ | ✅ | ✅ |
| itx.schedule.planning.line | ✅ | ✅ | ✅ | ✅ |
| itx.schedule.planning.config | ✅ | ✅ | ✅ | ✅ |
| itx.schedule.planning.template | ✅ | ✅ | ✅ | ✅ |
| itx.employee.workrole | ✅ | ✅ | ✅ | ✅ |
| itx.employee.workteam | ✅ | ✅ | ✅ | ✅ |
| itx.schedule.swap.request | ✅ | ✅ | ✅ | ✅ |
| itx.schedule.shift.type | ✅ | ✅ | ✅ | ✅ |

**Capabilities:**
- Generate Schedule Planning
- Publish Schedule (หลัก)
- Activate/Archive Schedule
- จัดการเมื่อคนไม่พอ
- Approve Shift Swap Request ระดับ Manager
- จัดการ Templates, Workroles, Workteams
- Upload Excel

---

### 2.5 Constraint Manager (HR)

**XML ID:** `itx_schedule_planning.group_constraint_manager`

**Inherits:** Schedule Manager

**Additional Permissions:**

| Model | Create | Read | Write | Delete |
|-------|--------|------|-------|--------|
| itx.schedule.constraint | ✅ | ✅ | ✅ | ✅ |
| itx.schedule.config.settings | ✅ | ✅ | ✅ | ✅ |

**Capabilities:**
- ทำได้ทุกอย่างเหมือน Schedule Manager
- จัดการ Constraints (Add/Remove/Activate/Deactivate)
- จัดการ System Settings
- Approve Shift Swap Request ขั้นสุดท้าย (HR level)
- Publish Schedule (กรณีฉุกเฉิน)

---

## 3. Record Rules

### 3.1 Schedule Planning - User Rule

```xml
<record id="planning_user_rule" model="ir.rule">
    <field name="name">Schedule Planning: User sees own team</field>
    <field name="model_id" ref="model_itx_schedule_planning"/>
    <field name="groups" eval="[(4, ref('group_schedule_user'))]"/>
    <field name="domain_force">
        [('line_ids.employee_id.workrole_id', '=', user.employee_id.workrole_id.id)]
    </field>
</record>
```

### 3.2 Schedule Line - User Rule

```xml
<record id="planning_line_user_rule" model="ir.rule">
    <field name="name">Schedule Line: User sees own and team</field>
    <field name="model_id" ref="model_itx_schedule_planning_line"/>
    <field name="groups" eval="[(4, ref('group_schedule_user'))]"/>
    <field name="domain_force">
        ['|',
            ('employee_id.user_id', '=', user.id),
            ('employee_id.workrole_id', '=', user.employee_id.workrole_id.id)
        ]
    </field>
</record>
```

### 3.3 Schedule Line - Supervisor Rule

```xml
<record id="planning_line_supervisor_rule" model="ir.rule">
    <field name="name">Schedule Line: Supervisor sees team</field>
    <field name="model_id" ref="model_itx_schedule_planning_line"/>
    <field name="groups" eval="[(4, ref('group_schedule_supervisor'))]"/>
    <field name="domain_force">
        [('employee_id.department_id', 'child_of', user.employee_id.department_id.id)]
    </field>
</record>
```

### 3.4 Swap Request - User Rule

```xml
<record id="swap_request_user_rule" model="ir.rule">
    <field name="name">Swap Request: User sees own requests</field>
    <field name="model_id" ref="model_itx_schedule_swap_request"/>
    <field name="groups" eval="[(4, ref('group_schedule_user'))]"/>
    <field name="domain_force">
        ['|',
            ('requester_id.user_id', '=', user.id),
            ('partner_id.user_id', '=', user.id)
        ]
    </field>
</record>
```

### 3.5 Swap Request - Supervisor Rule

```xml
<record id="swap_request_supervisor_rule" model="ir.rule">
    <field name="name">Swap Request: Supervisor sees team requests</field>
    <field name="model_id" ref="model_itx_schedule_swap_request"/>
    <field name="groups" eval="[(4, ref('group_schedule_supervisor'))]"/>
    <field name="domain_force">
        ['|',
            ('requester_id.department_id', 'child_of', user.employee_id.department_id.id),
            ('partner_id.department_id', 'child_of', user.employee_id.department_id.id)
        ]
    </field>
</record>
```

---

## 4. Menu Access

| Menu | User | Executive | Supervisor | Manager | HR |
|------|------|-----------|------------|---------|-----|
| My Schedule | ✅ | ❌ | ✅ | ✅ | ✅ |
| Team Schedule | ✅ | ❌ | ✅ | ✅ | ✅ |
| All Schedules | ❌ | ✅ | ❌ | ✅ | ✅ |
| My Swap Requests | ✅ | ❌ | ✅ | ✅ | ✅ |
| Team Swap Requests | ❌ | ❌ | ✅ | ✅ | ✅ |
| All Swap Requests | ❌ | ❌ | ❌ | ✅ | ✅ |
| Templates | ❌ | ❌ | ❌ | ✅ | ✅ |
| Workroles | ❌ | ❌ | ❌ | ✅ | ✅ |
| Workteams | ❌ | ❌ | ❌ | ✅ | ✅ |
| Constraints | ❌ | ❌ | ❌ | ❌ | ✅ |
| Settings | ❌ | ❌ | ❌ | ❌ | ✅ |
| Reports | ❌ | ✅ | ✅ | ✅ | ✅ |
| Dashboard | ❌ | ✅ | ✅ | ✅ | ✅ |

---

## 5. Action Permissions

### 5.1 Schedule Planning Actions

| Action | User | Executive | Supervisor | Manager | HR |
|--------|------|-----------|------------|---------|-----|
| View Schedule | ✅ (own/team) | ✅ (all) | ✅ (team) | ✅ | ✅ |
| Generate Draft | ❌ | ❌ | ❌ | ✅ | ✅ |
| Publish | ❌ | ❌ | ❌ | ✅ (หลัก) | ✅ (ฉุกเฉิน) |
| Activate | ❌ | ❌ | ❌ | ✅ | ✅ |
| Archive | ❌ | ❌ | ❌ | ✅ | ✅ |
| Clone | ❌ | ❌ | ❌ | ✅ | ✅ |

### 5.2 Swap Request Actions

| Action | User | Executive | Supervisor | Manager | HR |
|--------|------|-----------|------------|---------|-----|
| Create Request | ✅ | ❌ | ✅ | ✅ | ✅ |
| Acknowledge (Partner) | ✅ | ❌ | ✅ | ✅ | ✅ |
| Approve (Supervisor) | ❌ | ❌ | ✅ | ✅ | ✅ |
| Approve (HR Final) | ❌ | ❌ | ❌ | ❌ | ✅ |
| Reject | ❌ | ❌ | ✅ | ✅ | ✅ |

### 5.3 Constraint Actions

| Action | User | Executive | Supervisor | Manager | HR |
|--------|------|-----------|------------|---------|-----|
| View Constraints | ❌ | ✅ | ❌ | ❌ | ✅ |
| Add Constraint | ❌ | ❌ | ❌ | ❌ | ✅ |
| Remove Constraint | ❌ | ❌ | ❌ | ❌ | ✅ |
| Activate/Deactivate | ❌ | ❌ | ❌ | ❌ | ✅ |
