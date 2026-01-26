# ITX Schedule Planning - TODO & Open Items

## Status Legend

- **OPEN** - ยังไม่ได้คุย/ตัดสินใจ
- **IN PROGRESS** - กำลังคุย
- **DONE** - ตกลงแล้ว

---

## 1. Confirmed Items (ตกลงแล้ว)

### 1.1 Module & Naming

| Item | Value |
|------|-------|
| Module Name | `itx_schedule_planning` |
| Main Model | `itx.schedule.planning` |
| Line Model | `itx.schedule.planning.line` |
| Config Model | `itx.schedule.planning.config` |
| Template Model | `itx.schedule.planning.template` |
| Pattern Model | `itx.schedule.workoff.pattern` |
| Period Model | `itx.schedule.period` |
| Workrole Model | `itx.employee.workrole` |
| Workteam Model | `itx.employee.workteam` |
| Swap Request Model | `itx.schedule.swap.request` |
| Constraint Model | `itx.schedule.constraint` |

### 1.2 Business Context

| Item | Value |
|------|-------|
| Operation Type | 24/7 Operations |
| Target Groups | APM Operators, Infrastructure Controllers, Maintenance Crew |
| Legal Compliance | Thai Labor Law |

### 1.3 State Workflow

```
draft → published → active → archived
```

| State | Description |
|-------|-------------|
| `draft` | Generated, Manager แก้ไขได้ |
| `published` | พนักงานดูได้, Time-off system แก้ได้ |
| `active` | ใช้งานจริง, sync กับ Attendance |
| `archived` | จบ period (archive ได้ทันที) |

### 1.4 State Transitions

| Transition | Trigger | Who |
|------------|---------|-----|
| draft → published | Manual | Manager (หลัก), HR (ฉุกเฉิน) |
| published → active | Auto (วันแรก) หรือ Manual | System / Manager |
| active → archived | Manual (ทำได้ทันทีหลังจบ period) | Manager / HR |

### 1.5 Shift Swap Request

| Item | Value |
|------|-------|
| Available States | `published` + `active` |
| Workflow | Draft → Confirmed → Supervisor → HR → Done |
| Both parties acknowledge | Yes (required before Supervisor) |
| Cross-workrole swap | **ไม่อนุญาต** (ไม่มีความสามารถที่จะทำ) |

### 1.6 Constraint Engine

| Item | Value |
|------|-------|
| Constraint Manager | HR |
| Actions | Add / Remove / Activate / Deactivate |
| Types | `warning` (ไม่ block), `blocking` (block approve) |

### 1.7 Gap Management

| Item | Value |
|------|-------|
| Action | Alert only (ไม่ block) |
| Evidence | Message + Email log |
| Override | Manager สามารถ override ได้ ("คนใหญ่กว่าระบบ") |

### 1.8 Schedule Edit Rules

| State | Employee | Time-off System | Manager/HR |
|-------|----------|-----------------|------------|
| draft | ❌ | ❌ | ✅ |
| published | ❌ | ✅ (after approve) | ❌ |
| active | ❌ | ✅ (after approve) | Limited (จัดการ gap) |
| archived | ❌ | ❌ | ❌ |

### 1.9 Legal Constraints (Default)

| Constraint | Value | Type |
|------------|-------|------|
| Max hours/day | 8 ชม. | warning |
| Max hours/week | 48 ชม. | blocking |
| Min rest between shifts | 10 ชม. | blocking |
| Min break during work | 30-60 นาที | warning |

### 1.10 Template & Pattern Configuration (NEW)

| Item | Value |
|------|-------|
| Template `is_default` | มี - User เลือก default template ได้ |
| Work-Off Pattern | User สร้างเองได้หลาย pattern (ตาราง `itx.schedule.workoff.pattern`) |
| Rotation Direction | User เลือก forward/backward |
| `rotation_period_count` | เปลี่ยนกะทุกกี่ period (default: 1 = ทุก period) |

### 1.11 Period Configuration (NEW)

| Item | Value |
|------|-------|
| Period Model | `itx.schedule.period` - User กำหนด start/end date เอง |
| Default Start | วันที่ 26 ของเดือน |
| Default End | วันที่ 25 ของเดือนถัดไป |
| Archive | ทำได้ทันทีหลังจบ period (ไม่ต้องรอ) |

### 1.12 Payroll Integration (NEW)

| Item | Value |
|------|-------|
| Responsibility | **ไม่ใช่หน้าที่ของ module นี้** |
| Integration | Time Attendance system รับผิดชอบ sync กับ Payroll |

---

## 2. Open Items (ยังต้องคุย)

**ไม่มีแล้ว - Design เสร็จสมบูรณ์ 100%**

---

## 3. Development Phases (Suggested)

### Phase 1: Core (MVP)

- [ ] Basic models (planning, line, config, template, pattern, period)
- [ ] Master data models (workrole, workteam, shift.type)
- [ ] Generate wizard (basic)
- [ ] States (draft/published/active/archived)
- [ ] Security groups & rules
- [ ] Basic Timeline view

### Phase 2: Workflow & Swap

- [ ] Shift Swap Request model
- [ ] Swap approval workflow (same workrole only)
- [ ] Notifications (basic)

### Phase 3: Constraint Engine

- [ ] Constraint model
- [ ] Constraint validation logic
- [ ] Constraint management UI
- [ ] Default constraints

### Phase 4: Time-off Integration

- [ ] hr_holidays integration
- [ ] Auto-update schedule on leave approval
- [ ] Gap detection
- [ ] Gap notification

### Phase 5: Import/Export

- [ ] Excel import wizard
- [ ] Excel export
- [ ] Download template

### Phase 6: Reports & Polish

- [ ] Reports
- [ ] Dashboard
- [ ] UI improvements
- [ ] Performance optimization

---

## 4. Technical Decisions

### 4.1 Confirmed

| Decision | Choice | Reason |
|----------|--------|--------|
| Schedule storage | One record per employee per day | Simple, queryable |
| Constraint execution | Python code in model | Flexible, HR can add custom |
| Timeline view | web_timeline module | Standard Odoo approach |
| Notification | mail module | Built-in, with evidence |
| Cross-workrole swap | Not allowed | ไม่มีความสามารถที่จะทำ |
| Payroll integration | Not in scope | Time Attendance รับผิดชอบ |
| Period config | User-defined in itx.schedule.period | Flexible |
| Archive timing | Immediate after period end | No waiting needed |

### 4.2 To Decide (Minor)

| Decision | Options | Status |
|----------|---------|--------|
| Clone mechanism | Copy records vs. re-generate | OPEN (ไม่ urgent) |
| Version numbering | Auto-increment vs. manual | OPEN (ไม่ urgent) |

---

## 5. Next Steps

1. ~~**Confirm open items**~~ ✅ เสร็จแล้ว
2. **Review data model** - ตรวจสอบ models ใน 03_DATA_MODEL.md
3. **Start Phase 1** - เริ่ม coding MVP

---

## 6. Design Completion Summary

| Area | Status |
|------|--------|
| Module naming | ✅ 100% |
| Data models | ✅ 100% |
| State workflow | ✅ 100% |
| Security groups | ✅ 100% |
| Constraint engine | ✅ 100% |
| Gap management | ✅ 100% |
| Shift swap rules | ✅ 100% |
| Period configuration | ✅ 100% |
| Template/Pattern config | ✅ 100% |
| Payroll integration | ✅ 100% (out of scope) |

**Design Status: COMPLETE - พร้อมเริ่ม coding Phase 1**
