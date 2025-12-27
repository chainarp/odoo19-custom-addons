# Requirements Management Vision

**Date:** 2025-12-26
**Status:** Vision & Concept (ฟุ้ง)
**Phase:** Pre-Implementation Planning

---

## 🎯 Vision Statement

**ITX Moduler จะมี Requirements Management System ที่:**
- ช่วย SA เก็บ requirements จาก end-user แบบครบถ้วน
- มี version control เพื่อติดตาม requirements ที่เปลี่ยนไป
- แสดง impact ของการเปลี่ยน requirements ต่อ design
- มี freeze mechanism ก่อน development
- AI ช่วยแนะนำและวิเคราะห์ตลอดกระบวนการ

---

## 💡 Core Concept

### ปัญหาที่พบ (Pain Points):
1. **SA ไม่รู้ว่าจะถามอะไรบ้าง** - ถาม end-user ไม่ครบ, ลืมถามรายละเอียดสำคัญ
2. **Requirements เปลี่ยนเรื่อยๆ** - End-user เปลี่ยนใจ, เพิ่ม/ลด features ระหว่างทาง
3. **ไม่รู้ impact ของการเปลี่ยน** - เปลี่ยน 1 feature ส่งผลต่อ design ยังไง? เพิ่มเวลาเท่าไหร่?
4. **ไม่มี baseline** - ไม่รู้ว่า requirements ตอนไหนเป็น "final" สำหรับ development
5. **ไม่เห็นภาพ evolution** - ไม่รู้ว่า requirements เปลี่ยนมายังไงบ้าง

### โซลูชัน:
- **Smart Questionnaire Generator** - AI สร้าง checklist ให้ SA ไปถาม end-user
- **Requirements Version Control** - Track ทุก version ของ requirements
- **Impact Analysis** - วิเคราะห์ impact ต่อ models, effort, risk
- **Freeze Mechanism** - Lock requirements ก่อน development
- **AI Assistant** - คุยกับ AI เพื่อ refine requirements

---

## 🎨 User Journey

### Phase 1: Initial Requirements Gathering

```
1. SA เริ่มโปรเจกต์ใหม่
   → เปิด ITX Moduler → "New Project from Requirements"

2. AI ถามคำถาม high-level
   → "ระบบนี้เกี่ยวกับอะไร?"
   → SA: "ระบบจัดการใบขอซื้อ"

3. AI วิเคราะห์และสร้าง Smart Questionnaire
   → AI: "ใบขอซื้อมักจะมี Approval Workflow, Budget Control, Supplier..."
   → AI สร้าง checklist แบ่งเป็นหมวดหมู่:
      • Master Data (Product, Supplier, Department)
      • Workflow & Approval
      • Budget & Finance
      • Notifications
      • Reports
      • Security

4. SA export checklist เป็น PDF/Word
   → นำไปถาม end-user

5. SA กลับมากรอก checklist
   → Upload หรือพิมพ์คำตอบลงระบบ

6. AI แปล requirements → Odoo Structure
   → แนะนำ models, fields, relations, security, automation
   → แสดง best practices + pitfalls to avoid

7. Save เป็น v1.0 (Draft)
```

### Phase 2: Iteration & Refinement

```
8. End-user ขอเพิ่ม feature (เช่น Catering Service)
   → SA update requirements
   → AI analyze impact:
      • ➕ Will add: 1 model, 3 fields
      • ⏱️ Effort: +8 hours
   → Save เป็น v1.1

9. End-user เปลี่ยนใจ (เอา Visitor Management แทน Catering)
   → SA update requirements
   → AI analyze impact:
      • ➖ Remove: catering.service
      • ➕ Add: visitor.management, visitor.badge
      • ⚠️ Wasted effort: ~4 hours on catering
      • ⏱️ New effort: +10 hours
   → Save เป็น v1.2

10. ทำซ้ำจนครบ (v1.3, v1.4...)
```

### Phase 3: Review & Freeze

```
11. SA + Stakeholders review
    → เปรียบเทียบ versions
    → ดู evolution graph
    → Check impact summary

12. Complete freeze checklist
    ☑ All stakeholders reviewed
    ☑ End-user sign-off
    ☑ Technical feasibility confirmed
    ☑ Timeline and budget approved

13. Freeze as v2.0
    → Requirements locked
    → Baseline for development established
    → Development team can start

14. หลัง freeze ถ้ามี changes
    → ต้องผ่าน change request process
    → Save เป็น v2.1+ with approval
```

---

## 📊 Key Features

### 1. Smart Questionnaire Generator

**Concept:**
- AI ถามคำถาม step-by-step
- แบ่งเป็นหมวดหมู่ (Master Data, Workflow, Security, etc.)
- สร้าง checklist ให้ SA ไปถาม end-user
- Export เป็น PDF/Word

**Example:**
```
[Step 1/5] ประเภทระบบ
○ Master Data
● Transaction
○ Reporting
○ Integration

[Step 2/5] Workflow Pattern
● ใช่ (มี approval)
  ☑ Simple (1 ขั้น)
  ☑ Multi-level (หลายขั้น)
  ☐ Conditional (ตามเงื่อนไข)

[Generate Checklist] →

📋 Generated Checklist:
1. ข้อมูลพื้นฐาน
   ☐ มี Product/Item อะไรบ้าง?
   ☐ มี Supplier ไหม?
   ☐ มี Department ไหม?

2. Workflow & Approval
   ☐ ใครสร้างใบขอซื้อได้?
   ☐ ขั้นตอนการอนุมัติ?
   ☐ เงื่อนไขการอนุมัติ?

[Export PDF] [Export Word]
```

### 2. Requirements → Structure Converter

**Concept:**
- Upload/พิมพ์ requirements ที่เก็บมา
- AI วิเคราะห์และแปลเป็น Odoo structure
- แนะนำ models, fields, relations, security
- แสดง best practices + common pitfalls

**Example:**
```
Input:
"ต้องการให้แผนกต่างๆ สร้างใบขอซื้อได้
ถ้าไม่เกิน 10,000 ให้ Manager อนุมัติ
ถ้าเกิน 10,000 ต้อง Director อนุมัติเพิ่ม"

Output:
📦 Models Recommended:
1. purchase.request
   • state: draft → manager → director → approved
   • Use: mail.thread, mail.activity.mixin

2. purchase.request.line
   • product_id, quantity, price_unit

🔐 Security:
   • Group: PR User (create own)
   • Group: PR Manager (approve <10k)
   • Group: PR Director (approve all)

⚙️ Business Logic:
   • @api.constrains check amount
   • Conditional workflow based on total_amount
```

### 3. Version Control & Timeline

**Concept:**
- Track ทุก version ของ requirements
- Timeline view แสดง evolution
- Compare versions (diff view)
- Graph แสดง complexity trend

**Example:**
```
Timeline:
[v1.0] ───▶ [v1.1] ───▶ [v1.2] ───▶ [v2.0 FROZEN]
Week 1      Week 2      Week 3      Week 4
  ↓           ↓           ↓           ↓
Initial   +Catering   -Catering   Final
2 models  3 models    +Visitor    for Dev
                      4 models

[View v1.0] [Compare v1.0→v1.1] [View All Changes]
```

### 4. Change Comparison (Diff)

**Concept:**
- เปรียบเทียบ version A vs B
- แสดง Added/Removed/Modified
- ละเอียดถึงระดับ field

**Example:**
```
Compare: v1.1 → v1.2

Summary:
➕ Added: 2 features
➖ Removed: 1 feature
📝 Modified: 3 features

Models Changes:
➖ Removed:
   ❌ catering.service (3 fields)

➕ Added:
   ✅ visitor.management (5 fields)
   ✅ visitor.badge (3 fields)

📝 Modified:
   conference.booking:
   - catering_ids (Removed)
   + visitor_ids (Added)
   ~ security_required (Modified: Optional → Required)

Security Changes:
➕ New Group: Visitor Manager
```

### 5. Impact Analysis

**Concept:**
- วิเคราะห์ impact ของการเปลี่ยน requirements
- แสดง design impact (models, fields, views)
- Effort impact (hours)
- Risk assessment

**Example:**
```
Impact Analysis: v1.1 → v1.2

Design Impact:
┌──────────────┬──────┬──────┐
│ Component    │ v1.1 │ v1.2 │
├──────────────┼──────┼──────┤
│ Models       │ 3    │ 4    │ (+1)
│ Fields       │ 24   │ 28   │ (+4)
│ Views        │ 8    │ 12   │ (+4)
│ Security     │ 3    │ 4    │ (+1)
└──────────────┴──────┴──────┘

Effort Impact:
├─ Added: +10 hours (visitor features)
├─ Removed: -8 hours saved (catering)
└─ Net: +2 hours

Risk Impact:
🟡 Medium Risk: Security validation needs review
🟢 Low Risk: Badge generation standard
```

### 6. Freeze Mechanism

**Concept:**
- Checklist ก่อน freeze
- Lock requirements เมื่อ ready
- Establish baseline for development
- Change request process หลัง freeze

**Example:**
```
🔒 Freeze Requirements?

Current: v1.2 (Draft)
Freeze as: v2.0

Pre-Freeze Checklist:
☑ All stakeholders reviewed
☑ End-user sign-off
☑ Technical feasibility confirmed
☑ Timeline approved
☐ Final review meeting

Freeze Notes:
"Final requirements after 3 rounds.
 Removed catering, added visitor.
 Approved by Management."

After freeze:
• Development can start
• Changes → v2.1 (change request)

[Freeze as v2.0]
```

### 7. AI Conversation Assistant

**Concept:**
- คุยกับ AI แบบ natural language
- AI ถาม follow-up questions
- AI แนะนำและเตือน
- AI วิเคราะห์ impact ทุกครั้งที่เปลี่ยน

**Example:**
```
SA: "ผู้ใช้บอกเพิ่มว่า อยากให้มี catering service"

AI: 📝 เพิ่ม Catering Service

    Impact:
    ➕ catering.service model
    ➕ catering_ids field
    ⏱️ +8 hours

    Save as v1.1?
    [Yes]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SA: "เปลี่ยนใจ ไม่เอา catering เอา visitor แทน"

AI: 🤔 เปลี่ยน Catering → Visitor

    Impact:
    ➖ Remove catering (-8h)
    ➕ Add visitor (+10h)
    ⚠️ Wasted: ~4 hours on catering

    💡 Recommendation:
       Keep catering for future phase?

    [Proceed] [Keep Both] [Review First]
```

---

## 🎯 Design Principles

### 1. Hybrid Approach
- Form-based wizard (step-by-step) สำหรับเก็บ requirements
- Conversational AI สำหรับ refine และ analyze
- Visual timeline/graph สำหรับเห็นภาพ evolution

### 2. All Outputs
- Checklist (PDF/Word) สำหรับไปถาม end-user
- Structure diagram (visual) สำหรับเห็นภาพ design
- Impact report สำหรับ stakeholders
- ทั้งหมดพร้อมกัน

### 3. End-User vs Technical Separation
- คุยกับ end-user: ไม่ technical มาก
- ถามให้ครบทุกประเด็นจำเป็น
- SA vs AI: คุยกัน technical ได้เต็มที่

### 4. Requirements Evolution
- แก้ไขได้เรื่อยๆ ก่อน freeze
- มี version control
- เห็นภาพการเปลี่ยนไป
- เห็น impact ต่อ design

### 5. AI Guidance
- AI แนะนำตลอดกระบวนการ
- AI เตือนเมื่อควร freeze
- AI วิเคราะห์ impact ทุกการเปลี่ยน
- AI ช่วยตัดสินใจ

---

## 📊 Data Models (Conceptual)

### Requirements Version
```python
class RequirementsVersion(models.Model):
    _name = 'itx.moduler.requirements.version'

    name = fields.Char('Version')  # v1.0, v1.1, v2.0
    project_id = fields.Many2one('itx.moduler.ai.project')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('review', 'Under Review'),
        ('frozen', 'Frozen'),
    ])

    frozen_date = fields.Datetime()
    frozen_by = fields.Many2one('res.users')

    feature_ids = fields.One2many('itx.moduler.requirements.feature', 'version_id')

    parent_version_id = fields.Many2one('itx.moduler.requirements.version')
    change_summary = fields.Text()

    # Metrics
    models_count = fields.Integer()
    fields_count = fields.Integer()
    effort_hours = fields.Float()

    notes = fields.Html('Freeze Notes')
```

### Requirements Feature
```python
class RequirementsFeature(models.Model):
    _name = 'itx.moduler.requirements.feature'

    version_id = fields.Many2one('itx.moduler.requirements.version')

    name = fields.Char('Feature Name')
    description = fields.Text()
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ])

    status = fields.Selection([
        ('new', 'New'),
        ('modified', 'Modified'),
        ('unchanged', 'Unchanged'),
        ('removed', 'Removed'),
    ])

    # Design impact
    models_affected = fields.Text()
    fields_affected = fields.Text()
```

### Requirements Change
```python
class RequirementsChange(models.Model):
    _name = 'itx.moduler.requirements.change'

    version_from_id = fields.Many2one('itx.moduler.requirements.version')
    version_to_id = fields.Many2one('itx.moduler.requirements.version')

    change_type = fields.Selection([
        ('added', 'Added'),
        ('removed', 'Removed'),
        ('modified', 'Modified'),
    ])

    feature_id = fields.Many2one('itx.moduler.requirements.feature')

    description = fields.Text()
    impact = fields.Text()
    effort_delta = fields.Float('Effort Change')
```

---

## 🔄 Workflow

```
┌─────────────────────────────────────────────────────────┐
│ Requirements Lifecycle                                   │
└─────────────────────────────────────────────────────────┘

1. Initial Requirements (v1.0)
   ├─ SA เก็บ requirements จาก end-user
   ├─ AI สร้าง questionnaire
   ├─ AI แปลเป็น structure
   └─ Save as v1.0 (Draft)

2. Iteration Phase (v1.1, v1.2, v1.3...)
   ├─ End-user ขอเพิ่ม/ลด/แก้
   ├─ SA update requirements
   ├─ AI analyze impact
   ├─ Save as new version
   └─ Repeat

3. Review Phase
   ├─ Change state → "Under Review"
   ├─ Stakeholders review
   ├─ AI generate impact report
   └─ Approve/Request changes

4. Freeze Phase (v2.0)
   ├─ Complete checklist
   ├─ Change state → "Frozen"
   ├─ Record freeze date + notes
   └─ Development baseline

5. Change Request (v2.1+)
   ├─ New changes after freeze
   ├─ Formal change request
   ├─ Impact analysis
   └─ Approval required
```

---

## 🎨 UI Components (Conceptual)

### 1. Project Dashboard
- Requirements status (Draft/Review/Frozen)
- Current version
- Timeline view
- Quick actions

### 2. Smart Questionnaire Wizard
- Step-by-step form
- AI suggestions
- Export checklist
- Progress indicator

### 3. Requirements Editor
- Natural language input
- AI conversation panel
- Structure preview
- Save as version

### 4. Version Timeline
- Visual timeline
- Version cards
- Compare button
- Evolution graph

### 5. Diff Viewer
- Side-by-side comparison
- Added/Removed/Modified highlights
- Impact summary
- Drill-down details

### 6. Impact Dashboard
- Design metrics
- Effort estimation
- Risk assessment
- Action items

### 7. Freeze Dialog
- Pre-freeze checklist
- Freeze notes
- Confirmation
- Lock mechanism

---

## 💡 AI Capabilities Integration

### Conversation Management Capabilities Applied:

1. **Context Memory** ✅
   - Remember project requirements
   - Track all versions
   - Know current state

2. **Decision Log** ✅
   - Log all requirement changes
   - Track why features added/removed
   - Link to versions

3. **Guided Conversation** ✅
   - Step-by-step questionnaire
   - Progressive disclosure
   - Not overwhelming

4. **Constraint Validation** ✅
   - Check feasibility
   - Detect conflicts
   - Warn inconsistencies

5. **Incremental Refinement** ✅
   - Multiple versions (iterations)
   - Refine until satisfied
   - Freeze when ready

6. **Why Tracking** ✅
   - Capture reasons for changes
   - Document decisions
   - Freeze notes

7. **Assumption Checking** ✅
   - AI asks clarifying questions
   - Confirm interpretations
   - Validate understanding

8. **Conflict Resolution** ✅
   - Detect conflicting requirements
   - Suggest resolutions
   - Guide decisions

9. **Progress Awareness** ✅
   - Show version progress
   - Readiness for freeze
   - Completion percentage

10. **Rollback & Iteration** ✅
    - Revert to previous version
    - Compare and choose
    - Safe experimentation

---

## 📋 Open Questions (Deep Design - ทีหลัง)

### Freeze Process:
- หลัง freeze แก้ไม่ได้เลย? หรือแก้ได้แต่ต้อง approval?
- Change request process รายละเอียดยังไง?

### Impact Analysis:
- ควรละเอียดแค่ไหน? (models count? effort? cost? risk?)
- ใครเป็นคนประเมิน effort? (AI? SA? Developer?)

### AI Recommendations:
- ควรแนะนำเมื่อไหร่? (ทุกครั้ง? เฉพาะครั้งใหญ่?)
- ควรเข้มงวดแค่ไหน? (warning? blocking?)

### Version Naming:
- Semantic (v1.0, v1.1, v2.0)?
- Date-based (2025-12-26)?
- Milestone-based (Alpha, Beta, Final)?

---

## 🎯 Success Criteria

### For SA:
- ✅ เก็บ requirements ครบถ้วน ไม่ลืมถาม
- ✅ Track requirements changes ได้
- ✅ เห็น impact ของการเปลี่ยน
- ✅ มี baseline ชัดเจนก่อน development

### For End-User:
- ✅ ถูกถามคำถามที่ครบถ้วน ไม่งง
- ✅ เห็นภาพระบบที่จะได้
- ✅ เปลี่ยนใจได้จนกว่าจะ freeze

### For Development Team:
- ✅ ได้ requirements ที่ชัดเจน
- ✅ มี baseline ที่ stable
- ✅ เข้าใจ evolution ของ requirements

### For Project:
- ✅ Reduce rework จากการเปลี่ยน requirements ไม่รู้
- ✅ Better timeline estimation จาก impact analysis
- ✅ Clear audit trail ของ requirements changes

---

## 🚀 Next Steps

1. **Review Vision** - Confirm approach with stakeholders
2. **Deep Design** - Answer open questions, detailed specs
3. **Prototype** - Build proof of concept for key features
4. **Integrate** - Integrate with existing ITX Moduler architecture
5. **Implement** - Full implementation per roadmap

---

## 📚 Related Documents

- [IMPLEMENTATION_ROADMAP.md](./IMPLEMENTATION_ROADMAP.md) - Overall roadmap
- [STRATEGY_SUMMARY.md](./STRATEGY_SUMMARY.md) - Strategic direction
- [AI_CONVERSATION_MANAGEMENT.md](../04-Integration/AI_CONVERSATION_MANAGEMENT.md) - 10 AI capabilities
- [AI_TECHNICAL_IMPLEMENTATION.md](../04-Integration/AI_TECHNICAL_IMPLEMENTATION.md) - Technical design

---

**Status:** Vision Complete - Ready for Deep Design
**Next:** Design Document Workflow (คุยกันต่อ)

---

*Created: 2025-12-26*
*Type: Vision Document (ฟุ้ง)*
*Version: 1.0.0*
