# ITX Schedule Planning - Data Model

## 1. Core Models

### 1.1 itx.schedule.planning (Main Output)

ตารางงานหลัก - ผลลัพธ์สุดท้ายที่ generate ออกมา

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | ชื่อ Planning เช่น "Schedule Mar 2026 - v1" |
| `date_start` | Date | วันเริ่ม period |
| `date_end` | Date | วันสิ้นสุด period |
| `state` | Selection | `draft` / `published` / `active` / `archived` |
| `version` | Integer | เลข version (สำหรับ clone) |
| `parent_id` | Many2one → self | Clone มาจาก version ไหน |
| `config_ids` | One2many → config | Configs ที่ใช้ generate |
| `line_ids` | One2many → line | รายละเอียดกะรายคน รายวัน |
| `published_date` | Datetime | วันที่ publish |
| `published_by` | Many2one → res.users | ใคร publish |
| `activated_date` | Datetime | วันที่ activate |
| `archived_date` | Datetime | วันที่ archive |
| **Computed** | | |
| `total_employees` | Integer | จำนวนพนักงานทั้งหมด |
| `total_lines` | Integer | จำนวน records ทั้งหมด |
| `gap_count` | Integer | จำนวน gap ที่ตรวจพบ |

**Records Calculation:**
```
จำนวน records = จำนวน Employee × จำนวนวันใน Period
ตัวอย่าง: 50 คน × 30 วัน = 1,500 records ต่อ 1 Planning
```

---

### 1.2 itx.schedule.planning.line (Daily Schedule per Employee)

รายละเอียดตารางงานรายวันของแต่ละพนักงาน

| Field | Type | Description |
|-------|------|-------------|
| `planning_id` | Many2one → planning | อยู่ใน Planning ไหน |
| `employee_id` | Many2one → hr.employee | พนักงาน |
| `date` | Date | วันที่ |
| `hour_start` | Float | เข้างานกี่โมง (0-24) เช่น 6.0 = 06:00 |
| `hour_end` | Float | เลิกงานกี่โมง เช่น 14.0 = 14:00 |
| `duration` | Float (computed) | ชั่วโมงทำงาน (ไม่รวมพัก) |
| `is_day_off` | Boolean | เป็นวันหยุดตามกะหรือไม่ |
| `shift_type_id` | Many2one → shift.type | ประเภทกะ (เช้า/บ่าย/ดึก) |
| `workrole_id` | Many2one → workrole | ทำ role อะไร |
| `workteam_id` | Many2one → workteam | อยู่ทีมไหน |
| **Time-off** | | |
| `is_leave` | Boolean | มีการลาหรือไม่ |
| `leave_id` | Many2one → hr.leave | Link ไปใบลา |
| `leave_type` | Char (related) | ประเภทการลา |
| **Substitution** | | |
| `substitute_id` | Many2one → hr.employee | คนมาทำแทน (ถ้ามี) |
| `is_substitute` | Boolean | เป็นคนทำแทนหรือไม่ |
| `original_employee_id` | Many2one → hr.employee | ทำแทนใคร |
| **Tracking** | | |
| `source` | Selection | `generated` / `manual` / `swapped` / `timeoff` |
| `note` | Text | หมายเหตุ |

---

### 1.3 itx.schedule.planning.config (Mapping: Workrole + Template)

การจับคู่ระหว่าง Workrole กับ Template

| Field | Type | Description |
|-------|------|-------------|
| `planning_id` | Many2one → planning | อยู่ใน Planning ไหน |
| `workrole_id` | Many2one → workrole | กลุ่มงาน |
| `template_id` | Many2one → template | Template ที่ใช้ |
| `min_employees_per_shift` | Integer | จำนวนคนขั้นต่ำต่อกะ |
| `initial_shift` | Selection | กะเริ่มต้น (morning/afternoon/night) |
| `initial_team` | Many2one → workteam | ทีมเริ่มต้น |
| `initial_day_in_pattern` | Integer | วันที่เท่าไหร่ใน pattern (1-10 สำหรับ 7on-3off) |

---

## 2. Master Data Models

### 2.1 itx.employee.workrole (Work Role/Position)

กลุ่มงาน/ตำแหน่งงาน - พนักงานที่ทำงานเหมือนกัน แลกกะกันได้

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | ชื่อ เช่น "APM Driver", "APM Operator", "Maintenance" |
| `code` | Char | รหัส เช่น "DRIVER", "OPERATOR", "MAINT" |
| `description` | Text | รายละเอียด |
| `team_ids` | One2many → workteam | ทีมย่อยในกลุ่มงานนี้ |
| `employee_ids` | Many2many → hr.employee | พนักงานทั้งหมดใน role นี้ |
| `skill_ids` | Many2many → hr.skill | ทักษะที่ต้องมี |
| `active` | Boolean | Active/Inactive |

**Example Workroles:**

| Name | Code | Description |
|------|------|-------------|
| APM Driver | DRIVER | พนักงานขับรถอัตโนมัติ |
| APM Operator | OPERATOR | พนักงานควบคุมระบบ |
| Maintenance | MAINT | ทีมซ่อมบำรุง |

---

### 2.2 itx.employee.workteam (Team within Workrole)

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

**Example Teams:**

| Name | Code | Sequence | Workrole |
|------|------|----------|----------|
| Team A | A | 1 | APM Driver |
| Team B | B | 2 | APM Driver |
| Team C | C | 3 | APM Driver |
| Team D | D | 4 | APM Driver |

---

### 2.3 itx.schedule.planning.template (Schedule Template)

Template รูปแบบการทำงาน - เก็บกฎเกณฑ์การหมุนเวียนกะ (User สร้างเองได้หลาย pattern)

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | ชื่อ Template เช่น "3 Shifts 4 Teams Rotation" |
| `code` | Char | รหัส |
| `description` | Text | รายละเอียด |
| `is_default` | Boolean | เป็น default template หรือไม่ |
| **Rotation Settings** | | |
| `rotation_direction` | Selection | `forward` (เช้า→บ่าย→ดึก) / `backward` (เช้า→ดึก→บ่าย) |
| `rotation_period_count` | Integer | เปลี่ยนกะทุกกี่ period (default: 1 = ทุก period) |
| `shifts_per_day` | Integer | จำนวนกะต่อวัน (default: 3) |
| **Work-Off Pattern** | | |
| `pattern_id` | Many2one → pattern | Work-Off Pattern ที่ใช้ |
| **Shift Duration** | | |
| `shift_duration` | Float | ชั่วโมงทำงานต่อกะ (default: 8) |
| `break_duration` | Float | ชั่วโมงพัก (default: 1) |
| `total_shift_hours` | Float (computed) | รวมชั่วโมงต่อกะ (shift + break) |
| **Day Break Pattern** | | |
| `day_break_pattern` | Selection | `4w1b4w` / `5w1b3w` / `custom` |
| `day_break_work_before` | Integer | ชั่วโมงทำงานก่อนพัก (4 หรือ 5) |
| `day_break_work_after` | Integer | ชั่วโมงทำงานหลังพัก (4 หรือ 3) |
| **Shift Times** | | |
| `shift_time_ids` | One2many → shift.time | เวลาแต่ละกะ |
| `active` | Boolean | Active/Inactive |

---

### 2.4 itx.schedule.workoff.pattern (Work-Off Pattern)

รูปแบบวันทำงาน-วันหยุด (User สร้างเองได้หลาย pattern)

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | ชื่อ Pattern เช่น "7-On 3-Off" |
| `code` | Char | รหัส เช่น "7ON3OFF" |
| `work_days` | Integer | จำนวนวันทำงานติดต่อกัน (7) |
| `off_days` | Integer | จำนวนวันหยุดติดต่อกัน (3) |
| `pattern_length` | Integer (computed) | ความยาว pattern (work_days + off_days) |
| `is_default` | Boolean | เป็น default pattern หรือไม่ |
| `active` | Boolean | Active/Inactive |

**Example Patterns (User สร้างเอง):**

| Name | Code | Work Days | Off Days | Length |
|------|------|-----------|----------|--------|
| 7-On 3-Off | 7ON3OFF | 7 | 3 | 10 |
| 5-On 2-Off | 5ON2OFF | 5 | 2 | 7 |
| 4-On 2-Off | 4ON2OFF | 4 | 2 | 6 |

---

### 2.5 itx.schedule.shift.time (Shift Time Definition)

กำหนดเวลาของแต่ละกะ

| Field | Type | Description |
|-------|------|-------------|
| `template_id` | Many2one → template | อยู่ใน Template ไหน |
| `name` | Char | ชื่อกะ เช่น "กะเช้า", "กะบ่าย", "กะดึก" |
| `code` | Char | รหัส เช่น "MORNING", "AFTERNOON", "NIGHT" |
| `sequence` | Integer | ลำดับ 1, 2, 3 |
| `hour_start` | Float | เวลาเริ่ม (0-24) |
| `hour_end` | Float | เวลาสิ้นสุด (0-24, ข้ามวันได้) |
| `is_overnight` | Boolean (computed) | ข้ามวันหรือไม่ |
| `color` | Integer | สีแสดงบน Timeline |

**Default Shift Times:**

| Name | Code | Start | End | Overnight |
|------|------|-------|-----|-----------|
| กะเช้า | MORNING | 06:00 | 14:00 | No |
| กะบ่าย | AFTERNOON | 14:00 | 22:00 | No |
| กะดึก | NIGHT | 22:00 | 06:00 | Yes |

---

### 2.6 itx.schedule.shift.type (Shift Type - Simplified)

ประเภทกะ (Master Data แยกจาก Template สำหรับใช้ทั่วไป)

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | ชื่อ เช่น "กะเช้า" |
| `code` | Char | รหัส เช่น "MORNING" |
| `hour_start` | Float | เวลาเริ่ม default |
| `hour_end` | Float | เวลาสิ้นสุด default |
| `is_day_off` | Boolean | เป็นวันหยุดหรือไม่ |
| `color` | Integer | สี |
| `active` | Boolean | Active/Inactive |

---

## 3. Shift Swap Request Model

### 3.1 itx.schedule.swap.request

ใบขอแลกกะ

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char (computed) | ชื่อ Request |
| `planning_id` | Many2one → planning | อยู่ใน Planning ไหน |
| **Requester (Employee A)** | | |
| `requester_id` | Many2one → hr.employee | พนักงานที่ขอ |
| `requester_line_id` | Many2one → line | กะของผู้ขอ |
| `requester_date` | Date (related) | วันที่กะผู้ขอ |
| **Partner (Employee B)** | | |
| `partner_id` | Many2one → hr.employee | พนักงานคู่แลก |
| `partner_line_id` | Many2one → line | กะของคู่แลก |
| `partner_date` | Date (related) | วันที่กะคู่แลก |
| **Workflow** | | |
| `state` | Selection | (see below) |
| `reason` | Text | เหตุผลที่ขอแลก |
| `reject_reason` | Text | เหตุผลที่ปฏิเสธ |
| **Timestamps** | | |
| `confirmed_date` | Datetime | วันที่คู่แลก confirm |
| `supervisor_approved_date` | Datetime | วันที่หัวหน้าอนุมัติ |
| `hr_approved_date` | Datetime | วันที่ HR อนุมัติ |
| `rejected_date` | Datetime | วันที่ถูก reject |
| `rejected_by` | Many2one → res.users | ใคร reject |

**States:**

| State | Value | Description |
|-------|-------|-------------|
| Draft | `draft` | พนักงาน A สร้าง Request |
| Confirmed | `confirmed` | พนักงาน B acknowledge |
| Supervisor Approved | `supervisor_approved` | หัวหน้าอนุมัติ |
| HR Approved | `hr_approved` | HR อนุมัติ |
| Done | `done` | สลับกะเรียบร้อย |
| Rejected | `rejected` | ถูกปฏิเสธ |

---

## 4. Constraint Engine Models

### 4.1 itx.schedule.constraint

กฎเกณฑ์/ข้อจำกัดที่ HR จัดการได้

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | ชื่อ Constraint |
| `code` | Char | รหัส เช่น "REST_10H", "MAX_48H_WEEK" |
| `description` | Text | รายละเอียด |
| `constraint_type` | Selection | `warning` / `blocking` |
| `is_active` | Boolean | เปิด/ปิดใช้งาน |
| `python_code` | Text | Python code สำหรับ validate |
| `error_message` | Char | ข้อความ error |
| `sequence` | Integer | ลำดับการตรวจสอบ |

**Default Constraints:**

| Name | Code | Type | Description |
|------|------|------|-------------|
| พักขั้นต่ำ 10 ชม. | REST_10H | blocking | พักติดต่อกันไม่น้อยกว่า 10 ชม.ก่อนกะถัดไป |
| ไม่เกิน 8 ชม./วัน | MAX_8H_DAY | warning | ทำงานไม่เกิน 8 ชม./วัน |
| ไม่เกิน 48 ชม./สัปดาห์ | MAX_48H_WEEK | blocking | ทำงานไม่เกิน 48 ชม./สัปดาห์ |
| พักระหว่างวัน 30 นาที | BREAK_30M | warning | ต้องมีพักระหว่างวันอย่างน้อย 30 นาที |

---

## 5. Extended Models

### 5.1 hr.employee (Extension)

| Field | Type | Description |
|-------|------|-------------|
| `workrole_id` | Many2one → workrole | กลุ่มงาน |
| `workteam_id` | Many2one → workteam | ทีม |
| `schedule_line_ids` | One2many → line | ตารางงานทั้งหมด |
| `swap_request_ids` | One2many → swap | Requests ทั้งหมด |

### 5.2 hr.leave (Extension)

| Field | Type | Description |
|-------|------|-------------|
| `schedule_line_ids` | One2many → line | กะที่ถูก affected |

---

## 6. Configuration Models

### 6.1 itx.schedule.period (Period Definition)

กำหนดช่วงเวลา period - User กำหนดเองได้

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | ชื่อ Period เช่น "March 2026" |
| `date_start` | Date | วันเริ่ม period (default: 26) |
| `date_end` | Date | วันสิ้นสุด period (default: 25 ของเดือนถัดไป) |
| `planning_ids` | One2many → planning | Planning ใน period นี้ |
| `state` | Selection | `draft` / `active` / `closed` |

**Default Period:**
```
ปกติ: วันที่ 26 ของเดือน → วันที่ 25 ของเดือนถัดไป

ตัวอย่าง: Period เดือนมีนาคม 2026
         เริ่ม:     26 กุมภาพันธ์ 2026
         สิ้นสุด:   25 มีนาคม 2026
```

### 6.2 itx.schedule.config.settings

| Field | Type | Description |
|-------|------|-------------|
| `default_period_start_day` | Integer | วันเริ่มต้น period default (default: 26) |
| `default_planning_weeks` | Integer | จำนวนสัปดาห์ที่วางแผนล่วงหน้า |
| `auto_activate` | Boolean | Auto activate วันแรกของ period |

**Note:**
- Cross-workrole swap = **ไม่อนุญาต** (hardcoded)
- Archive ทำได้ทันทีหลังจบ period (ไม่ต้องรอ)

---

## 7. Model Relationships Diagram

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
┌─────────────────────┐        ┌─────────────────┐        ┌─────────────────────┐
│ itx.schedule        │        │   hr.employee   │        │    hr.contract      │
│ .planning.template  │        │    (พนักงาน)     │        │   (สัญญาจ้าง)        │
└──────────┬──────────┘        └────────┬────────┘        └─────────────────────┘
           │                            │
           │ many2one                   │ many2one
           └──────────┬─────────────────┘
                      ▼
         ┌─────────────────────────────────┐
         │  itx.schedule.planning.config   │
         │    (Mapping: workrole+template) │
         └───────────────┬─────────────────┘
                         │ one2many
                         ▼
         ┌─────────────────────────────────┐
         │     itx.schedule.planning       │
         │        (Main Output)            │
         └───────────────┬─────────────────┘
                         │ one2many
                         ▼
         ┌─────────────────────────────────┐
         │   itx.schedule.planning.line    │
         │      (Daily per Employee)       │
         └───────────────┬─────────────────┘
                         │
            ┌────────────┴────────────┐
            ▼                         ▼
┌─────────────────────┐    ┌─────────────────────────┐
│     hr.leave        │    │ itx.schedule.swap       │
│   (ใบลา)            │    │ .request (ใบขอแลกกะ)    │
└─────────────────────┘    └─────────────────────────┘
```
