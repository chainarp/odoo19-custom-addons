# AI Conversation Management - "The Art of Guiding AI"

**Date:** 2025-12-26
**Purpose:** Define how ITX Moduler should manage AI conversations effectively
**Status:** Design Specification

---

## 🎯 Core Problem

**"AI ต้องถูกตะล่อม"** - AI ไม่สามารถทำงานได้ดีเองโดยอัตโนมัติ

### Current Issues with AI Development:
- ❌ AI ลืมบริบทง่าย → ต้องย้ำซ้ำ
- ❌ AI วิ่งไปคนละทาง → ต้องดึงกลับมา
- ❌ AI สมมติเอง → ผลลัพธ์ไม่ตรงต้องการ
- ❌ AI ไม่รู้ว่าถึงไหนแล้ว → งงว่าต้องทำอะไรต่อ
- ❌ ต้อง "คุม" AI ตลอดเวลา → เหนื่อย

### Solution Direction:
**ITX Moduler ต้องเป็น "AI Conversation Manager"** ที่:
- ✅ จำบริบทให้ AI
- ✅ กำหนดกรอบให้ AI
- ✅ เตือน AI เมื่อวิ่งออกนอกทาง
- ✅ พา AI ไปทีละขั้น
- ✅ ให้ user ควบคุมได้ง่าย

---

## 📋 10 Core Capabilities

### 1. Context Memory (จำบริบท) 🧠

**Problem:**
```
Conversation 1:
User: "ทำระบบจองห้องประชุม"
AI: "เข้าใจค่ะ..."

--- 30 minutes later ---

Conversation 2:
User: "เพิ่ม field attendees"
AI: "เพิ่มที่ model ไหนครับ?" ❌ (ลืมแล้วว่ากำลังทำอะไร)
```

**Solution:**
```
ITX Moduler จำไว้:
├── Project Context
│   ├── Module Name: "conference_booking"
│   ├── Purpose: "จองห้องประชุม"
│   └── Target: Odoo 19
│
├── Design Decisions
│   ├── Models: conference.room, conference.booking, conference.equipment
│   ├── Main Pattern: State-based workflow
│   └── Security: 2 groups (User, Manager)
│
└── Current Focus
    ├── Working On: conference.booking model
    ├── Current Step: Defining fields
    └── Next: Relations between models

AI can access this context anytime
```

**User Experience:**
```
User: "เพิ่ม field attendees"
AI: "เข้าใจค่ะ จะเพิ่ม attendee_ids (Many2many → res.users)
     ที่ conference.booking model ใช่ไหม?"
✅ AI รู้บริบทโดยอัตโนมัติ
```

---

### 2. Decision Log (บันทึกการตัดสินใจ) 📝

**Problem:**
```
Week 1: User: "ใช้ mail.thread"
Week 2: AI แนะนำ: "อาจไม่ต้องใช้ mail.thread" ❌
→ ทำไมแนะนำไม่สอดคล้อง?
```

**Solution:**
```
Decision Log:
┌─────────────────────────────────────────────────────────┐
│ #1 [APPROVED] Use mail.thread mixin                    │
│    Reason: Need chatter, followers, activities         │
│    Date: 2025-12-20                                     │
│    Impact: All main models inherit mail.thread         │
├─────────────────────────────────────────────────────────┤
│ #2 [APPROVED] Use state pattern                        │
│    Reason: Need workflow (draft→confirmed→done)        │
│    Date: 2025-12-20                                     │
│    Impact: Add state field, statusbar widget           │
├─────────────────────────────────────────────────────────┤
│ #3 [REJECTED] Use wizard for booking                   │
│    Reason: Too complex, simple form is enough          │
│    Date: 2025-12-21                                     │
│    Impact: Use normal form, not TransientModel         │
└─────────────────────────────────────────────────────────┘
```

**User Experience:**
```
AI แนะนำ: "ควรใช้ wizard..."
System เช็ค: Decision #3 rejected wizard
AI ปรับ: "เนื่องจากคุณไม่ต้องการใช้ wizard (decision #3)
          แนะนำให้ใช้ normal form + server action แทน"
✅ AI สอดคล้องกับ decisions ที่ผ่านมา
```

---

### 3. Guided Conversation (พาไปทีละขั้น) 🚶

**Problem:**
```
AI ถามทุกอย่างพร้อมกัน:
"บอกหน่อยว่า:
 - มี models อะไรบ้าง
 - แต่ละ model มี fields อะไร
 - relations ยังไง
 - security ต้องการอย่างไร
 - views แบบไหน
 - ..."
❌ Overwhelmed!
```

**Solution:**
```
Conversation Flow (Progressive):

Step 1: High-Level Understanding
├── What: "ทำระบบจองห้องประชุม"
└── Who: Internal users only

Step 2: Core Models
├── conference.room
├── conference.booking
└── conference.equipment

Step 3: Focus Model 1 (conference.room)
├── Basic Fields: name, capacity, location
├── Relations: equipment_ids
└── Constraints: name unique

Step 4: Focus Model 2 (conference.booking)
├── Basic Fields: ...
└── ...

Step 5: Relations Between Models
...

Step 6: Security
...

→ Each step builds on previous
→ User not overwhelmed
→ Clear progress
```

**User Experience:**
```
Progress: ████████░░ 80%

Current Step: Relations (4/6)
Completed: ✅ High-level ✅ Models ✅ Fields
Next: Security

[Continue] [Back] [Skip to Step]
```

---

### 4. Constraint Validation (เช็คความขัดแย้ง) ⚠️

**Problem:**
```
User: "เพิ่ม field email ใน booking"
AI: "เพิ่มแล้วครับ"
→ แต่ booking มี user_id แล้ว (ซ้ำซ้อน!)
❌ ไม่มีใครเตือน
```

**Solution:**
```
Validation Rules:
├── Data Model Rules
│   ├── No duplicate information (email in user already)
│   ├── No orphan relations (must have parent model)
│   └── No circular dependencies
│
├── Odoo Best Practices
│   ├── Don't duplicate standard fields
│   ├── Use computed fields when possible
│   └── Follow naming conventions
│
└── Design Consistency
    ├── All state-based models use same states
    ├── All main models inherit same mixins
    └── Security groups consistent across models
```

**User Experience:**
```
User: "เพิ่ม field email"

AI: ⚠️ Warning: Potential Redundancy
    booking model already has:
    - user_id.email (via Many2one)

    Do you want to:
    A. Use existing user_id.email (Recommended)
    B. Add separate email field (Why?)
    C. Let me explain more

✅ AI warns before creating problems
```

---

### 5. Incremental Refinement (ค่อยๆละเอียดขึ้น) 🔄

**Problem:**
```
AI พยายามทำให้สมบูรณ์แบบในครั้งแรก
→ ใช้เวลานาน
→ ถ้าต้องเปลี่ยน ต้องทำใหม่หมด
❌ Waterfall approach
```

**Solution:**
```
Iterative Approach:

Round 1: Skeleton (ใช้งานได้ขั้นต่ำ)
├── Basic models (ไม่มี computed fields)
├── Basic fields (required only)
├── Simple views (form, tree)
└── Basic security (1 group)
→ Working prototype in 15 minutes

Round 2: Core Features
├── Add relations
├── Add constraints
├── Add compute fields
└── Add proper security (2-3 groups)
→ Working module in 1 hour

Round 3: Polish
├── Advanced features (cron, automation)
├── Better views (kanban, calendar)
├── Reports
└── Tests
→ Production-ready in 3 hours

→ ทำได้ทีละ round
→ แต่ละ round ใช้งานได้จริง
→ เปลี่ยนใจง่าย (ยังไม่ลงลึก)
```

**User Experience:**
```
Current Round: 1 (Skeleton)
✅ Can already test basic CRUD

Want to:
A. Continue to Round 2 (Add features)
B. Refine Round 1 (Change models)
C. Export Round 1 (Use as is)

✅ Flexible, not locked in
```

---

### 6. Why Tracking (จำเหตุผล) 🤔

**Problem:**
```
Design says: "ใช้ mail.thread"
But why?
→ ถ้า requirements เปลี่ยน ไม่รู้ว่าต้อง update อะไร
```

**Solution:**
```
Decision Tree:

Use mail.thread
├── Why? Need follower system
│   ├── Requirement: Users need notifications
│   ├── Requirement: Multiple people track bookings
│   └── Impact: Add followers widget to views
│
├── Why? Need activity system
│   ├── Requirement: Reminder for booking owner
│   ├── Requirement: Approval workflow tracking
│   └── Impact: Add activity widget to views
│
└── Why? Need chatter
    ├── Requirement: Communication history
    └── Impact: Add message_ids to views

If requirement "Need follower system" removed:
→ Auto-suggest: Remove mail.thread? (lose chatter too)
→ Or keep for other reasons?
```

**User Experience:**
```
User: "ไม่ต้องการ follower system แล้ว"

AI: "เข้าใจค่ะ follower system เป็นหนึ่งในเหตุผลที่ใช้ mail.thread
     เหตุผลอื่นที่ยังใช้:
     - Activity tracking (for reminders)
     - Chatter (for communication)

     ต้องการ:
     A. เอา follower ออกอย่างเดียว (keep mail.thread)
     B. เอา mail.thread ออกทั้งหมด (lose all 3 features)
     C. ใช้ alternative (แนะนำอะไร?)

✅ AI รู้ว่าการเปลี่ยนกระทบอะไรบ้าง
```

---

### 7. Assumption Checking (ถามก่อนสมมติ) ✋

**Problem:**
```
User: "เพิ่ม field phone"
AI สมมติ: เป็น Char field
AI สร้าง: fields.Char('Phone')
→ แต่ถ้า user ต้องการ phone widget ล่ะ?
❌ AI ไม่ถาม
```

**Solution:**
```
Before Acting, Ask:

User: "เพิ่ม field phone"

AI Assumptions:
├── Field type: Char (default for phone)
├── Widget: phone (better UX)
├── Validation: Phone format (recommended)
└── International: No country code (assumption)

AI: "จะเพิ่ม phone field:
     - Type: Char
     - Widget: phone (clickable)
     - Validation: Phone format (optional)

     ถูกต้องไหม? [Yes] [Customize]"

✅ User can confirm or adjust
```

**User Experience:**
```
AI: "ผมจะสมมติว่า..."
    [Quick Accept] [Let me customize]

If customize:
├── Field Type: [Char] [Phone] [Text]
├── Validation: [None] [Phone Format] [Custom]
└── Widget: [Default] [Phone] [URL]

✅ Clear assumptions, easy to adjust
```

---

### 8. Conflict Resolution (แก้ไขความขัดแย้ง) ⚔️

**Problem:**
```
Requirement A: "booking ต้องมี user_id"
Design Decision: "ใช้ mail.thread (มี user_id built-in)"
User แก้: "เอา mail.thread ออก"
→ แล้ว user_id ทำยังไง?
❌ ไม่มีใครเตือน
```

**Solution:**
```
Conflict Detection:

Change Request: Remove mail.thread
AI Detects Conflicts:
├── Conflict #1: user_id field
│   ├── Current: Inherited from mail.thread
│   ├── After remove: Lost
│   └── Required by: Requirement #3
│
├── Conflict #2: activity tracking
│   ├── Current: From mail.activity.mixin
│   ├── After remove: Lost
│   └── Required by: Requirement #7
│
└── Conflict #3: Views
    ├── 3 views use message_ids widget
    └── Will break after remove

AI Suggests:
A. Keep mail.thread (no changes)
B. Add user_id manually + remove activity requirement
C. Alternative: Use simpler mixin
```

**User Experience:**
```
User: "เอา mail.thread ออก"

AI: ⚠️ Found 3 conflicts
    [Show Details] [Proceed Anyway] [Find Alternative]

If [Show Details]:
├── ❌ Lose user_id (required by requirement #3)
├── ❌ Lose activities (required by requirement #7)
└── ⚠️ 3 views will break

Suggested Solutions:
A. Keep mail.thread → No changes needed
B. Remove + fix manually → 8 changes required
C. Use mail.alias only → Partial solution

✅ User makes informed decision
```

---

### 9. Progress Awareness (รู้ว่าถึงไหนแล้ว) 📊

**Problem:**
```
User: "ต่อไปทำอะไร?"
AI: "..." ❌ (ไม่รู้ว่าทำอะไรไปแล้ว)
```

**Solution:**
```
Progress Tracking:

Module: conference_booking
Overall: ████████░░ 75%

Phases:
├── [✅] 1. Requirements (100%)
│   ├── ✅ Business requirements
│   ├── ✅ User requirements
│   └── ✅ Technical requirements
│
├── [✅] 2. Design (100%)
│   ├── ✅ Data model
│   ├── ✅ Architecture decisions
│   └── ✅ Security design
│
├── [🔄] 3. Implementation (60%)
│   ├── ✅ Models (100%)
│   ├── ✅ Fields (100%)
│   ├── 🔄 Relations (80%)
│   ├── 🔄 Business Logic (40%)
│   ├── ⏳ Views (20%)
│   └── ❌ Security (0%)
│
├── [⏳] 4. Testing (0%)
└── [⏳] 5. Documentation (0%)

Current: Working on Business Logic
Next Suggested: Complete Relations → Views
```

**User Experience:**
```
Dashboard:
┌─────────────────────────────────────┐
│ Progress: 75%  ████████░░           │
├─────────────────────────────────────┤
│ Current: Business Logic (40%)       │
│                                     │
│ Blocking Issues: None               │
│ Warnings: 2 relations incomplete    │
│                                     │
│ Next Steps:                         │
│ 1. Complete compute methods         │
│ 2. Add constraints                  │
│ 3. Start on Views                   │
└─────────────────────────────────────┘

[Continue] [Jump to Section] [Review Progress]

✅ Always know where you are
```

---

### 10. Rollback & Iteration (ย้อนกลับได้) ⏪

**Problem:**
```
User: "ไม่เอา Model B แล้ว ลบ"
AI: "ลบแล้วครับ"
→ แต่ Model C ยัง reference Model B อยู่
→ Module พัง ❌
```

**Solution:**
```
Dependency Tracking:

Model B has:
├── Dependencies (ถูกใช้โดย)
│   ├── Model C.field_x (Many2one → Model B)
│   ├── Model D.field_y (Many2many → Model B)
│   └── View "booking_form" (shows Model B data)
│
└── Requirements (ต้องการ)
    ├── Model A (inherits)
    └── Group "booking_user" (for ACLs)

Delete Request: Model B
AI Calculates Impact:
├── Will break: Model C, Model D, 1 view
├── Will orphan: 15 records in database
└── Cascade delete: 3 ACLs, 2 menus

AI Asks:
"Deleting Model B will affect:
 - Model C (field_x will break) → Need to remove or change
 - Model D (field_y will break) → Need to remove or change
 - View booking_form → Need to remove or update
 - 3 ACLs, 2 menus → Auto-delete

 Proceed? [Yes] [No] [Show Details]"
```

**User Experience:**
```
User: "ลบ Model B"

AI: ⚠️ Impact Analysis

Direct Impact:
├── ❌ Model C.field_x (Many2one)
├── ❌ Model D.field_y (Many2many)
└── ⚠️ 1 view will break

Cascade Delete:
├── 3 ACLs
├── 2 menus
└── 1 action

Do you want to:
A. Delete Model B + Auto-fix all (remove fields, views)
B. Delete Model B only (manual fix required)
C. Cancel (keep everything)

[A] [B] [C] [Show Full Impact Tree]

✅ Safe deletion with full visibility
```

---

## 🎯 Summary of 10 Core Capabilities

| # | Capability | Purpose | User Benefit |
|---|-----------|---------|--------------|
| 1 | Context Memory | จำบริบท | ไม่ต้องย้ำซ้ำ |
| 2 | Decision Log | บันทึกตัดสินใจ | AI สอดคล้อง |
| 3 | Guided Conversation | พาทีละขั้น | ไม่งง ไม่ overwhelm |
| 4 | Constraint Validation | เช็คขัดแย้ง | ป้องกัน design flaws |
| 5 | Incremental Refinement | ค่อยๆละเอียด | ยืดหยุ่น เปลี่ยนง่าย |
| 6 | Why Tracking | จำเหตุผล | เข้าใจ impact ของการเปลี่ยน |
| 7 | Assumption Checking | ถามก่อนสมมติ | ผลลัพธ์ตรงใจ |
| 8 | Conflict Resolution | แก้ไขขัดแย้ง | Safe changes |
| 9 | Progress Awareness | รู้ว่าถึงไหน | มี direction |
| 10 | Rollback & Iteration | ย้อนกลับได้ | Risk-free experimentation |

---

## 💭 Philosophy

**"AI is powerful but needs guidance"**

ITX Moduler is not just an AI tool.
It's an **AI Conversation Manager** that:
- Remembers context
- Guides the conversation
- Validates consistency
- Prevents mistakes
- Tracks progress
- Enables safe iteration

**Result:** Productive human-AI collaboration, not frustrating back-and-forth

---

**Status:** Core Design Principles
**Next:** Technical Implementation Strategy

---

**Created:** 2025-12-26
**Author:** Based on real AI development experience
