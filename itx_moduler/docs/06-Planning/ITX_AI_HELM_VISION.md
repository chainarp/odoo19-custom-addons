# ITX AI Helm - Core AI Conversation Framework

**Date:** 2025-12-27 (Updated: 2025-12-29)
**Status:** Vision & Architecture (ฟุ้ง)
**Type:** Core Framework / Standalone Addon

---

## 🎯 Vision Statement

**ITX AI Helm เป็น Core Framework สำหรับสร้าง AI-Assisted Applications ที่:**
- 🎨 **Domain-agnostic** - ใช้ได้กับงานใดก็ได้ (Odoo development, Audio circuit, Camping vehicle, etc.)
- 🔌 **Pluggable** - ใส่ knowledge domain เข้าไปได้
- 🧩 **Reusable** - Addon อื่นๆ extend ไปใช้
- 🤖 **AI-Powered** - ใช้ Claude API (หรือ AI อื่นๆ)
- ⛵ **Ship's Wheel Metaphor** - Helm (พังงา) with 10 Spokes to control the mighty AI ship

### 🚢 The Ship's Wheel Metaphor
```
AI = Mighty Ship (powerful, large)
Helm (Ship's Wheel) = ITX AI Helm (control interface)
10 Spokes = The conversation management capabilities
Small person grabs the spokes to control the mighty ship
```

---

## 💡 Why ITX AI Helm?

### ปัญหาที่พบ:
1. **AI ต้องถูก "ตะล่อม"** - AI ต้องการการชี้แนะ เตือนความจำ กำหนดกรอบ
2. **แต่ละ Domain ต่างกัน** - Odoo dev ≠ Audio circuit ≠ Camping vehicle
3. **Core Capabilities เหมือนกัน** - Context memory, Decision log, Version control ใช้ร่วมกันได้
4. **ไม่ควรเขียนซ้ำ** - AI conversation management ควรเป็น framework

### โซลูชัน:
**แยก Core Framework (`itx_ai_helm`) ออกมา:**
- ✅ Core AI conversation management (The 10 Spokes)
- ✅ Domain plugin architecture
- ✅ Version control (requirements, design)
- ✅ Claude API integration
- ✅ Reusable UI components

**Domain-specific addons extend framework:**
- `itx_moduler` → Odoo Development Domain
- `itx_audio_circuit` → Audio Circuit Design Domain
- `itx_camping_vehicle` → Camping Vehicle Design Domain
- `your_domain` → Your Domain

---

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────┐
│                itx_ai_helm                           │
│         (Core AI Conversation Framework)             │
│              Ship's Wheel (Helm) 🚢                  │
├─────────────────────────────────────────────────────┤
│                                                      │
│ ┌─────────────────────────────────────────────┐    │
│ │  The 10 Spokes (Conversation Management)    │    │
│ │  • Spoke 1: Context Memory (Log Book)       │    │
│ │  • Spoke 2: Decision Log                    │    │
│ │  • Spoke 3: Guided Conversation             │    │
│ │  • Spoke 4: Constraint Validation           │    │
│ │  • Spoke 5: Incremental Refinement          │    │
│ │  • Spoke 6: Why Tracking                    │    │
│ │  • Spoke 7: Assumption Checking             │    │
│ │  • Spoke 8: Conflict Resolution             │    │
│ │  • Spoke 9: Progress Awareness              │    │
│ │  • Spoke 10: Rollback & Iteration           │    │
│ └─────────────────────────────────────────────┘    │
│                                                      │
│ ┌─────────────────────────────────────────────┐    │
│ │  Core Services                               │    │
│ │  • Conversation Manager                      │    │
│ │  • Claude API Client                         │    │
│ │  • Context Builder                           │    │
│ │  • Response Parser                           │    │
│ │  • Validation Engine                         │    │
│ │  • State Machine                             │    │
│ └─────────────────────────────────────────────┘    │
│                                                      │
│ ┌─────────────────────────────────────────────┐    │
│ │  Domain Plugin System                        │    │
│ │  • Domain Abstract Class                     │    │
│ │  • Knowledge Base Management                 │    │
│ │  • Pattern Library                           │    │
│ │  • Best Practices Engine                     │    │
│ └─────────────────────────────────────────────┘    │
│                                                      │
│ ┌─────────────────────────────────────────────┐    │
│ │  Version Control                             │    │
│ │  • Requirements Versioning                   │    │
│ │  • Design Versioning                         │    │
│ │  • Impact Analysis                           │    │
│ │  • Freeze Mechanism                          │    │
│ └─────────────────────────────────────────────┘    │
│                                                      │
│ ┌─────────────────────────────────────────────┐    │
│ │  UI Components                               │    │
│ │  • Chat Widget                               │    │
│ │  • Timeline View                             │    │
│ │  • Diff Viewer                               │    │
│ │  • Impact Dashboard                          │    │
│ └─────────────────────────────────────────────┘    │
│                                                      │
└─────────────────────────────────────────────────────┘
                         ↑
                         │ extends / depends
         ┌───────────────┼───────────────┬─────────────┐
         │               │               │             │
    ┌────▼────┐    ┌────▼────┐    ┌────▼────┐   ┌────▼────┐
    │   itx   │    │   itx   │    │   itx   │   │  Your   │
    │ moduler │    │  audio  │    │ camping │   │ Domain  │
    │         │    │ circuit │    │ vehicle │   │         │
    └─────────┘    └─────────┘    └─────────┘   └─────────┘

    Domain:        Domain:        Domain:        Domain:
    Odoo Dev       Audio Design   Vehicle        ?
```

---

## 🎨 Core Concepts

### 1. Project
- **AI Project** = งานที่ใช้ AI ช่วย
- แต่ละ Project มี Domain (Odoo, Audio, Camping, etc.)
- มี Requirements Versions, Design Versions
- มี Conversation Sessions

### 2. Domain
- **Domain** = Knowledge area (เช่น Odoo Development)
- Domain Plugin = ความรู้เฉพาะทาง + Patterns + Best Practices
- Pluggable architecture - เพิ่มได้เรื่อยๆ

### 3. Session
- **Session** = การสนทนา 1 ครั้ง
- มี Messages (User ↔ AI)
- มี Context (ข้อมูลที่ AI ต้องรู้)
- มี State (Draft → Review → Frozen)

### 4. Version
- **Requirements Version** = ความต้องการแต่ละ version (v1.0, v1.1, v2.0)
- **Design Version** = การออกแบบแต่ละ version (d1.0, d1.1, d2.0)
- Track changes, impact analysis
- Freeze mechanism

---

## 🎯 The 10 Spokes (Conversation Management Capabilities)

### Spoke 1: Context Memory 🧠 (Log Book)
**What:** Remember project, decisions, current state

**Models:**
- `itx.ai.context` - Context snapshots
- `itx.ai.context.item` - Individual context items

**Example:**
```python
# AI remembers:
- Project name: "Purchase Request System"
- Domain: Odoo Development
- Current phase: Design
- Requirements version: v2.0 (frozen)
- Design version: d0.3 (draft)
- Models designed: 3 (purchase.request, purchase.request.line, department.budget)
```

---

### Spoke 2: Decision Log 📝
**What:** Track all decisions with reasons (why) and impacts (what affected)

**Models:**
- `itx.ai.decision` - Decisions made
- `itx.ai.decision.reason` - Why decisions made
- `itx.ai.decision.impact` - What decisions affect

**Example:**
```python
Decision: "Use mail.thread mixin"
├─ Reason: "Need audit trail and chatter"
├─ Impact: "purchase.request model"
├─ Alternatives Rejected: "Custom logging"
└─ Made by: SA, Approved: Yes
```

---

### Spoke 3: Guided Conversation 🗺️
**What:** Step-by-step, progressive disclosure, not overwhelming

**Models:**
- `itx.ai.conversation.flow` - Conversation flow definition
- `itx.ai.conversation.step` - Steps in conversation
- `itx.ai.conversation.state` - Current state

**Example:**
```python
Flow: Requirements Gathering
├─ Step 1: System Type (Master Data / Transaction / Report)
├─ Step 2: Workflow Pattern (Simple / Multi-level / Conditional)
├─ Step 3: Generate Checklist
├─ Step 4: Collect Answers
└─ Step 5: Generate Structure

Current State: Step 3 (Generate Checklist)
```

---

### Spoke 4: Constraint Validation ✅
**What:** Check conflicts, feasibility before acting

**Models:**
- `itx.ai.validation.rule` - Validation rules
- `itx.ai.validation.result` - Validation results
- `itx.ai.conflict` - Detected conflicts

**Example:**
```python
Validation: Check naming conflicts
├─ Rule: "Model names must be unique"
├─ Check: "purchase.request" already exists?
├─ Result: ❌ Conflict detected
└─ Suggestion: "Use different name or extend existing"
```

---

### Spoke 5: Incremental Refinement 🔄
**What:** Build in rounds (skeleton → core → polish)

**Models:**
- `itx.ai.refinement.round` - Refinement rounds
- `itx.ai.refinement.feedback` - Feedback per round

**Example:**
```python
Round 1: Skeleton
├─ Generate basic structure
├─ User review: "Add budget control"
└─ Next: Round 2

Round 2: Core
├─ Add budget features
├─ User review: "Add email notifications"
└─ Next: Round 3

Round 3: Polish
├─ Add email templates
├─ User review: "Looks good!"
└─ Status: Complete
```

---

### Spoke 6: Why Tracking 🔍
**What:** Capture rationale for all decisions

**Models:**
- `itx.ai.why.entry` - Why entries
- `itx.ai.why.link` - Link to decisions/requirements

**Example:**
```python
Why: "Why use state field instead of boolean flags?"
├─ Reason: "More maintainable and scalable"
├─ Reason: "Odoo best practice for workflows"
├─ Linked to: Decision #42 "State machine pattern"
└─ Linked to: Requirement v2.0 "Approval workflow"
```

---

### Spoke 7: Assumption Checking 🤔
**What:** Ask before assuming, confirm interpretations

**Models:**
- `itx.ai.assumption` - Assumptions made
- `itx.ai.assumption.confirmation` - User confirmations

**Example:**
```python
AI: "ผมเข้าใจว่า Manager คือ department.manager_id ใช่ไหม?"
├─ Assumption: "Manager from department"
├─ Alternative: "Manager from user profile"
├─ User confirms: "Yes, from department"
└─ Status: Confirmed
```

---

### Spoke 8: Conflict Resolution ⚔️
**What:** Detect conflicts and suggest resolutions

**Models:**
- `itx.ai.conflict` - Detected conflicts
- `itx.ai.conflict.resolution` - Proposed resolutions

**Example:**
```python
Conflict: Naming conflict
├─ Item 1: Model "purchase.request" (existing)
├─ Item 2: New model "purchase.request" (proposed)
├─ Type: Naming conflict
├─ Resolution 1: "Rename new model to 'custom.purchase.request'"
├─ Resolution 2: "Extend existing model instead"
├─ User chooses: Resolution 2
└─ Status: Resolved
```

---

### Spoke 9: Progress Awareness 📊
**What:** Always know current state, completion %

**Models:**
- `itx.ai.progress` - Progress tracking
- `itx.ai.progress.milestone` - Milestones

**Example:**
```python
Progress: Requirements Phase
├─ Total steps: 5
├─ Completed: 3
├─ Current: Step 4 (Collect answers)
├─ Remaining: 1
├─ Completion: 80%
└─ Next milestone: Freeze requirements
```

---

### Spoke 10: Rollback & Iteration 🔙
**What:** Safe rollback, iterate on decisions

**Models:**
- `itx.ai.snapshot` - State snapshots
- `itx.ai.rollback.point` - Rollback points

**Example:**
```python
Rollback Point: Before adding catering feature
├─ State snapshot: v1.0 (3 models, 20 fields)
├─ User: "ทดลองเพิ่ม catering"
├─ After: v1.1 (4 models, 25 fields)
├─ User: "ไม่เอา catering แล้ว"
├─ Rollback to: v1.0
└─ Status: Rolled back
```

---

## 📊 Core Data Models

### AI Project & Sessions
```python
class AiProject(models.Model):
    """AI-Assisted Project (Domain-agnostic)"""
    _name = 'itx.ai.project'
    _description = 'AI Project'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Project Name', required=True, tracking=True)

    # Domain
    domain_type = fields.Selection(
        selection='_get_domain_types',
        string='Domain',
        required=True,
    )
    domain_data = fields.Serialized('Domain Data')

    # Versions
    requirements_version_ids = fields.One2many(
        'itx.ai.requirements.version',
        'project_id',
    )
    design_version_ids = fields.One2many(
        'itx.ai.design.version',
        'project_id',
    )

    current_requirements_version_id = fields.Many2one(
        'itx.ai.requirements.version',
        string='Current Requirements',
    )
    current_design_version_id = fields.Many2one(
        'itx.ai.design.version',
        string='Current Design',
    )

    # Sessions
    session_ids = fields.One2many('itx.ai.session', 'project_id')

    # Progress
    progress = fields.Float('Progress %', compute='_compute_progress')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('requirements', 'Requirements Gathering'),
        ('design', 'Design'),
        ('implementation', 'Implementation'),
        ('done', 'Done'),
    ], default='draft', tracking=True)

    @api.model
    def _get_domain_types(self):
        """Get available domains from plugins"""
        domains = []
        # Scan for domain plugins
        for model_name in self.env:
            if model_name.startswith('itx.ai.domain.'):
                model = self.env[model_name]
                if hasattr(model, 'get_domain_name'):
                    domain_id = model_name.replace('itx.ai.domain.', '')
                    domain_name = model.get_domain_name()
                    domains.append((domain_id, domain_name))
        return domains


class AiSession(models.Model):
    """Conversation Session"""
    _name = 'itx.ai.session'
    _description = 'AI Conversation Session'
    _order = 'create_date desc'

    name = fields.Char('Session Name', compute='_compute_name', store=True)
    project_id = fields.Many2one('itx.ai.project', required=True, ondelete='cascade')

    # Messages
    message_ids = fields.One2many('itx.ai.message', 'session_id')
    message_count = fields.Integer(compute='_compute_message_count')

    # Context
    context_ids = fields.One2many('itx.ai.context', 'session_id')

    # State
    state = fields.Selection([
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
    ], default='active')

    @api.depends('create_date', 'project_id.name')
    def _compute_name(self):
        for session in self:
            session.name = f"{session.project_id.name} - {session.create_date}"


class AiMessage(models.Model):
    """Chat Message"""
    _name = 'itx.ai.message'
    _description = 'AI Chat Message'
    _order = 'create_date asc'

    session_id = fields.Many2one('itx.ai.session', required=True, ondelete='cascade')

    role = fields.Selection([
        ('user', 'User'),
        ('assistant', 'AI Assistant'),
        ('system', 'System'),
    ], required=True)

    content = fields.Text('Message Content', required=True)

    # Metadata
    tokens_used = fields.Integer('Tokens Used')
    cost = fields.Float('Cost (USD)')
    response_time = fields.Float('Response Time (seconds)')

    # Attachments (if any)
    attachment_ids = fields.Many2many('ir.attachment')
```

---

### Context Management
```python
class AiContext(models.Model):
    """Conversation Context"""
    _name = 'itx.ai.context'
    _description = 'AI Context'

    session_id = fields.Many2one('itx.ai.session', required=True, ondelete='cascade')

    # Context snapshot
    context_type = fields.Selection([
        ('project', 'Project Context'),
        ('requirements', 'Requirements Context'),
        ('design', 'Design Context'),
        ('domain', 'Domain Knowledge'),
        ('conversation', 'Conversation History'),
    ], required=True)

    context_data = fields.Serialized('Context Data')

    # Version
    version = fields.Integer('Version', default=1)
    active_version = fields.Boolean('Active Version', default=True)


class AiContextItem(models.Model):
    """Individual Context Item"""
    _name = 'itx.ai.context.item'
    _description = 'AI Context Item'

    context_id = fields.Many2one('itx.ai.context', required=True, ondelete='cascade')

    key = fields.Char('Key', required=True)
    value = fields.Text('Value')
    data_type = fields.Selection([
        ('string', 'String'),
        ('integer', 'Integer'),
        ('float', 'Float'),
        ('boolean', 'Boolean'),
        ('json', 'JSON'),
    ], required=True)
```

---

### Decision & Why Tracking
```python
class AiDecision(models.Model):
    """AI Decision Log"""
    _name = 'itx.ai.decision'
    _description = 'AI Decision'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    project_id = fields.Many2one('itx.ai.project', required=True, ondelete='cascade')
    session_id = fields.Many2one('itx.ai.session', ondelete='set null')

    name = fields.Char('Decision', required=True, tracking=True)
    description = fields.Text('Description')

    # Why tracking
    reason_ids = fields.One2many('itx.ai.decision.reason', 'decision_id')

    # Impact tracking
    impact_ids = fields.One2many('itx.ai.decision.impact', 'decision_id')

    # Alternatives
    alternative_ids = fields.One2many('itx.ai.decision.alternative', 'decision_id')

    # Status
    status = fields.Selection([
        ('proposed', 'Proposed'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ], default='proposed', tracking=True)

    made_by = fields.Many2one('res.users', default=lambda self: self.env.user)
    made_date = fields.Datetime(default=fields.Datetime.now)


class AiDecisionReason(models.Model):
    """Decision Reason (Why)"""
    _name = 'itx.ai.decision.reason'
    _description = 'Decision Reason'

    decision_id = fields.Many2one('itx.ai.decision', required=True, ondelete='cascade')
    reason = fields.Text('Reason', required=True)
    sequence = fields.Integer('Sequence')


class AiDecisionImpact(models.Model):
    """Decision Impact (What affected)"""
    _name = 'itx.ai.decision.impact'
    _description = 'Decision Impact'

    decision_id = fields.Many2one('itx.ai.decision', required=True, ondelete='cascade')

    impact_type = fields.Selection([
        ('model', 'Model'),
        ('field', 'Field'),
        ('view', 'View'),
        ('security', 'Security'),
        ('other', 'Other'),
    ], required=True)

    impact_description = fields.Text('Impact Description', required=True)
    severity = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ])


class AiDecisionAlternative(models.Model):
    """Alternative Solutions"""
    _name = 'itx.ai.decision.alternative'
    _description = 'Decision Alternative'

    decision_id = fields.Many2one('itx.ai.decision', required=True, ondelete='cascade')

    name = fields.Char('Alternative', required=True)
    description = fields.Text('Description')
    pros = fields.Text('Pros')
    cons = fields.Text('Cons')
    rejected_reason = fields.Text('Why Rejected')
```

---

### Requirements & Design Versions
```python
class AiRequirementsVersion(models.Model):
    """Requirements Version"""
    _name = 'itx.ai.requirements.version'
    _description = 'Requirements Version'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char('Version', required=True)  # v1.0, v1.1, v2.0
    project_id = fields.Many2one('itx.ai.project', required=True, ondelete='cascade')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('review', 'Under Review'),
        ('frozen', 'Frozen'),
    ], default='draft', tracking=True)

    frozen_date = fields.Datetime('Frozen Date', tracking=True)
    frozen_by = fields.Many2one('res.users', tracking=True)

    # Snapshot of requirements
    feature_ids = fields.One2many('itx.ai.requirements.feature', 'version_id')

    # Change tracking
    parent_version_id = fields.Many2one('itx.ai.requirements.version', 'Previous Version')
    change_summary = fields.Text('Change Summary')

    # Impact metrics
    models_count = fields.Integer('Models Count', compute='_compute_metrics')
    fields_count = fields.Integer('Fields Count', compute='_compute_metrics')
    effort_hours = fields.Float('Estimated Effort (hours)')

    # Notes
    notes = fields.Html('Notes')


class AiRequirementsFeature(models.Model):
    """Requirements Feature"""
    _name = 'itx.ai.requirements.feature'
    _description = 'Requirements Feature'

    version_id = fields.Many2one('itx.ai.requirements.version', required=True, ondelete='cascade')

    name = fields.Char('Feature Name', required=True)
    description = fields.Text('Description')

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

    # Design impact (domain-specific)
    design_impact = fields.Text('Design Impact')


class AiDesignVersion(models.Model):
    """Design Document Version"""
    _name = 'itx.ai.design.version'
    _description = 'Design Version'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char('Version', required=True)  # d1.0, d1.1, d2.0
    project_id = fields.Many2one('itx.ai.project', required=True, ondelete='cascade')

    requirements_version_id = fields.Many2one(
        'itx.ai.requirements.version',
        string='Based on Requirements',
        domain="[('project_id', '=', project_id), ('state', '=', 'frozen')]",
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('review', 'Under Review'),
        ('frozen', 'Frozen'),
    ], default='draft', tracking=True)

    # Design document sections (domain-specific)
    architecture_doc = fields.Html('Architecture')
    models_doc = fields.Html('Data Models')
    business_logic_doc = fields.Html('Business Logic')
    ui_doc = fields.Html('UI Design')
    security_doc = fields.Html('Security')
    automation_doc = fields.Html('Automation')

    # Completeness & Review
    completeness = fields.Float('Completeness %', compute='_compute_completeness')
    review_notes = fields.Html('Review Notes')
    ai_suggestions = fields.Html('AI Suggestions')
```

---

### Validation & Conflicts
```python
class AiValidationRule(models.Model):
    """Validation Rule"""
    _name = 'itx.ai.validation.rule'
    _description = 'Validation Rule'

    name = fields.Char('Rule Name', required=True)
    description = fields.Text('Description')

    rule_type = fields.Selection([
        ('naming', 'Naming Convention'),
        ('structure', 'Structure'),
        ('security', 'Security'),
        ('performance', 'Performance'),
        ('best_practice', 'Best Practice'),
    ], required=True)

    domain = fields.Char('Domain Filter')  # Which domain this applies to

    # Rule logic (could be Python code or JSON)
    rule_logic = fields.Text('Rule Logic')

    severity = fields.Selection([
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('critical', 'Critical'),
    ], default='warning')

    active = fields.Boolean(default=True)


class AiValidationResult(models.Model):
    """Validation Result"""
    _name = 'itx.ai.validation.result'
    _description = 'Validation Result'

    project_id = fields.Many2one('itx.ai.project', required=True, ondelete='cascade')
    rule_id = fields.Many2one('itx.ai.validation.rule', required=True)

    status = fields.Selection([
        ('pass', 'Passed'),
        ('fail', 'Failed'),
        ('skip', 'Skipped'),
    ], required=True)

    message = fields.Text('Message')
    details = fields.Text('Details')

    # Actions
    suggestion = fields.Text('Suggested Fix')
    auto_fixable = fields.Boolean('Can Auto-Fix')


class AiConflict(models.Model):
    """Detected Conflict"""
    _name = 'itx.ai.conflict'
    _description = 'AI Conflict'
    _inherit = ['mail.thread']

    project_id = fields.Many2one('itx.ai.project', required=True, ondelete='cascade')

    name = fields.Char('Conflict', required=True, tracking=True)
    description = fields.Text('Description')

    conflict_type = fields.Selection([
        ('naming', 'Naming Conflict'),
        ('structure', 'Structure Conflict'),
        ('logic', 'Logic Conflict'),
        ('requirement', 'Requirement Conflict'),
    ], required=True)

    # Conflicting items
    item1 = fields.Text('Item 1')
    item2 = fields.Text('Item 2')

    # Resolutions
    resolution_ids = fields.One2many('itx.ai.conflict.resolution', 'conflict_id')

    # Status
    status = fields.Selection([
        ('open', 'Open'),
        ('resolved', 'Resolved'),
        ('ignored', 'Ignored'),
    ], default='open', tracking=True)

    resolved_by = fields.Many2one('res.users')
    resolved_date = fields.Datetime()


class AiConflictResolution(models.Model):
    """Conflict Resolution Option"""
    _name = 'itx.ai.conflict.resolution'
    _description = 'Conflict Resolution'

    conflict_id = fields.Many2one('itx.ai.conflict', required=True, ondelete='cascade')

    name = fields.Char('Resolution', required=True)
    description = fields.Text('Description')

    impact = fields.Text('Impact if Applied')

    selected = fields.Boolean('Selected')
```

---

## 🔌 Domain Plugin System

### Abstract Domain Class
```python
class AiDomainAbstract(models.AbstractModel):
    """Abstract class for domain plugins"""
    _name = 'itx.ai.domain.abstract'
    _description = 'AI Domain Plugin (Abstract)'

    @api.model
    def get_domain_name(self):
        """Return domain display name"""
        raise NotImplementedError("Domain must implement get_domain_name()")

    @api.model
    def get_domain_description(self):
        """Return domain description"""
        return ""

    @api.model
    def get_knowledge_base(self):
        """
        Return domain-specific knowledge

        Returns:
            dict: {
                'patterns': [...],
                'best_practices': [...],
                'common_pitfalls': [...],
                'elements': [...],
                ...
            }
        """
        raise NotImplementedError("Domain must implement get_knowledge_base()")

    @api.model
    def generate_questionnaire(self, project):
        """
        Generate domain-specific questionnaire

        Args:
            project: itx.ai.project recordset

        Returns:
            dict: {
                'sections': [
                    {
                        'name': 'Section Name',
                        'questions': ['Q1', 'Q2', ...],
                    },
                    ...
                ],
            }
        """
        raise NotImplementedError("Domain must implement generate_questionnaire()")

    @api.model
    def analyze_requirements(self, requirements_text):
        """
        Analyze requirements with domain knowledge

        Args:
            requirements_text: str

        Returns:
            dict: {
                'suggested_patterns': [...],
                'suggested_models': [...],
                'best_practices': [...],
                'warnings': [...],
            }
        """
        return {}

    @api.model
    def generate_design(self, requirements_version):
        """
        Generate design from requirements

        Args:
            requirements_version: itx.ai.requirements.version recordset

        Returns:
            dict: Domain-specific design structure
        """
        return {}

    @api.model
    def validate_design(self, design_version):
        """
        Validate design with domain knowledge

        Args:
            design_version: itx.ai.design.version recordset

        Returns:
            list: [
                {
                    'type': 'error' / 'warning' / 'info',
                    'message': '...',
                    'suggestion': '...',
                },
                ...
            ]
        """
        return []

    @api.model
    def get_context_for_ai(self, project):
        """
        Build domain-specific context for AI

        Args:
            project: itx.ai.project recordset

        Returns:
            dict: Context to send to AI
        """
        return {
            'domain': self.get_domain_name(),
            'knowledge': self.get_knowledge_base(),
        }
```

---

## ⚙️ Core Services

### Conversation Manager
```python
# services/conversation_manager.py

class ConversationManager:
    """Manages AI conversations"""

    def __init__(self, env):
        self.env = env
        self.claude_client = ClaudeAPIClient(env)
        self.context_builder = ContextBuilder(env)
        self.response_parser = ResponseParser(env)
        self.validator = ValidationEngine(env)

    def process_user_message(self, session, message_content):
        """
        Process user message and get AI response

        Steps:
        1. Add user message to history
        2. Build context
        3. Get current state
        4. Build Claude prompt
        5. Call Claude API
        6. Parse response
        7. Validate actions
        8. Handle validation
        9. Execute actions
        10. Update state
        11. Add AI response to history
        """

        # 1. Add user message
        user_msg = self.env['itx.ai.message'].create({
            'session_id': session.id,
            'role': 'user',
            'content': message_content,
        })

        # 2. Build context
        context = self.context_builder.build_context(session)

        # 3. Get current state
        state = self._get_conversation_state(session)

        # 4. Build Claude prompt
        system_prompt = self._build_system_prompt(session, context, state)
        messages = self._build_message_history(session)

        # 5. Call Claude API
        response = self.claude_client.send_message(
            system_prompt=system_prompt,
            messages=messages,
            context=context,
        )

        # 6. Parse response
        parsed = self.response_parser.parse(response)

        # 7. Validate actions
        validation_results = self.validator.validate(parsed['actions'])

        # 8. Handle validation
        if validation_results['has_errors']:
            # Ask AI to fix
            return self._handle_validation_errors(session, validation_results)

        # 9. Execute actions
        self._execute_actions(session, parsed['actions'])

        # 10. Update state
        self._update_state(session, parsed['new_state'])

        # 11. Add AI response
        ai_msg = self.env['itx.ai.message'].create({
            'session_id': session.id,
            'role': 'assistant',
            'content': parsed['message'],
            'tokens_used': response.get('usage', {}).get('total_tokens'),
            'cost': self._calculate_cost(response),
        })

        return {
            'message': parsed['message'],
            'actions': parsed['actions'],
            'state': parsed['new_state'],
        }
```

---

### Claude API Client
```python
# services/claude_api_client.py

import anthropic

class ClaudeAPIClient:
    """Claude API integration"""

    def __init__(self, env):
        self.env = env
        api_key = self.env['ir.config_parameter'].sudo().get_param('itx.ai.claude.api_key')
        self.client = anthropic.Anthropic(api_key=api_key)

    def send_message(self, system_prompt, messages, context=None, model='claude-sonnet-4.5-20250929'):
        """
        Send message to Claude API

        Args:
            system_prompt: str - System prompt
            messages: list - Message history
            context: dict - Additional context
            model: str - Model to use

        Returns:
            dict: Claude API response
        """

        # Build messages for Claude API
        api_messages = []
        for msg in messages:
            api_messages.append({
                'role': msg['role'],
                'content': msg['content'],
            })

        # Call API
        response = self.client.messages.create(
            model=model,
            max_tokens=8192,
            temperature=0.3,  # Lower temperature for consistency
            system=system_prompt,
            messages=api_messages,
        )

        return {
            'content': response.content[0].text,
            'usage': {
                'input_tokens': response.usage.input_tokens,
                'output_tokens': response.usage.output_tokens,
                'total_tokens': response.usage.input_tokens + response.usage.output_tokens,
            },
            'model': response.model,
            'stop_reason': response.stop_reason,
        }
```

---

### Context Builder
```python
# services/context_builder.py

class ContextBuilder:
    """Builds context for AI"""

    def __init__(self, env):
        self.env = env

    def build_context(self, session):
        """
        Build complete context for AI

        Returns:
            dict: {
                'project': {...},
                'requirements': {...},
                'design': {...},
                'domain': {...},
                'conversation': {...},
                'decisions': [...],
            }
        """

        project = session.project_id

        context = {
            'project': self._build_project_context(project),
            'domain': self._build_domain_context(project),
        }

        # Add requirements context if exists
        if project.current_requirements_version_id:
            context['requirements'] = self._build_requirements_context(
                project.current_requirements_version_id
            )

        # Add design context if exists
        if project.current_design_version_id:
            context['design'] = self._build_design_context(
                project.current_design_version_id
            )

        # Add conversation history
        context['conversation'] = self._build_conversation_context(session)

        # Add decisions
        context['decisions'] = self._build_decisions_context(project)

        return context

    def _build_domain_context(self, project):
        """Build domain-specific context"""
        domain_model_name = f'itx.ai.domain.{project.domain_type}'

        if domain_model_name not in self.env:
            return {}

        domain_model = self.env[domain_model_name]
        return domain_model.get_context_for_ai(project)
```

---

## 🎨 UI Components

### Chat Widget (OWL Component)
```javascript
// static/src/components/chat_widget/chat_widget.js

import { Component, useState, useRef, onMounted } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class AiChatWidget extends Component {
    setup() {
        this.rpc = useService("rpc");
        this.state = useState({
            messages: [],
            inputText: "",
            isTyping: false,
        });
        this.chatContainer = useRef("chatContainer");

        onMounted(() => {
            this.loadMessages();
        });
    }

    async loadMessages() {
        const messages = await this.rpc("/itx_ai_steerer/chat/messages", {
            session_id: this.props.sessionId,
        });
        this.state.messages = messages;
        this.scrollToBottom();
    }

    async sendMessage() {
        if (!this.state.inputText.trim()) return;

        const userMessage = this.state.inputText;
        this.state.inputText = "";

        // Add user message immediately
        this.state.messages.push({
            role: "user",
            content: userMessage,
        });
        this.scrollToBottom();

        // Show typing indicator
        this.state.isTyping = true;

        try {
            // Send to AI
            const response = await this.rpc("/itx_ai_steerer/chat/send", {
                session_id: this.props.sessionId,
                message: userMessage,
            });

            // Add AI response
            this.state.messages.push({
                role: "assistant",
                content: response.message,
            });

        } catch (error) {
            console.error("Failed to send message:", error);
        } finally {
            this.state.isTyping = false;
            this.scrollToBottom();
        }
    }

    scrollToBottom() {
        if (this.chatContainer.el) {
            this.chatContainer.el.scrollTop = this.chatContainer.el.scrollHeight;
        }
    }
}

AiChatWidget.template = "itx_ai_steerer.ChatWidget";
AiChatWidget.props = {
    sessionId: Number,
};
```

---

## 🎯 Use Cases & Examples

### Example 1: Odoo Module Development
```python
# Domain plugin: itx_moduler

from odoo import models, api

class OdooDevelopmentDomain(models.AbstractModel):
    _name = 'itx.ai.domain.odoo'
    _inherit = 'itx.ai.domain.abstract'

    @api.model
    def get_domain_name(self):
        return 'Odoo Module Development'

    @api.model
    def get_knowledge_base(self):
        return {
            'framework': 'Odoo 19.0',
            'patterns': [
                'State Machine Pattern',
                'Chatter Pattern (mail.thread)',
                'Sequence Pattern',
                'Approval Pattern (mail.activity)',
            ],
            'best_practices': [
                'Use ORM instead of direct SQL',
                'Add @api.depends on computed fields',
                'Use proper ondelete on Many2one fields',
                'Add tracking on important fields',
            ],
            'common_pitfalls': [
                'SQL Injection via search domains',
                'N+1 queries in loops',
                'Missing ACLs on models',
                'Forgetting @api.constrains validation',
            ],
        }
```

---

### Example 2: Audio Circuit Design
```python
# Domain plugin: itx_audio_circuit

class AudioCircuitDomain(models.AbstractModel):
    _name = 'itx.ai.domain.audio'
    _inherit = 'itx.ai.domain.abstract'

    @api.model
    def get_domain_name(self):
        return 'Audio Circuit Design'

    @api.model
    def get_knowledge_base(self):
        return {
            'components': [
                'Op-Amp (Operational Amplifier)',
                'Transistor (BJT, MOSFET)',
                'Capacitor (Electrolytic, Ceramic)',
                'Resistor',
                'Transformer',
            ],
            'patterns': [
                'Common Emitter Amplifier',
                'Differential Amplifier',
                'Power Supply (Linear, Switching)',
                'Tone Control Circuit',
            ],
            'best_practices': [
                'Use decoupling capacitors on power rails',
                'Proper grounding (star ground)',
                'Consider signal-to-noise ratio (SNR)',
                'Heat dissipation for power components',
            ],
            'calculations': [
                'Gain calculation: Av = -Rf/Rin',
                'Cutoff frequency: fc = 1/(2πRC)',
                'Power dissipation: P = V²/R',
            ],
        }

    @api.model
    def generate_questionnaire(self, project):
        return {
            'sections': [
                {
                    'name': 'Amplifier Requirements',
                    'questions': [
                        'Output power needed (Watts)?',
                        'Input impedance (Ohms)?',
                        'Frequency response (Hz)?',
                        'THD (Total Harmonic Distortion) requirement?',
                    ],
                },
                {
                    'name': 'Power Supply',
                    'questions': [
                        'Input voltage (AC/DC)?',
                        'Output voltages needed?',
                        'Current requirements (Amps)?',
                    ],
                },
            ],
        }
```

---

## 📅 Implementation Roadmap

### Phase 1: Core Foundation (Weeks 1-4) 🔴

**Week 1-2: Basic Structure**
- ✅ Core models (Project, Session, Message, Context)
- ✅ Domain abstract class
- ✅ Claude API integration
- ✅ Basic conversation flow

**Week 3-4: Version Control**
- ✅ Requirements versioning
- ✅ Design versioning
- ✅ Change tracking
- ✅ Impact analysis framework

---

### Phase 2: The 10 Spokes (Weeks 5-8) 🟡

**Week 5-6: Memory & Tracking**
- ✅ Spoke 1: Context Memory (Log Book) ⭐ MOST IMPORTANT
- ✅ Spoke 2: Decision Log
- ✅ Spoke 6: Why Tracking

**Week 7-8: Validation & Refinement**
- ✅ Spoke 4: Constraint Validation
- ✅ Spoke 5: Incremental Refinement
- ✅ Spoke 8: Conflict Resolution

---

### Phase 3: Advanced Features (Weeks 9-12) 🟡

**Week 9-10: Conversation Management**
- ✅ Spoke 3: Guided Conversation
- ✅ Spoke 7: Assumption Checking
- ✅ Spoke 9: Progress Awareness

**Week 11-12: Safety & Iteration**
- ✅ Spoke 10: Rollback & Iteration
- ✅ State snapshots
- ✅ Safe rollback mechanism

---

### Phase 4: UI & UX (Weeks 13-16) 🟢

**Week 13-14: Core UI**
- ✅ Chat widget (OWL component)
- ✅ Timeline view
- ✅ Diff viewer

**Week 15-16: Advanced UI**
- ✅ Impact dashboard
- ✅ Progress visualization
- ✅ Context panel

---

### Phase 5: Testing & Polish (Weeks 17-18) 🟢

**Week 17: Testing**
- ✅ Unit tests
- ✅ Integration tests
- ✅ End-to-end scenarios

**Week 18: Documentation**
- ✅ API documentation
- ✅ Domain plugin guide
- ✅ User manual

---

## 💰 Cost Estimation

### Development Cost
```
18 weeks × 1 developer = ~4.5 months
```

### Operational Cost (Claude API)
```
Per Message:
- Input: ~2,000 tokens (context)
- Output: ~500 tokens (response)
- Total: ~2,500 tokens
- Cost: ~$0.03 per message

Per Project (estimated):
- Requirements phase: ~20 messages
- Design phase: ~30 messages
- Total: ~50 messages
- Cost: ~$1.50 per project

Per Month (estimated):
- 100 projects/month
- Cost: ~$150/month
```

---

## 🎯 Success Criteria

### For Framework:
- ✅ All 10 Spokes working
- ✅ Domain plugin system functional
- ✅ Claude API integration stable
- ✅ Version control working
- ✅ UI components responsive

### For Domain Plugins:
- ✅ Easy to create new domain
- ✅ Clear API documentation
- ✅ Example domains working (Odoo, Audio, Camping)

### For Users:
- ✅ Intuitive conversation flow
- ✅ AI provides helpful guidance
- ✅ Requirements/Design quality improved
- ✅ Time saved vs manual work

---

## 📚 Related Documents

- [REQUIREMENTS_MANAGEMENT_VISION.md](./REQUIREMENTS_MANAGEMENT_VISION.md) - Requirements workflow
- [DESIGN_DOCUMENT_VISION.md](./DESIGN_DOCUMENT_VISION.md) - Design doc workflow
- [AI_CONVERSATION_MANAGEMENT.md](../04-Integration/AI_CONVERSATION_MANAGEMENT.md) - The 10 Spokes detail
- [SPOKE_1_CONTEXT_MEMORY_DESIGN.md](./SPOKE_1_CONTEXT_MEMORY_DESIGN.md) - Spoke 1 (Context Memory / Log Book) design
- [AI_TECHNICAL_IMPLEMENTATION.md](../04-Integration/AI_TECHNICAL_IMPLEMENTATION.md) - Technical specs
- [IMPLEMENTATION_ROADMAP.md](./IMPLEMENTATION_ROADMAP.md) - Overall roadmap

---

## 🚀 Next Steps

1. **Review Vision** - Confirm approach
2. **Refine Domain API** - Finalize abstract methods
3. **Prototype Core** - Build proof of concept
4. **Create First Domain** - Odoo development domain
5. **Iterate & Improve** - Based on feedback

---

**Status:** Vision Complete - Spoke 1 Designed - Ready for Implementation
**Module Name:** `itx_ai_helm`
**Dependencies:** `base`, `mail`
**License:** Proprietary (or as decided)

---

*Created: 2025-12-27*
*Updated: 2025-12-29 (Renamed from itx_ai_steerer to itx_ai_helm)*
*Type: Vision & Architecture Document*
*Version: 2.0.0*
