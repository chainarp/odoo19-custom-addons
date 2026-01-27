# ITX Schedule Planning - TODO & Open Items

## Status Legend

- **OPEN** - ยังไม่ได้คุย/ตัดสินใจ
- **IN PROGRESS** - กำลังคุย
- **DONE** - ตกลงแล้ว

---

## 1. Confirmed Items (ตกลงแล้ว)

### 1.1 Module & Naming

| Item | Value | Status |
|------|-------|--------|
| Module Name | `itx_schedule_planning` | ✅ Implemented |
| Main Model (L1) | `itx.schedule.planning` | ✅ Implemented |
| Workrole Model (L2) | `itx.schedule.planning.workrole` | ✅ Implemented |
| Entry Model (L3) | `itx.schedule.planning.workrole.entry` | ✅ Implemented |
| Team Snapshot Model | `itx.schedule.planning.workrole.team` | ✅ Implemented |
| Template Model | `itx.schedule.planning.template` | ✅ Implemented |
| Pattern Model | `itx.schedule.workoff.pattern` | ✅ Implemented |
| Period Model | `itx.schedule.period` | ✅ Implemented |
| Shift Type Model | `itx.schedule.shift.type` | ✅ Implemented |
| Workrole Model | `itx.employee.workrole` | ✅ Implemented |
| Workteam Model | `itx.employee.workteam` | ✅ Implemented |
| Swap Request Model | `itx.schedule.swap.request` | 🔲 Phase 2 |
| Constraint Model | `itx.schedule.constraint` | 🔲 Phase 3 |

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

---

## 2. Development Phases

### Phase 1: Core (MVP) - IN PROGRESS

| Task | Status |
|------|--------|
| Master data models (workrole, workteam, shift.type) | ✅ Done |
| Work-off pattern model | ✅ Done |
| Planning template model | ✅ Done |
| Schedule period model | ✅ Done |
| 3-level planning structure (planning → workrole → entry) | ✅ Done |
| hr.employee extension (workrole_id, workteam_id, employee_number) | ✅ Done |
| CSV seed data for master data | ✅ Done |
| Timeline view (web_timeline integration) | ✅ Done |
| Demo/test data for timeline | 🔄 Testing |
| Generate wizard (basic) | 🔲 TODO |
| States (draft/published/active/archived) | ✅ Done (model only) |
| Security groups & rules | 🔲 TODO |

### Phase 2: Workflow & Swap

| Task | Status |
|------|--------|
| Shift Swap Request model | 🔲 TODO |
| Swap approval workflow (same workrole only) | 🔲 TODO |
| Notifications (basic) | 🔲 TODO |

### Phase 3: Constraint Engine

| Task | Status |
|------|--------|
| Constraint model | 🔲 TODO |
| Constraint validation logic | 🔲 TODO |
| Constraint management UI | 🔲 TODO |
| Default constraints | 🔲 TODO |

### Phase 4: Time-off Integration

| Task | Status |
|------|--------|
| hr_holidays integration | 🔲 TODO |
| Auto-update schedule on leave approval | 🔲 TODO |
| Gap detection | 🔲 TODO |
| Gap notification | 🔲 TODO |

### Phase 5: Import/Export

| Task | Status |
|------|--------|
| Excel import wizard | 🔲 TODO |
| Excel export | 🔲 TODO |
| Download template | 🔲 TODO |

### Phase 6: Reports & Polish

| Task | Status |
|------|--------|
| Reports | 🔲 TODO |
| Dashboard | 🔲 TODO |
| UI improvements | 🔲 TODO |
| Performance optimization | 🔲 TODO |

---

## 3. Technical Decisions

### 3.1 Confirmed

| Decision | Choice | Reason |
|----------|--------|--------|
| Data structure | 3-level hierarchy | Flexible per-workrole config |
| Schedule storage | One record per employee per day | Simple, queryable |
| Timeline view | web_timeline module | Standard OCA approach |
| Notification | mail module | Built-in, with evidence |
| Cross-workrole swap | Not allowed | ไม่มีความสามารถที่จะทำ |
| Payroll integration | Not in scope | Time Attendance รับผิดชอบ |
| Period config | User-defined in itx.schedule.period | Flexible |
| Archive timing | Immediate after period end | No waiting needed |

### 3.2 To Decide (Minor)

| Decision | Options | Status |
|----------|---------|--------|
| Clone mechanism | Copy records vs. re-generate | OPEN (ไม่ urgent) |
| Version numbering | Auto-increment vs. manual | OPEN (ไม่ urgent) |

---

## 4. Current Sprint Tasks

### Immediate (Today)
1. ✅ Fix demo data error (remove `code` field from period)
2. 🔄 Test timeline view with demo data
3. 🔲 Adjust timeline view if needed

### Next
1. Generate Schedule wizard
2. Basic validation
3. Security groups

---

## 5. Files Created/Modified

### Models (10 files)
- `models/employee_workrole.py` ✅
- `models/employee_workteam.py` ✅
- `models/shift_type.py` ✅
- `models/workoff_pattern.py` ✅
- `models/planning_template.py` ✅
- `models/schedule_period.py` ✅
- `models/schedule_planning.py` ✅
- `models/schedule_planning_workrole.py` ✅
- `models/schedule_planning_workrole_entry.py` ✅
- `models/hr_employee.py` ✅

### Views (11 files)
- `views/workrole_views.xml` ✅
- `views/workteam_views.xml` ✅
- `views/shift_type_views.xml` ✅
- `views/workoff_pattern_views.xml` ✅
- `views/planning_template_views.xml` ✅
- `views/period_views.xml` ✅
- `views/schedule_planning_views.xml` ✅
- `views/schedule_planning_workrole_views.xml` ✅
- `views/schedule_planning_workrole_entry_views.xml` ✅ (includes timeline)
- `views/hr_employee_views.xml` ✅
- `views/menuitems.xml` ✅

### Data (6 files)
- `data/itx.schedule.shift.type.csv` ✅
- `data/itx.schedule.workoff.pattern.csv` ✅
- `data/itx.schedule.planning.template.csv` ✅
- `data/itx.employee.workrole.csv` ✅
- `data/itx.employee.workteam.csv` ✅
- `data/demo_data.xml` ✅

### Security (1 file)
- `security/ir.model.access.csv` ✅

### Documentation (7 files)
- `docs/01_OVERVIEW.md` ✅
- `docs/02_WORKFLOW.md` ✅
- `docs/03_DATA_MODEL.md` ✅ (updated)
- `docs/04_SECURITY.md` ✅
- `docs/05_FEATURES.md` ✅
- `docs/06_TODO_OPEN_ITEMS.md` ✅ (updated)
- `docs/07_ODOO19_GUIDELINES.md` ✅

---

## 6. Design Completion Summary

| Area | Status |
|------|--------|
| Module naming | ✅ 100% |
| Data models | ✅ 100% |
| State workflow | ✅ 100% |
| Security groups | 🔲 TODO |
| Constraint engine | 🔲 Phase 3 |
| Gap management | 🔲 Phase 4 |
| Shift swap rules | 🔲 Phase 2 |
| Period configuration | ✅ 100% |
| Template/Pattern config | ✅ 100% |
| Timeline view | ✅ 100% |

**Overall Phase 1 Progress: ~70%**
