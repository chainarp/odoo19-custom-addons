# ITX Schedule Planning - Data Model

## 1. Core Models (3-Level Structure)

### 1.1 itx.schedule.planning (Level 1 - Header)

ตารางงานหลัก - 1 record ต่อ 1 period

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | ชื่อ Planning เช่น "Schedule Mar 2026 - v1" |
| `period_id` | Many2one → period | Period ที่ใช้ |
| `date_start` | Date (related) | วันเริ่ม period |
| `date_end` | Date (related) | วันสิ้นสุด period |
| `state` | Selection | `draft` / `published` / `active` / `archived` |
| `version` | Integer | เลข version (สำหรับ clone) |
| `parent_id` | Many2one → self | Clone มาจาก version ไหน |
| `workrole_ids` | One2many → planning.workrole | Work roles ใน planning นี้ |
| **Tracking** | | |
| `published_date` | Datetime | วันที่ publish |
| `published_by` | Many2one → res.users | ใคร publish |
| `activated_date` | Datetime | วันที่ activate |
| `archived_date` | Datetime | วันที่ archive |
| **Computed** | | |
| `total_employees` | Integer | จำนวนพนักงานทั้งหมด |
| `total_entries` | Integer | จำนวน entries ทั้งหมด |
| `gap_count` | Integer | จำนวน gap ที่ตรวจพบ |

---

### 1.2 itx.schedule.planning.workrole (Level 2 - Per Workrole)

การตั้งค่าต่อ workrole - 1 planning มีหลาย workrole

| Field | Type | Description |
|-------|------|-------------|
| `planning_id` | Many2one → planning | อยู่ใน Planning ไหน |
| `workrole_id` | Many2one → workrole | กลุ่มงาน |
| `template_id` | Many2one → template | Template ที่ใช้ generate |
| `responsible_id` | Many2one → res.users | ผู้รับผิดชอบ workrole นี้ |
| `min_employees_per_shift` | Integer | จำนวนคนขั้นต่ำต่อกะ |
| `sequence` | Integer | ลำดับการแสดงผล |
| **Team Snapshots** | | |
| `team_snapshot_ids` | One2many → workrole.team | สถานะทีมเริ่มต้น/สิ้นสุด |
| **Entries** | | |
| `entry_ids` | One2many → workrole.entry | ตารางรายวันรายคน |

---

### 1.3 itx.schedule.planning.workrole.entry (Level 3 - Per Employee Per Day)

รายละเอียดตารางงานรายวันของแต่ละพนักงาน

| Field | Type | Description |
|-------|------|-------------|
| `planning_workrole_id` | Many2one → planning.workrole | อยู่ใน Workrole ไหน |
| `planning_id` | Many2one (related) | อยู่ใน Planning ไหน |
| `workrole_id` | Many2one (related) | Work role |
| `employee_id` | Many2one → hr.employee | พนักงาน |
| `employee_number` | Char (related) | รหัสพนักงาน |
| `date` | Date | วันที่ |
| **Shift Info** | | |
| `shift_type_id` | Many2one → shift.type | ประเภทกะ (เช้า/บ่าย/ดึก) |
| `hour_start` | Float | เข้างานกี่โมง (0-24) |
| `hour_end` | Float | เลิกงานกี่โมง |
| `duration` | Float (computed) | ชั่วโมงทำงาน |
| `is_day_off` | Boolean | เป็นวันหยุดตามกะ |
| `workteam_id` | Many2one → workteam | อยู่ทีมไหน |
| **Timeline Fields** | | |
| `date_start` | Datetime (computed) | วันเวลาเริ่ม (สำหรับ timeline) |
| `date_end` | Datetime (computed) | วันเวลาสิ้นสุด (สำหรับ timeline) |
| `color` | Integer (computed) | สี (สำหรับ timeline) |
| **Time-off** | | |
| `is_leave` | Boolean | มีการลาหรือไม่ |
| `leave_id` | Many2one → hr.leave | Link ไปใบลา |
| `leave_type` | Char (related) | ประเภทการลา |
| **Substitution** | | |
| `substitute_id` | Many2one → hr.employee | คนมาทำแทน |
| `is_substitute` | Boolean | เป็นคนทำแทนหรือไม่ |
| `original_employee_id` | Many2one → hr.employee | ทำแทนใคร |
| **Tracking** | | |
| `source` | Selection | `generated` / `manual` / `swapped` / `timeoff` |
| `note` | Text | หมายเหตุ |

**Records Calculation:**
```
จำนวน records = จำนวน Employee × จำนวนวันใน Period
ตัวอย่าง: 50 คน × 30 วัน = 1,500 records ต่อ 1 Workrole
```

---

### 1.4 itx.schedule.planning.workrole.team (Team Snapshot)

สถานะทีมเริ่มต้น/สิ้นสุด สำหรับการ generate ต่อเนื่อง

| Field | Type | Description |
|-------|------|-------------|
| `planning_workrole_id` | Many2one → planning.workrole | อยู่ใน Workrole ไหน |
| `workteam_id` | Many2one → workteam | ทีม |
| `initial_shift_type_id` | Many2one → shift.type | กะเริ่มต้น |
| `initial_day_in_pattern` | Integer | วันที่เท่าไหร่ใน pattern |
| `final_shift_type_id` | Many2one → shift.type | กะสิ้นสุด |
| `final_day_in_pattern` | Integer | วันที่สิ้นสุดใน pattern |

---

## 2. Master Data Models

### 2.1 itx.employee.workrole (Work Role)

กลุ่มงาน/ตำแหน่งงาน - พนักงานที่ทำงานเหมือนกัน แลกกะกันได้

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | ชื่อ เช่น "Operator", "Technician" |
| `code` | Char | รหัส เช่น "OPERATOR", "TECHNICIAN" |
| `description` | Text | รายละเอียด |
| `team_ids` | One2many → workteam | ทีมย่อยในกลุ่มงานนี้ |
| `employee_ids` | Many2many → hr.employee | พนักงานทั้งหมดใน role นี้ |
| `sequence` | Integer | ลำดับ |
| `color` | Integer | สี |
| `active` | Boolean | Active/Inactive |

---

### 2.2 itx.employee.workteam (Work Team)

ทีมย่อยภายในกลุ่มงาน - สำหรับหมุนเวียนกะ

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | ชื่อทีม เช่น "Team A", "Team B" |
| `code` | Char | รหัส เช่น "A", "B", "C", "D" |
| `workrole_id` | Many2one → workrole | อยู่ในกลุ่มงานไหน |
| `employee_ids` | Many2many → hr.employee | สมาชิกในทีม |
| `sequence` | Integer | ลำดับการหมุนเวียน |
| `color` | Integer | สีแสดงบน Timeline |
| `active` | Boolean | Active/Inactive |

---

### 2.3 itx.schedule.shift.type (Shift Type)

ประเภทกะ

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | ชื่อ เช่น "Morning Shift" |
| `code` | Char | รหัส เช่น "MORNING" |
| `hour_start` | Float | เวลาเริ่ม |
| `hour_end` | Float | เวลาสิ้นสุด |
| `duration` | Float (computed) | ชั่วโมงทำงาน |
| `is_overnight` | Boolean (computed) | ข้ามวันหรือไม่ |
| `is_day_off` | Boolean | เป็นวันหยุดหรือไม่ |
| `sequence` | Integer | ลำดับ |
| `color` | Integer | สี |
| `active` | Boolean | Active/Inactive |

**Seed Data:**

| Name | Code | Start | End | Day Off |
|------|------|-------|-----|---------|
| Morning Shift | MORNING | 06:00 | 14:00 | No |
| Afternoon Shift | AFTERNOON | 14:00 | 22:00 | No |
| Night Shift | NIGHT | 22:00 | 06:00 | No |
| Day Shift | DAY | 08:00 | 17:00 | No |
| Day Off | OFF | - | - | Yes |

---

### 2.4 itx.schedule.workoff.pattern (Work-Off Pattern)

รูปแบบวันทำงาน-วันหยุด

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | ชื่อ Pattern เช่น "4 On 2 Off" |
| `code` | Char | รหัส เช่น "4ON2OFF" |
| `pattern_type` | Selection | `consecutive` / `weekday` |
| `work_days` | Integer | จำนวนวันทำงานติดต่อกัน |
| `off_days` | Integer | จำนวนวันหยุดติดต่อกัน |
| `pattern_length` | Integer (computed) | ความยาว pattern |
| `weekday_mon` - `weekday_sun` | Boolean | วันทำงาน (สำหรับ weekday type) |
| `is_default` | Boolean | เป็น default pattern |
| `active` | Boolean | Active/Inactive |

**Seed Data:**

| Name | Code | Type | Work | Off |
|------|------|------|------|-----|
| 4 On 2 Off | 4ON2OFF | consecutive | 4 | 2 |
| 5 On 2 Off | 5ON2OFF | consecutive | 5 | 2 |
| 7 On 3 Off | 7ON3OFF | consecutive | 7 | 3 |
| Weekday (Mon-Fri) | WEEKDAY | weekday | 5 | 2 |

---

### 2.5 itx.schedule.planning.template (Planning Template)

Template รูปแบบการทำงาน

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | ชื่อ Template |
| `code` | Char | รหัส |
| `description` | Text | รายละเอียด |
| `is_default` | Boolean | เป็น default template |
| **Rotation** | | |
| `rotation_direction` | Selection | `none` / `forward` / `backward` |
| `rotation_period_count` | Integer | เปลี่ยนกะทุกกี่ period |
| `shifts_per_day` | Integer | จำนวนกะต่อวัน |
| **Pattern** | | |
| `pattern_id` | Many2one → pattern | Work-Off Pattern |
| **Duration** | | |
| `shift_duration` | Float | ชั่วโมงทำงานต่อกะ |
| `break_duration` | Float | ชั่วโมงพัก |
| `active` | Boolean | Active/Inactive |

**Seed Data:**

| Name | Code | Rotation | Pattern |
|------|------|----------|---------|
| 3 Shifts 4 Teams | 3S4T | forward | 4ON2OFF |
| 3 Shifts Fixed | 3SF | none | 4ON2OFF |
| Day Shift Only | DAY | none | WEEKDAY |

---

### 2.6 itx.schedule.period (Schedule Period)

กำหนดช่วงเวลา period

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | ชื่อ Period เช่น "January 2026" |
| `date_start` | Date | วันเริ่ม period |
| `date_end` | Date | วันสิ้นสุด period |
| `state` | Selection | `draft` / `active` / `closed` |
| `days_count` | Integer (computed) | จำนวนวัน |
| `planning_ids` | One2many → planning | Planning ใน period นี้ |
| `active` | Boolean | Active/Inactive |

---

## 3. Extended Models

### 3.1 hr.employee (Extension)

| Field | Type | Description |
|-------|------|-------------|
| `employee_number` | Char | รหัสพนักงาน (user-entered) |
| `workrole_id` | Many2one → workrole | กลุ่มงาน |
| `workteam_id` | Many2one → workteam | ทีม |

---

## 4. Model Relationships Diagram

```
                         ┌─────────────────────────┐
                         │  itx.employee.workrole  │
                         │       (กลุ่มงาน)          │
                         └────────────┬────────────┘
                                      │ one2many
                                      ▼
                         ┌─────────────────────────┐
                         │  itx.employee.workteam  │
                         │        (ทีม)             │
                         └────────────┬────────────┘
                                      │ many2many
                                      ▼
┌─────────────────────┐        ┌─────────────────┐
│ itx.schedule        │        │   hr.employee   │
│ .planning.template  │        │    (พนักงาน)     │
└──────────┬──────────┘        └────────┬────────┘
           │                            │
           │                            │
           └──────────┬─────────────────┘
                      ▼
┌─────────────────────────────────────────────────┐
│            itx.schedule.period                  │
│               (งวดตารางงาน)                       │
└───────────────────────┬─────────────────────────┘
                        │ one2many
                        ▼
┌─────────────────────────────────────────────────┐
│         itx.schedule.planning (Level 1)         │
│              (Header - ตารางงานหลัก)              │
└───────────────────────┬─────────────────────────┘
                        │ one2many
                        ▼
┌─────────────────────────────────────────────────┐
│     itx.schedule.planning.workrole (Level 2)    │
│          (Per Workrole - ตั้งค่าต่อกลุ่มงาน)       │
└───────────────────────┬─────────────────────────┘
                        │ one2many
                        ▼
┌─────────────────────────────────────────────────┐
│  itx.schedule.planning.workrole.entry (Level 3) │
│         (Per Employee Per Day - รายวันรายคน)     │
└─────────────────────────────────────────────────┘
```

---

## 5. Future Models (Not Yet Implemented)

### 5.1 itx.schedule.swap.request (Phase 2)

ใบขอแลกกะ - จะพัฒนาใน Phase 2

### 5.2 itx.schedule.constraint (Phase 3)

กฎเกณฑ์/ข้อจำกัด - จะพัฒนาใน Phase 3
