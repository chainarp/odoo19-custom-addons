# AI Technical Implementation Strategy

**Date:** 2025-12-26
**Purpose:** How to build ITX Moduler addon to support 10 AI Conversation Capabilities
**Status:** Technical Design

---

## 🏗️ Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│                    User Interface                         │
│  (Chat Widget, Wizard Forms, Progress Dashboard)         │
└────────────────┬─────────────────────────────────────────┘
                 │
┌────────────────▼─────────────────────────────────────────┐
│              Conversation Manager                         │
│  (State Machine, Context Builder, Validation Engine)     │
└────────────────┬─────────────────────────────────────────┘
                 │
┌────────────────▼─────────────────────────────────────────┐
│                Claude API Client                          │
│  (Prompt Builder, Response Parser, Error Handler)        │
└────────────────┬─────────────────────────────────────────┘
                 │
┌────────────────▼─────────────────────────────────────────┐
│               Data Models (Odoo)                          │
│  (Project, Session, Message, Decision, Progress, etc.)   │
└──────────────────────────────────────────────────────────┘
```

---

## 📦 Required Odoo Models

### 1. Core Models

#### `itx.moduler.ai.project`
```python
"""Represents a module development project"""
class AIProject(models.Model):
    _name = 'itx.moduler.ai.project'

    # Basic Info
    name = fields.Char('Project Name', required=True)  # e.g., "conference_booking"
    description = fields.Text('Description')  # "ระบบจองห้องประชุม"
    target_version = fields.Selection([...], default='19.0')

    # Relationships
    module_id = fields.Many2one('itx.moduler.module')  # Link to workspace
    session_ids = fields.One2many('itx.moduler.ai.session', 'project_id')
    decision_ids = fields.One2many('itx.moduler.ai.decision', 'project_id')

    # Status
    state = fields.Selection([
        ('requirements', 'Requirements'),
        ('design', 'Design'),
        ('implementation', 'Implementation'),
        ('testing', 'Testing'),
        ('done', 'Done'),
    ])
    progress = fields.Float('Progress %', compute='_compute_progress')
```

#### `itx.moduler.ai.session`
```python
"""Represents a conversation session"""
class AISession(models.Model):
    _name = 'itx.moduler.ai.session'

    # Session Info
    name = fields.Char('Session Name', default='New Session')
    project_id = fields.Many2one('itx.moduler.ai.project', required=True)
    start_date = fields.Datetime('Started', default=fields.Datetime.now)
    end_date = fields.Datetime('Ended')

    # Conversation
    message_ids = fields.One2many('itx.moduler.ai.message', 'session_id')
    context_ids = fields.One2many('itx.moduler.ai.context', 'session_id')

    # Current State
    current_step = fields.Char('Current Step')  # "defining_fields"
    current_round = fields.Integer('Current Round', default=1)  # 1=skeleton, 2=core, 3=polish

    # Context Snapshot (JSON)
    context_snapshot = fields.Json('Context Snapshot')
    """
    {
        "models": ["conference.room", "conference.booking"],
        "current_model": "conference.booking",
        "current_focus": "defining_fields",
        "decisions": [...],
        "assumptions": [...]
    }
    """
```

#### `itx.moduler.ai.message`
```python
"""Represents a single message in conversation"""
class AIMessage(models.Model):
    _name = 'itx.moduler.ai.message'
    _order = 'sequence, create_date'

    session_id = fields.Many2one('itx.moduler.ai.session', required=True)
    sequence = fields.Integer('Sequence')

    # Message
    role = fields.Selection([
        ('user', 'User'),
        ('assistant', 'AI'),
        ('system', 'System'),
    ], required=True)
    content = fields.Text('Content', required=True)

    # Metadata
    tokens_used = fields.Integer('Tokens')
    response_time = fields.Float('Response Time (s)')

    # Context at this point
    context_at_message = fields.Json('Context Snapshot')
```

---

### 2. Context & Memory Models

#### `itx.moduler.ai.context`
```python
"""Stores context elements (Capability #1: Context Memory)"""
class AIContext(models.Model):
    _name = 'itx.moduler.ai.context'

    session_id = fields.Many2one('itx.moduler.ai.session', required=True)

    # Context Type
    context_type = fields.Selection([
        ('project_info', 'Project Information'),
        ('model_definition', 'Model Definition'),
        ('field_definition', 'Field Definition'),
        ('relation', 'Relation'),
        ('decision', 'Decision'),
        ('assumption', 'Assumption'),
    ], required=True)

    # Content
    key = fields.Char('Key', required=True)  # e.g., "models.conference.room.name"
    value = fields.Json('Value')  # Structured data

    # Tracking
    active = fields.Boolean('Active', default=True)
    created_at = fields.Datetime('Created', default=fields.Datetime.now)
    updated_at = fields.Datetime('Updated', default=fields.Datetime.now)
```

Example context entries:
```python
# Project info
{
    "context_type": "project_info",
    "key": "project.name",
    "value": "conference_booking"
}

# Model definition
{
    "context_type": "model_definition",
    "key": "models.conference.booking",
    "value": {
        "name": "conference.booking",
        "description": "Conference Room Booking",
        "inherit": ["mail.thread", "mail.activity.mixin"],
        "fields": {...}
    }
}
```

#### `itx.moduler.ai.decision`
```python
"""Stores decisions and reasons (Capability #2: Decision Log)"""
class AIDecision(models.Model):
    _name = 'itx.moduler.ai.decision'
    _order = 'decision_number'

    project_id = fields.Many2one('itx.moduler.ai.project', required=True)
    decision_number = fields.Integer('Decision #', required=True)

    # Decision
    title = fields.Char('Title', required=True)  # "Use mail.thread mixin"
    description = fields.Text('Description')
    status = fields.Selection([
        ('proposed', 'Proposed'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('superseded', 'Superseded'),
    ], default='proposed')

    # Reasoning (Capability #6: Why Tracking)
    reason_ids = fields.One2many('itx.moduler.ai.decision.reason', 'decision_id')

    # Impact (for rollback/conflict detection)
    impact_ids = fields.One2many('itx.moduler.ai.decision.impact', 'decision_id')

    # History
    decided_date = fields.Datetime('Decided')
    decided_by = fields.Many2one('res.users')
    superseded_by_id = fields.Many2one('itx.moduler.ai.decision', 'Superseded By')
```

#### `itx.moduler.ai.decision.reason`
```python
"""Why decisions were made (Capability #6: Why Tracking)"""
class AIDecisionReason(models.Model):
    _name = 'itx.moduler.ai.decision.reason'

    decision_id = fields.Many2one('itx.moduler.ai.decision', required=True)

    # Reason
    requirement_ref = fields.Char('Requirement Ref')  # "REQ-003"
    reason = fields.Text('Reason', required=True)
    impact = fields.Text('Impact')  # What this enables/affects
```

Example:
```python
Decision: "Use mail.thread"
Reasons:
  - Requirement REQ-003: "Need follower system"
    Impact: "Adds followers widget to views"
  - Requirement REQ-007: "Need activity tracking"
    Impact: "Enables reminder system"
```

#### `itx.moduler.ai.decision.impact`
```python
"""What will be affected by this decision"""
class AIDecisionImpact(models.Model):
    _name = 'itx.moduler.ai.decision.impact'

    decision_id = fields.Many2one('itx.moduler.ai.decision', required=True)

    # Impact
    affected_type = fields.Selection([
        ('model', 'Model'),
        ('field', 'Field'),
        ('view', 'View'),
        ('security', 'Security'),
    ])
    affected_ref = fields.Char('Reference')  # "conference.booking"
    impact_description = fields.Text('Impact')
```

---

### 3. Progress & Flow Models

#### `itx.moduler.ai.progress`
```python
"""Tracks progress (Capability #9: Progress Awareness)"""
class AIProgress(models.Model):
    _name = 'itx.moduler.ai.progress'

    project_id = fields.Many2one('itx.moduler.ai.project', required=True)

    # Phase
    phase = fields.Selection([
        ('requirements', 'Requirements'),
        ('design', 'Design'),
        ('implementation', 'Implementation'),
        ('testing', 'Testing'),
        ('documentation', 'Documentation'),
    ], required=True)

    # Sub-tasks
    task_ids = fields.One2many('itx.moduler.ai.progress.task', 'progress_id')

    # Progress
    progress = fields.Float('Progress %', compute='_compute_progress')
    status = fields.Selection([
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ])
```

#### `itx.moduler.ai.progress.task`
```python
"""Individual tasks within a phase"""
class AIProgressTask(models.Model):
    _name = 'itx.moduler.ai.progress.task'
    _order = 'sequence'

    progress_id = fields.Many2one('itx.moduler.ai.progress', required=True)
    sequence = fields.Integer('Sequence')

    # Task
    name = fields.Char('Task', required=True)
    description = fields.Text('Description')
    status = fields.Selection([
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('skipped', 'Skipped'),
    ], default='pending')

    # Dependencies
    depends_on_ids = fields.Many2many('itx.moduler.ai.progress.task',
                                       relation='ai_task_dependency_rel',
                                       column1='task_id',
                                       column2='depends_on_id',
                                       string='Depends On')

    # Blocking
    is_blocking = fields.Boolean('Blocking', compute='_compute_blocking')
    blocking_reason = fields.Char('Blocking Reason')
```

---

### 4. Validation & Conflict Models

#### `itx.moduler.ai.validation.rule`
```python
"""Validation rules (Capability #4: Constraint Validation)"""
class AIValidationRule(models.Model):
    _name = 'itx.moduler.ai.validation.rule'

    # Rule
    name = fields.Char('Rule Name', required=True)
    description = fields.Text('Description')
    rule_type = fields.Selection([
        ('data_model', 'Data Model'),
        ('odoo_best_practice', 'Odoo Best Practice'),
        ('design_consistency', 'Design Consistency'),
        ('security', 'Security'),
    ])

    # Code
    code = fields.Text('Python Code', required=True)
    """
    Python function that returns:
    {
        'valid': True/False,
        'message': 'Error message if invalid',
        'suggestion': 'How to fix'
    }
    """

    severity = fields.Selection([
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('blocker', 'Blocker'),
    ])
```

Example rule:
```python
def validate_no_duplicate_email(context):
    """Don't add email field if user.email exists"""
    if context.get('field_type') == 'Char' and 'email' in context.get('field_name', '').lower():
        model = context.get('model')
        if model.has_field('user_id'):
            return {
                'valid': False,
                'message': 'Email field redundant - user_id.email exists',
                'suggestion': 'Use user_id.email instead or explain why separate email needed'
            }
    return {'valid': True}
```

#### `itx.moduler.ai.conflict`
```python
"""Detected conflicts (Capability #8: Conflict Resolution)"""
class AIConflict(models.Model):
    _name = 'itx.moduler.ai.conflict'

    project_id = fields.Many2one('itx.moduler.ai.project', required=True)

    # Conflict
    conflict_type = fields.Selection([
        ('requirement', 'Requirement Conflict'),
        ('design', 'Design Conflict'),
        ('dependency', 'Dependency Conflict'),
    ])
    description = fields.Text('Description', required=True)

    # Involved
    element1_ref = fields.Char('Element 1')  # "Decision #3"
    element2_ref = fields.Char('Element 2')  # "Requirement #7"

    # Resolution
    status = fields.Selection([
        ('detected', 'Detected'),
        ('user_notified', 'User Notified'),
        ('resolved', 'Resolved'),
        ('ignored', 'Ignored'),
    ])
    resolution_ids = fields.One2many('itx.moduler.ai.conflict.resolution', 'conflict_id')
```

---

## 🔧 Core Services (Python Classes)

### 1. Conversation Manager

```python
class ConversationManager:
    """
    Manages conversation flow (Capability #3: Guided Conversation)
    """

    def __init__(self, session_id):
        self.session = env['itx.moduler.ai.session'].browse(session_id)
        self.project = self.session.project_id
        self.state_machine = ConversationStateMachine(self.project)

    def process_user_message(self, message):
        """Main entry point for user messages"""

        # 1. Add user message to history
        self._add_message('user', message)

        # 2. Build context for Claude
        context = self._build_context()

        # 3. Get current state and determine next action
        current_state = self.state_machine.current_state

        # 4. Build Claude prompt based on state
        prompt = self._build_prompt(message, context, current_state)

        # 5. Call Claude API
        response = self._call_claude_api(prompt, context)

        # 6. Parse response and extract actions
        actions = self._parse_response(response)

        # 7. Validate actions
        validation_results = self._validate_actions(actions)

        # 8. Handle validation (ask user if needed)
        if validation_results.has_issues():
            return self._handle_validation_issues(validation_results)

        # 9. Execute actions (update context, decisions, etc.)
        self._execute_actions(actions)

        # 10. Update state machine
        self.state_machine.transition(actions)

        # 11. Add AI response to history
        self._add_message('assistant', response)

        return response

    def _build_context(self):
        """Build context from all sources (Capability #1: Context Memory)"""
        return {
            'project': self._get_project_context(),
            'decisions': self._get_decisions_context(),
            'current_state': self._get_state_context(),
            'progress': self._get_progress_context(),
            'models': self._get_models_context(),
        }

    def _validate_actions(self, actions):
        """Validate proposed actions (Capability #4: Constraint Validation)"""
        validator = ActionValidator(self.project)
        return validator.validate_all(actions)
```

---

### 2. Claude API Client

```python
class ClaudeAPIClient:
    """
    Handles Claude API communication
    """

    def __init__(self, api_key):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-5-20251029"

    def send_message(self, system_prompt, messages, context):
        """
        Send message to Claude with proper context

        system_prompt: Instructions for Claude's role and behavior
        messages: Conversation history
        context: Current project context (for long context window)
        """

        # Build system prompt with context
        full_system_prompt = self._build_system_prompt(system_prompt, context)

        # Call API
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=full_system_prompt,
            messages=messages,
            temperature=0.3,  # Lower for more consistent code generation
        )

        return {
            'content': response.content[0].text,
            'tokens': {
                'input': response.usage.input_tokens,
                'output': response.usage.output_tokens,
            },
            'stop_reason': response.stop_reason,
        }

    def _build_system_prompt(self, base_prompt, context):
        """
        Build comprehensive system prompt
        """
        return f"""
{base_prompt}

# Current Project Context
{self._format_context(context)}

# Your Responsibilities
1. ALWAYS check decisions log before suggesting
2. ALWAYS validate against constraints
3. ALWAYS explain WHY you suggest something
4. ALWAYS ask before assuming
5. ALWAYS check for conflicts

# Response Format
Use structured JSON responses for easier parsing:
{{
    "understanding": "What I understood from user",
    "suggestions": [
        {{
            "type": "add_field",
            "data": {{...}},
            "reason": "Why this suggestion",
            "assumptions": ["What I'm assuming"]
        }}
    ],
    "questions": ["Clarification questions if any"],
    "warnings": ["Potential issues detected"],
    "next_step": "What to do next"
}}
"""
```

---

### 3. State Machine

```python
class ConversationStateMachine:
    """
    Manages conversation flow (Capability #3: Guided Conversation)
    """

    STATES = {
        'initial': {
            'question': "What kind of module do you want to create?",
            'next': ['requirements'],
        },
        'requirements': {
            'question': "What are the main requirements?",
            'sub_states': ['business', 'users', 'technical'],
            'next': ['design'],
        },
        'design': {
            'question': "Let's design the module structure",
            'sub_states': ['models', 'relations', 'architecture'],
            'next': ['implementation'],
        },
        'implementation': {
            'question': "Let's implement the module",
            'sub_states': ['models', 'fields', 'logic', 'views', 'security'],
            'next': ['testing', 'documentation'],
            'rounds': [
                {'name': 'skeleton', 'focus': 'basic structure'},
                {'name': 'core', 'focus': 'main features'},
                {'name': 'polish', 'focus': 'advanced features'},
            ],
        },
    }

    def __init__(self, project):
        self.project = project
        self.current_state = project.state or 'initial'
        self.current_sub_state = None
        self.current_round = project.session_ids[-1].current_round if project.session_ids else 1

    def get_next_question(self):
        """Get appropriate next question based on state"""
        state_config = self.STATES[self.current_state]

        if self.current_sub_state:
            # In sub-state, ask sub-question
            return self._get_sub_state_question()
        else:
            # Main state question
            return state_config['question']

    def transition(self, actions):
        """Transition to next state based on actions"""
        # Determine if current state is complete
        if self._is_state_complete():
            self.current_state = self._get_next_state()
            self.current_sub_state = None
        else:
            # Move to next sub-state
            self.current_sub_state = self._get_next_sub_state()
```

---

### 4. Prompt Builder

```python
class PromptBuilder:
    """
    Builds effective prompts for different scenarios
    """

    PROMPTS = {
        'design_assistant': """
You are an Odoo development expert helping design a module.

Your role:
- Suggest appropriate models, fields, relations
- Warn about common pitfalls
- Recommend best practices
- Explain WHY each suggestion

Current Context:
{context}

Recent Decisions:
{decisions}

User Message: {user_message}

Remember:
- Check decision log before suggesting
- Explain your reasoning
- Ask before assuming
- Warn about potential issues
""",

        'code_reviewer': """
You are an Odoo code reviewer.

Review this code for:
- Security issues (SQL injection, XSS, Access Control)
- Performance issues (N+1 queries, inefficient loops)
- Odoo best practices
- Common mistakes

Code:
{code}

Context:
{context}

Provide:
- Issues found (with severity)
- Suggested fixes
- Explanation of WHY it's an issue
""",

        'conflict_resolver': """
You are helping resolve a conflict in module design.

Conflict:
{conflict_description}

Context:
{context}

Provide:
- Analysis of the conflict
- Possible solutions (at least 3)
- Pros/cons of each solution
- Recommended solution (with reasoning)
""",
    }

    def build(self, prompt_type, **kwargs):
        """Build prompt from template"""
        template = self.PROMPTS.get(prompt_type)
        if not template:
            raise ValueError(f"Unknown prompt type: {prompt_type}")

        return template.format(**kwargs)
```

---

## 📱 UI Components

### 1. Chat Widget (JavaScript/OWL)

```javascript
/** @odoo-module **/
import { Component, useState } from "@odoo/owl";

export class AIChat extends Component {
    static template = "itx_moduler.AIChat";

    setup() {
        this.state = useState({
            messages: [],
            context: {},
            isTyping: false,
            suggestions: [],
        });
    }

    async sendMessage(message) {
        // Add user message to UI
        this.addMessage('user', message);

        // Show typing indicator
        this.state.isTyping = true;

        try {
            // Call backend
            const response = await this.rpc('/ai/chat/send', {
                session_id: this.props.sessionId,
                message: message,
            });

            // Add AI response
            this.addMessage('assistant', response.content);

            // Update context
            this.state.context = response.context;

            // Show suggestions if any
            this.state.suggestions = response.suggestions || [];

        } finally {
            this.state.isTyping = false;
        }
    }

    addMessage(role, content) {
        this.state.messages.push({
            role: role,
            content: content,
            timestamp: Date.now(),
        });
    }
}
```

### 2. Progress Dashboard

```javascript
export class ProgressDashboard extends Component {
    static template = "itx_moduler.ProgressDashboard";

    setup() {
        this.state = useState({
            phases: [],
            currentPhase: null,
            overallProgress: 0,
        });

        this.loadProgress();
    }

    async loadProgress() {
        const data = await this.rpc('/ai/progress/get', {
            project_id: this.props.projectId,
        });

        this.state.phases = data.phases;
        this.state.currentPhase = data.current_phase;
        this.state.overallProgress = data.overall_progress;
    }
}
```

---

## 🔄 Request/Response Flow

### Example: User adds a field

```
1. User: "เพิ่ม field email"
   ↓
2. UI sends to backend
   POST /ai/chat/send
   {
     session_id: 123,
     message: "เพิ่ม field email"
   }
   ↓
3. ConversationManager.process_user_message()
   ├── Build context (from DB)
   │   ├── Current models
   │   ├── Recent decisions
   │   └── Progress state
   │
   ├── Build prompt
   │   System: "You are Odoo expert..."
   │   Context: {models: [...], decisions: [...]}
   │   User: "เพิ่ม field email"
   │
   ├── Call Claude API
   │   → Claude analyzes
   │   → Checks for user_id.email
   │   → Returns structured response
   │
   ├── Parse response
   │   {
   │     understanding: "User wants email field",
   │     warnings: ["user_id.email exists"],
   │     questions: ["Use existing or add new?"],
   │     suggestions: [
   │       {type: "use_related", path: "user_id.email"},
   │       {type: "add_new", reason: "..."}
   │     ]
   │   }
   │
   ├── Validate (run validation rules)
   │   Rule: check_duplicate_info
   │   → Warning: redundant field
   │
   └── Return to UI
       {
         content: "⚠️ Warning: ...",
         suggestions: [...],
         requires_confirmation: true
       }
   ↓
4. UI shows warning + suggestions
   User chooses option
   ↓
5. Loop back to step 2
```

---

## 🎯 Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)
**Models:**
- ✅ itx.moduler.ai.project
- ✅ itx.moduler.ai.session
- ✅ itx.moduler.ai.message
- ✅ itx.moduler.ai.context

**Services:**
- ✅ ClaudeAPIClient (basic)
- ✅ ConversationManager (basic)

**UI:**
- ✅ Simple chat widget

**Capabilities Covered:**
- #1 Context Memory (basic)

---

### Phase 2: Decision & Tracking (Weeks 3-4)
**Models:**
- ✅ itx.moduler.ai.decision
- ✅ itx.moduler.ai.decision.reason
- ✅ itx.moduler.ai.decision.impact

**Services:**
- ✅ DecisionManager
- ✅ WhyTracker

**Capabilities Covered:**
- #2 Decision Log
- #6 Why Tracking

---

### Phase 3: Guided Flow (Weeks 5-6)
**Models:**
- ✅ itx.moduler.ai.progress
- ✅ itx.moduler.ai.progress.task

**Services:**
- ✅ ConversationStateMachine
- ✅ ProgressTracker

**UI:**
- ✅ Progress Dashboard
- ✅ Step-by-step wizard

**Capabilities Covered:**
- #3 Guided Conversation
- #5 Incremental Refinement
- #9 Progress Awareness

---

### Phase 4: Validation (Weeks 7-8)
**Models:**
- ✅ itx.moduler.ai.validation.rule
- ✅ itx.moduler.ai.conflict
- ✅ itx.moduler.ai.conflict.resolution

**Services:**
- ✅ ValidationEngine
- ✅ ConflictDetector
- ✅ ConflictResolver

**UI:**
- ✅ Validation warnings
- ✅ Conflict resolution wizard

**Capabilities Covered:**
- #4 Constraint Validation
- #7 Assumption Checking
- #8 Conflict Resolution

---

### Phase 5: Advanced (Weeks 9-10)
**Models:**
- ✅ itx.moduler.ai.history (for rollback)
- ✅ itx.moduler.ai.dependency (for impact analysis)

**Services:**
- ✅ HistoryManager
- ✅ DependencyTracker
- ✅ RollbackEngine

**Capabilities Covered:**
- #10 Rollback & Iteration

---

## 💰 Cost Considerations

### Claude API Pricing (Sonnet 4.5)
- Input: $3 / million tokens
- Output: $15 / million tokens

### Typical Conversation:
```
Context per message: ~5,000 tokens (input)
User message: ~100 tokens (input)
AI response: ~1,000 tokens (output)

Cost per message:
= (5,100 * $3 / 1M) + (1,000 * $15 / 1M)
= $0.0153 + $0.015
= ~$0.03 per message

Typical module creation: ~50 messages
= ~$1.50 per module

Monthly (100 modules): ~$150
```

### Optimization Strategies:
1. **Context Compression** - Only send relevant context
2. **Cache System Prompts** - Reuse common prompts
3. **Batch Operations** - Multiple validations in one call
4. **Smart Caching** - Cache repeated analyses

---

## 🔐 Security Considerations

1. **API Key Storage**
   - Store in Odoo config file (not in database)
   - Use environment variables
   - Encrypt if possible

2. **Data Privacy**
   - User data sent to Claude (external service)
   - Consider: On-premise Claude option
   - Log what's sent to API

3. **Rate Limiting**
   - Implement rate limits per user
   - Prevent abuse

4. **Access Control**
   - Only authorized users can use AI features
   - Audit log all AI interactions

---

## 📊 Monitoring & Analytics

Track:
- API calls per day/month
- Token usage
- Cost per project
- User satisfaction (thumbs up/down on responses)
- Common issues/conflicts detected
- Most used features

---

**Status:** Technical Design Complete
**Next:** Start Implementation Phase 1

---

**Created:** 2025-12-26
**Author:** Technical Architecture Team
