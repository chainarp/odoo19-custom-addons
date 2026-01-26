# ITX Schedule Planning - Workflow

## 1. Main Workflow: Schedule Planning

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       SCHEDULE PLANNING WORKFLOW                            │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌──────────┐      ┌───────────┐      ┌────────┐      ┌──────────┐
  │  DRAFT   │ ───▶ │ PUBLISHED │ ───▶ │ ACTIVE │ ───▶ │ ARCHIVED │
  │(Generated)│     │(Emp Review)│     │(Running)│     │(History) │
  └──────────┘      └───────────┘      └────────┘      └──────────┘
       │                  │                 │
       │   Manager/HR     │   Auto/Manual   │   หลังจบ period
       │   publish        │   วันแรก period  │   (ทำได้ทันที)
       │                  │                 │
       │                  ▼                 ▼
       │            ┌─────────────────────────────┐
       │            │    Shift Swap Request       │
       │            │    (ขอได้ทั้ง 2 states)       │
       │            └─────────────────────────────┘
       │                        │
       ▼                        ▼
  ┌───────────────────────────────────────────────────┐
  │  Time-off System Integration                      │
  │  (Approved leave → Auto update schedule)          │
  │  → ถ้าคนไม่พอ → Manager จัดการ                     │
  └───────────────────────────────────────────────────┘
```

### State Descriptions

| State | Description | Who Can Change | Editable? |
|-------|-------------|----------------|-----------|
| **Draft** | ระบบ Generate ตารางจาก Config + Template | System (auto) | Yes - Manager/HR |
| **Published** | Manager publish ให้พนักงานดูและตรวจสอบ | Manager (หลัก), HR (ฉุกเฉิน) | Limited - Time-off system only |
| **Active** | ตารางที่ใช้งานจริง sync กับ Attendance | Auto (วันแรก) หรือ Manual | Limited - Time-off system only |
| **Archived** | จบ period (archive ได้ทันที) | Manual | No - Read only |

### Workflow Steps

1. **Prepare Master Data**
   - ตั้งค่า `itx.employee.workrole` (กลุ่มงาน: APM Driver, Operator, Maintenance)
   - ตั้งค่า `itx.employee.workteam` (ทีม: A, B, C, D)
   - ตั้งค่า `itx.schedule.planning.template` (รูปแบบกะ, rotation pattern)

2. **Create Config**
   - สร้าง `itx.schedule.planning.config` จับคู่ workrole + template
   - กำหนด initial values (วันเริ่ม, ค่าจากเดือนก่อน)

3. **Generate Draft**
   - ระบบ generate `itx.schedule.planning` (Draft)
   - แสดง Time-off ที่ขอล่วงหน้า (ลาพักร้อน, หมอนัด)
   - แสดง Gap Warning ถ้าคนไม่พอ

4. **Manager Review & Publish**
   - Manager ตรวจสอบและแก้ไข (ถ้าจำเป็น)
   - Publish ให้พนักงานดู
   - พนักงานตรวจสอบตารางตัวเอง

5. **Activate**
   - Auto activate วันแรกของ period
   - หรือ Manager activate manual
   - Sync กับ Time Attendance System

6. **During Active Period**
   - Time-off system แก้ไขตารางอัตโนมัติ (หลัง approve ลา)
   - Shift Swap Request ยังทำได้
   - Manager จัดการเมื่อคนไม่พอ

7. **Archive**
   - ทำได้ทันทีหลังจบ period (ไม่ต้องรอ)
   - เก็บเป็นประวัติ (Read-only)
   - Payroll integration เป็นหน้าที่ของ Time Attendance system

---

## 2. Shift Swap Request Workflow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SHIFT SWAP REQUEST WORKFLOW                          │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌──────────┐     ┌───────────┐     ┌────────────┐     ┌────────────┐
  │  DRAFT   │ ──▶ │ CONFIRMED │ ──▶ │ SUPERVISOR │ ──▶ │    HR      │
  │ (Emp A)  │     │ (Emp B)   │     │  APPROVED  │     │  APPROVED  │
  └──────────┘     └───────────┘     └────────────┘     └────────────┘
       │                                                       │
       │                                                       ▼
       │                                               ┌─────────────┐
       │                                               │    DONE     │
       │                                               │ (Auto Swap) │
       │                                               └─────────────┘
       │
       │                ┌──────────┐
       └──────────────▶ │ REJECTED │ ◀────────────────────────
                        └──────────┘
```

### Swap Request States

| State | Description | Action By |
|-------|-------------|-----------|
| **Draft** | พนักงาน A สร้าง Request ขอแลกกะกับพนักงาน B | Employee A |
| **Confirmed** | พนักงาน B acknowledge และยอมรับการแลก | Employee B |
| **Supervisor Approved** | หัวหน้าทีมอนุมัติ | Supervisor |
| **HR Approved** | HR อนุมัติ (ตรวจสอบกฎหมายแรงงาน) | HR |
| **Done** | ระบบสลับกะให้อัตโนมัติ | System |
| **Rejected** | ถูกปฏิเสธ (โดย Emp B, Supervisor, หรือ HR) | Any approver |

### Swap Request Rules

- ขอแลกกะได้ทั้ง **Published** และ **Active** state
- ทั้งสองฝ่ายต้อง **acknowledge** ก่อน route ไป Supervisor
- HR เป็นผู้ approve ขั้นสุดท้าย (ตรวจสอบ constraint เช่น OT เกินกำหนด)
- **Cross-workrole swap: ไม่อนุญาต** - แลกได้เฉพาะ workrole เดียวกันเท่านั้น

### Why HR Must Approve?

- ตรวจสอบว่าการแลกกะไม่ทำให้พนักงานทำงานเกินกฎหมายกำหนด
- ตรวจสอบ constraint ต่างๆ ที่ HR กำหนด
- เช่น พนักงาน A หรือ B ทำงานเกิน 48 ชม./สัปดาห์
- เช่น พักไม่ถึง 10 ชม. ก่อนกะถัดไป

---

## 3. Time-off Integration Workflow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        TIME-OFF INTEGRATION                                 │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌──────────────┐      ┌──────────────┐      ┌──────────────────────┐
  │ Employee     │ ───▶ │ hr_holidays  │ ───▶ │ Schedule Planning    │
  │ Request Leave│      │ (Approve)    │      │ (Auto Update)        │
  └──────────────┘      └──────────────┘      └──────────────────────┘
                                                       │
                                                       ▼
                                              ┌──────────────────────┐
                                              │ Gap Detection        │
                                              │ (คนไม่พอ?)            │
                                              └──────────────────────┘
                                                       │
                                          ┌────────────┴────────────┐
                                          ▼                         ▼
                                   ┌─────────────┐          ┌─────────────┐
                                   │ คนพอ        │          │ คนไม่พอ      │
                                   │ (OK)        │          │ (Alert Mgr) │
                                   └─────────────┘          └─────────────┘
```

### Time-off Types Handled

| Type | Example | Impact |
|------|---------|--------|
| **ลาพักร้อน (Annual Leave)** | ขอล่วงหน้า | แสดงใน Draft, ลบกะออก |
| **ลาป่วยล่วงหน้า (Sick Leave - Planned)** | หมอนัด | แสดงใน Draft, ลบกะออก |
| **ลาป่วยกะทันหัน (Sick Leave - Emergency)** | ป่วยกะทันหัน | แก้ไข Active schedule |
| **ลากิจฉุกเฉิน (Emergency Leave)** | ญาติผู้ใหญ่เสีย | แก้ไข Active schedule |

### Auto Update Rules

1. เมื่อ Time-off ถูก **Approve** ใน hr_holidays
2. ระบบตรวจสอบว่ามี Schedule Planning ที่ **Published** หรือ **Active**
3. ลบ/แก้ไข schedule line ของพนักงานในวันที่ลา
4. ตรวจสอบ Gap → ถ้าคนไม่พอ → แจ้ง Manager

---

## 4. Period Configuration

### Planning Period

```
Default: วันที่ 26 ของเดือน → วันที่ 25 ของเดือนถัดไป

ตัวอย่าง: Planning Period เดือนมีนาคม 2026
         เริ่ม:     26 กุมภาพันธ์ 2026
         สิ้นสุด:   25 มีนาคม 2026
```

### Period Model (itx.schedule.period)

User กำหนด period เองได้ในตาราง `itx.schedule.period`:
- `date_start` - วันเริ่ม period
- `date_end` - วันสิ้นสุด period

### Configurable Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `default_period_start_day` | 26 | วันเริ่มต้น period default |
| `auto_activate` | True | Auto activate วันแรกของ period |

**Note:** Archive ทำได้ทันทีหลังจบ period (ไม่ต้องรอ)

---

## 5. Notification Events

| Event | Recipients | Channels | Evidence |
|-------|------------|----------|----------|
| Schedule Published | พนักงานทุกคนใน period | Email + Odoo Inbox | Message log |
| Schedule Activated | พนักงานทุกคนใน period | Odoo Inbox | Message log |
| Gap Warning | Manager + HR | Email + Odoo Inbox | Message log |
| Swap Request Created | พนักงาน B (คู่แลก) | Email + Odoo Inbox | Activity |
| Swap Request Status | ผู้เกี่ยวข้อง | Email + Odoo Inbox | Message log |
| Time-off Approved | Manager (ถ้าคนไม่พอ) | Email + Odoo Inbox | Message log |
| Constraint Violation | Manager + HR | Email + Odoo Inbox | Message log |
