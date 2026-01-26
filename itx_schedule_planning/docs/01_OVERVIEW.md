# ITX Schedule Planning - Overview

## Module Information

| Item | Value |
|------|-------|
| **Module Name** | itx_schedule_planning |
| **Technical Name** | itx_schedule_planning |
| **Version** | 19.0.1.0.0 |
| **Category** | Human Resources |
| **License** | AGPL-3 |

## Business Context

ระบบบริหารจัดการกำลังคน (Workforce Management) สำหรับธุรกิจที่มีการทำงานแบบ **24/7 Operations** (ทำงานต่อเนื่องไม่มีวันหยุด)

### Target Employee Groups

| Group | Description |
|-------|-------------|
| **Remote APM Operators** | พนักงานควบคุมระบบขนส่งอัตโนมัติจากห้องควบคุม (Remote Control Room) |
| **Infrastructure Controllers** | เจ้าหน้าที่เฝ้าระวังและควบคุมระบบสาธารณูปโภค/โครงสร้างพื้นฐาน |
| **Maintenance Crew** | ทีมซ่อมบำรุงที่ต้องพร้อมจัดการเหตุฉุกเฉินและซ่อมบำรุงตามรอบ |

## Legal & Compliance Foundation

ระบบตั้งอยู่บนฐานกฎหมายคุ้มครองแรงงานไทย และมาตรฐานความปลอดภัยสากล:

| Rule | Requirement |
|------|-------------|
| **Normal Working Hours** | ไม่เกิน 8 ชม./วัน และไม่เกิน 48 ชม./สัปดาห์ |
| **Rest Period (Between Shifts)** | พักติดต่อกันไม่น้อยกว่า 10 ชั่วโมงก่อนเริ่มงานกะถัดไป |
| **Break During Work** | พักระหว่างวันอย่างน้อย 30-60 นาที |
| **Continuous Work** | งานที่หยุดไม่ได้ ทำงานวันหยุดได้ แต่ต้องจ่ายค่าตอบแทนตามกฎหมาย |

## Key Features

1. **Schedule Planning** - วางแผนตารางงานล่วงหน้า (รายเดือน)
2. **Auto Generation** - สร้างตารางอัตโนมัติจาก Template + Config
3. **State Workflow** - Draft → Published → Active → Archived
4. **Shift Swap Request** - พนักงานขอแลกกะได้ (ทั้ง Published & Active state)
5. **Time-off Integration** - ระบบลาแก้ไขตารางอัตโนมัติหลัง approve
6. **Constraint Engine** - กฎเกณฑ์ที่ HR add/remove/activate/deactivate ได้
7. **Gap Management** - แจ้งเตือนเมื่อคนไม่พอ (พร้อมหลักฐาน message/email)
8. **Timeline View** - แสดงผลแบบ Timeline
9. **Excel Import** - Upload ตารางจาก Excel
10. **Notifications** - แจ้งเตือนผ่าน Email + Odoo Inbox

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         MASTER DATA (ตั้งค่าครั้งเดียว)                    │
├─────────────────────────────────┬───────────────────────────────────────┤
│  itx.employee.workrole          │  itx.schedule.planning.template       │
│  (ใครทำงานอะไร)                   │  (ทำงานยังไง)                          │
└────────────────┬────────────────┴───────────────────┬───────────────────┘
                 │                                    │
                 │              1:1                   │
                 └──────────────┬─────────────────────┘
                                ▼
              ┌─────────────────────────────────────────┐
              │   itx.schedule.planning.config          │
              │   (จับคู่: workrole + template)          │
              └──────────────────┬──────────────────────┘
                                 │ Generate
                                 ▼
              ┌─────────────────────────────────────────┐
              │      itx.schedule.planning              │
              │      (ผลลัพธ์: ตารางงานรายคน)             │
              │      Records = Employee × Days          │
              └──────────────────┬──────────────────────┘
                                 │ Sync
                                 ▼
              ┌─────────────────────────────────────────┐
              │      Time Attendance System             │
              │      (ตรวจสอบเข้า-ออกงาน + Payroll)       │
              └─────────────────────────────────────────┘
```

## Dependencies

```python
"depends": [
    "hr",              # พนักงาน
    "resource",        # ปฏิทิน, Working Hours
    "hr_attendance",   # เชื่อม Check-in/Check-out
    "hr_contract",     # ชั่วโมงตามสัญญาจ้าง
    "hr_holidays",     # Time Off (ลาพักร้อน, ลาป่วย)
    "web_timeline",    # Timeline View
    "mail",            # Notifications
]
```

## Target Users

| Role | Responsibilities |
|------|------------------|
| **Employee** | ดูตารางตัวเอง/ทีม, ขอแลกกะ, acknowledge ใบลา |
| **Supervisor** | ดูตารางทีม, approve Swap Request ระดับแรก |
| **Manager** | Publish ตาราง, จัดการเมื่อคนไม่พอ, approve Swap |
| **HR** | จัดการทุกอย่าง, Constraint Manager, approve Swap ขั้นสุดท้าย |
| **Executive** | ดู Schedule Planning ทั้งบริษัท (Read-only) |

## Reference

- Migrated and redesigned from: `resource_schedule` (Odoo 14, TREVI Software)
- Inspired by: Odoo Enterprise Planning module
