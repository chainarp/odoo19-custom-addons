# ITX Schedule Planning - Features Detail

## 1. Timeline View

### Display Elements

Timeline จะแสดงข้อมูลต่อไปนี้รวมกัน:

| Type | Color (Example) | Description |
|------|-----------------|-------------|
| Schedule - Draft | Yellow | ตารางที่ยัง generate อยู่ |
| Schedule - Published | Blue | ตารางที่ publish แล้ว |
| Schedule - Active | Green | ตารางที่ใช้งานอยู่ |
| กะเช้า | Light Blue | Morning shift (06:00-14:00) |
| กะบ่าย | Orange | Afternoon shift (14:00-22:00) |
| กะดึก | Purple | Night shift (22:00-06:00) |
| วันหยุดตามกะ | Gray | Day off (scheduled) |
| Time Off - ลาพักร้อน | Magenta | Annual leave |
| Time Off - ลาป่วย | Red | Sick leave |
| Gap Warning | Red Border | ช่วงที่คนไม่พอ |

### Grouping Options

- Group by Employee (default)
- Group by Department
- Group by Workrole
- Group by Workteam

### Timeline XML Example

```xml
<timeline
    date_start="date_start"
    date_stop="date_end"
    default_group_by="employee_id"
    colors="#f0ad4e:state=='draft';#5bc0de:state=='published';#5cb85c:state=='active'"
    event_open_popup="true"
>
    <field name="employee_id"/>
    <field name="shift_type_id"/>
    <field name="state"/>
    <field name="is_leave"/>
</timeline>
```

---

## 2. Schedule Generation

### Generation Wizard

```
┌─────────────────────────────────────────────────────────────────┐
│  Generate Schedule Planning                                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Period:     [2026-02-20] to [2026-03-19]                      │
│                                                                 │
│  Configs:                                                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Workrole        │ Template              │ Min/Shift     │   │
│  ├─────────────────┼───────────────────────┼───────────────┤   │
│  │ APM Driver      │ 3-Shift-4-Team        │ 2             │   │
│  │ APM Operator    │ 3-Shift-4-Team        │ 3             │   │
│  │ Maintenance     │ 3-Shift-4-Team        │ 1             │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Initial Values:  ○ From previous period                        │
│                   ● Manual setup                                │
│                                                                 │
│  Options:    ☑ Include approved time-off                        │
│              ☑ Check constraints after generate                 │
│              ☑ Show gap warnings                                │
│                                                                 │
│           [ Cancel ]                    [ Generate Draft ]      │
└─────────────────────────────────────────────────────────────────┘
```

### Generation Logic

1. **Load Config** - โหลด workrole + template mapping
2. **Load Employees** - โหลดพนักงานแต่ละ workrole/workteam
3. **Load Time-off** - โหลดใบลาที่ approved ล่วงหน้า
4. **Generate Lines** - สร้าง schedule line ตาม template pattern
5. **Apply Time-off** - mark วันที่ลาใน schedule
6. **Check Constraints** - ตรวจสอบ constraint violations
7. **Check Gaps** - ตรวจสอบช่วงที่คนไม่พอ
8. **Create Planning** - สร้าง Planning record (Draft)

### Initial Values from Previous Period

เมื่อเลือก "From previous period":
- ดึงค่ากะสุดท้ายของแต่ละทีม
- ดึงวันที่อยู่ใน work-off pattern
- ต่อเนื่องจากเดือนก่อนได้เลย

---

## 3. Constraint Engine

### Concept

HR สามารถจัดการ constraints ได้เอง โดยไม่ต้องแก้ code:
- **Add** - เพิ่ม constraint ใหม่
- **Remove** - ลบ constraint
- **Activate/Deactivate** - เปิด/ปิด constraint

### Constraint Types

| Type | Behavior |
|------|----------|
| `warning` | แจ้งเตือน แต่ไม่ block |
| `blocking` | แจ้งเตือน และ block การ approve |

### Default Constraints

```python
# REST_10H - พักขั้นต่ำ 10 ชม.ก่อนกะถัดไป
def check_rest_10h(self, line, prev_line):
    if not prev_line:
        return True
    rest_hours = (line.hour_start + 24) - prev_line.hour_end
    if rest_hours < 10:
        return False, f"พักเพียง {rest_hours} ชม. (ต้องพักอย่างน้อย 10 ชม.)"
    return True

# MAX_8H_DAY - ไม่เกิน 8 ชม./วัน
def check_max_8h_day(self, line):
    if line.duration > 8:
        return False, f"ทำงาน {line.duration} ชม. (เกิน 8 ชม./วัน)"
    return True

# MAX_48H_WEEK - ไม่เกิน 48 ชม./สัปดาห์
def check_max_48h_week(self, employee, week_start, week_end):
    total_hours = sum(line.duration for line in employee.schedule_line_ids
                      if week_start <= line.date <= week_end)
    if total_hours > 48:
        return False, f"รวม {total_hours} ชม./สัปดาห์ (เกิน 48 ชม.)"
    return True
```

### Constraint Validation UI

```
┌─────────────────────────────────────────────────────────────────┐
│  Constraint Violations                                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ⛔ BLOCKING (2)                                                │
│  ├── นายก: พักเพียง 8 ชม. ระหว่าง 21 ก.พ. - 22 ก.พ.              │
│  └── นายข: ทำงาน 52 ชม. ในสัปดาห์ 20-26 ก.พ.                     │
│                                                                 │
│  ⚠️ WARNING (3)                                                 │
│  ├── นายค: ทำงาน 9 ชม. วันที่ 23 ก.พ.                            │
│  ├── นายง: ทำงาน 8.5 ชม. วันที่ 25 ก.พ.                          │
│  └── นายจ: ไม่มีพักระหว่างวัน 27 ก.พ.                            │
│                                                                 │
│  ❌ Cannot publish: Please resolve blocking violations first    │
│                                                                 │
│           [ View Details ]              [ Close ]               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. Gap Management

### Gap Detection

ระบบตรวจสอบทุกช่วงเวลา 24 ชม. ว่ามีคนครบตาม `min_employees_per_shift` หรือไม่

### Gap Warning UI

```
┌─────────────────────────────────────────────────────────────────┐
│  Gap Warnings                                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ⚠️ Understaffed Shifts (5)                                    │
│                                                                 │
│  │ Date       │ Shift     │ Workrole    │ Required │ Actual │  │
│  ├────────────┼───────────┼─────────────┼──────────┼────────┤  │
│  │ 2026-02-23 │ กะเช้า     │ APM Driver  │ 2        │ 1      │  │
│  │ 2026-02-23 │ กะบ่าย     │ APM Driver  │ 2        │ 1      │  │
│  │ 2026-02-25 │ กะดึก     │ APM Operator│ 3        │ 2      │  │
│  │ 2026-02-28 │ กะเช้า     │ Maintenance │ 1        │ 0      │  │
│  │ 2026-03-01 │ กะบ่าย     │ APM Driver  │ 2        │ 1      │  │
│                                                                 │
│  Reason: Time-off approved for employees in these shifts        │
│                                                                 │
│  Action Required: Manager must assign substitute employees      │
│                                                                 │
│           [ Notify Manager ]            [ Close ]               │
└─────────────────────────────────────────────────────────────────┘
```

### Gap Alert (Evidence)

เมื่อพบ Gap จะส่ง notification พร้อมหลักฐาน:
- Email ถึง Manager + HR
- Odoo Inbox message
- Log ใน chatter ของ Planning record

---

## 5. Excel Import

### Format

| Column | Field | Required | Example |
|--------|-------|----------|---------|
| A | Employee Code/Name | Yes | EMP001 หรือ "นายก" |
| B | Date | Yes | 2026-02-20 |
| C | Shift Type | Yes | "MORNING" หรือ "กะเช้า" |
| D | Start Time | No | 06:00 |
| E | End Time | No | 14:00 |
| F | Note | No | หมายเหตุ |

### Sample Excel

```
| Employee | Date       | Shift     | Start | End   | Note     |
|----------|------------|-----------|-------|-------|----------|
| EMP001   | 2026-02-20 | MORNING   | 06:00 | 14:00 |          |
| EMP001   | 2026-02-21 | AFTERNOON | 14:00 | 22:00 |          |
| EMP002   | 2026-02-20 | NIGHT     | 22:00 | 06:00 |          |
| EMP002   | 2026-02-21 | DAY_OFF   |       |       | หยุดตามกะ |
```

### Import Wizard Features

- Download Template button
- Validate before import
- Show preview before confirm
- Error report for invalid rows
- Skip duplicates option
- Check constraints after import

---

## 6. Notifications

### Email Templates

#### 6.1 Schedule Published Notification

```
Subject: [ITX] Your Schedule for {period_name} is Published

Dear {employee_name},

Your work schedule for {period_name} has been published.

Period: {date_from} - {date_to}

Your Schedule Summary:
- Working Days: {work_days}
- Day Off: {off_days}
- Total Hours: {total_hours}

Please review your schedule and contact your supervisor if you have any questions.

[View My Schedule]

Best regards,
HR Team
```

#### 6.2 Gap Warning Notification

```
Subject: [ITX] Schedule Gap Alert - Action Required

Dear {manager_name},

A staffing gap has been detected in the schedule for {period_name}.

Gap Details:
{gap_list}

Please assign substitute employees to cover these shifts.

[View Schedule] [Assign Substitutes]

Best regards,
System
```

#### 6.3 Shift Swap Request

```
Subject: [ITX] Shift Swap Request from {requester_name}

Dear {partner_name},

{requester_name} has requested to swap shifts with you.

Your Shift:
- Date: {partner_shift_date}
- Time: {partner_shift_time}

Their Shift:
- Date: {requester_shift_date}
- Time: {requester_shift_time}

Reason: {reason}

Please confirm or reject this request:
[Confirm] [Reject]

Best regards,
HR Team
```

### Notification Evidence

ทุก notification จะถูก log เป็นหลักฐานใน:
- `mail.message` - ใน chatter ของ record
- `mail.mail` - email ที่ส่งออก
- `mail.activity` - สำหรับ pending actions

---

## 7. Reports (Future)

### Planned Reports

1. **Schedule Coverage Report**
   - แสดงจำนวนคนในแต่ละกะแต่ละวัน
   - เตือนถ้า understaffed

2. **Hours Summary Report**
   - สรุปชั่วโมงทำงานรายคน รายสัปดาห์/เดือน
   - เปรียบเทียบกับ contract hours

3. **Attendance vs Schedule Report**
   - เปรียบเทียบตารางที่วางแผน vs ลงเวลาจริง
   - สำหรับ payroll

4. **Swap Request Report**
   - สถิติการขอแลกกะ
   - อัตรา approve/reject

5. **Constraint Violation Report**
   - สรุป violations ที่เกิดขึ้น
   - แยกตาม constraint type

---

## 8. Time-off Integration

### Auto-Update Flow

1. พนักงานขอลาใน `hr_holidays`
2. Manager/HR approve ใบลา
3. ระบบตรวจสอบ Schedule Planning ที่ `published` หรือ `active`
4. ถ้ามี schedule ในวันที่ลา:
   - Mark `is_leave = True`
   - Link `leave_id`
   - Clear shift time (ถ้าลาเต็มวัน)
5. ตรวจสอบ Gap
6. ถ้าคนไม่พอ → แจ้ง Manager

### Leave Types Handling

| Leave Type | Schedule Impact |
|------------|-----------------|
| Annual Leave | ลบกะออก, mark as leave |
| Sick Leave (Planned) | ลบกะออก, mark as leave |
| Sick Leave (Emergency) | แก้ไข active schedule |
| Emergency Leave | แก้ไข active schedule |
| Half-day Leave | แก้ไข shift time |
