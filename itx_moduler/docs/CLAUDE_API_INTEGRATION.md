# Claude Code CLI/API Integration Architecture

## 🎯 Vision: IDE for System Analysts

ITX Moduler as an **Integrated Development Environment** where:
1. SA sketches requirements
2. Designs module structure
3. Claude Code assists in generating actual code
4. Ready-to-deploy module output

---

## 🏗️ Architecture Options

### Option A: Direct Claude API Integration (Recommended)

```
┌─────────────────────────────────────────┐
│         ITX Moduler (Odoo Module)        │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │  User Interface (Wizard)            │ │
│  │  - Describe requirements            │ │
│  │  - Design models/views              │ │
│  └───────────────┬────────────────────┘ │
│                  │                       │
│  ┌───────────────▼────────────────────┐ │
│  │  ITX Moduler Engine                 │ │
│  │  - Parse requirements               │ │
│  │  - Build context                    │ │
│  │  - Call Claude API                  │ │
│  └───────────────┬────────────────────┘ │
│                  │                       │
└──────────────────┼───────────────────────┘
                   │
                   │ HTTPS
                   ▼
    ┌──────────────────────────────┐
    │   Claude API (Anthropic)     │
    │   api.anthropic.com          │
    └──────────────┬───────────────┘
                   │
                   │ JSON Response
                   ▼
    ┌──────────────────────────────┐
    │   Snapshot Tables            │
    │   - itx.moduler.model        │
    │   - itx.moduler.model.field  │
    │   - itx.moduler.view         │
    └──────────────────────────────┘
```

**Pros:**
- Direct integration
- Fast response
- Full control
- Works in Odoo

**Cons:**
- Requires API key management
- Costs per usage
- Network dependency

---

### Option B: Claude Code CLI Bridge

```
┌─────────────────────────────────────────┐
│         ITX Moduler (Odoo Module)        │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │  User Interface                     │ │
│  └───────────────┬────────────────────┘ │
│                  │                       │
│  ┌───────────────▼────────────────────┐ │
│  │  CLI Bridge Service                 │ │
│  │  - Execute `claude` commands        │ │
│  │  - Parse CLI output                 │ │
│  └───────────────┬────────────────────┘ │
└──────────────────┼───────────────────────┘
                   │
                   │ subprocess.run()
                   ▼
    ┌──────────────────────────────┐
    │   Claude Code CLI            │
    │   (Already installed)        │
    └──────────────┬───────────────┘
                   │
                   ▼
    ┌──────────────────────────────┐
    │   Claude API (via CLI)       │
    └──────────────────────────────┘
```

**Pros:**
- Use existing Claude Code setup
- No separate API key needed
- User already authenticated

**Cons:**
- Less control
- Harder to parse responses
- CLI must be installed

---

### Option C: Hybrid Approach (Best!)

```
Use Claude API for:
- Structured code generation
- Model/field creation
- View generation

Use Claude Code CLI for:
- Code review
- Debugging suggestions
- Best practices advice
```

---

## 🔧 Implementation Details

### 1. API Key Management

```python
# models/res_config_settings.py
class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    claude_api_key = fields.Char(
        'Claude API Key',
        config_parameter='itx_moduler.claude_api_key',
        help='Get your API key from https://console.anthropic.com'
    )

    claude_model = fields.Selection([
        ('claude-sonnet-4-5-20250929', 'Claude Sonnet 4.5 (Recommended)'),
        ('claude-opus-4-5-20251101', 'Claude Opus 4.5 (Most capable)'),
        ('claude-haiku-3-5-20241022', 'Claude Haiku 3.5 (Fastest)'),
    ], default='claude-sonnet-4-5-20250929',
       config_parameter='itx_moduler.claude_model')
```

---

### 2. Claude Service Layer

```python
# models/itx_moduler_claude_service.py
import anthropic
import json
from odoo import models, api

class ItxCreatorClaudeService(models.AbstractModel):
    _name = 'itx.moduler.claude.service'
    _description = 'Claude API Service'

    @api.model
    def _get_api_key(self):
        return self.env['ir.config_parameter'].sudo().get_param(
            'itx_moduler.claude_api_key'
        )

    @api.model
    def _get_model(self):
        return self.env['ir.config_parameter'].sudo().get_param(
            'itx_moduler.claude_model',
            default='claude-sonnet-4-5-20250929'
        )

    @api.model
    def call_claude(self, prompt, system_prompt=None, max_tokens=8000):
        """Call Claude API with given prompt"""
        api_key = self._get_api_key()
        if not api_key:
            raise UserError('Claude API key not configured. '
                          'Please configure in Settings.')

        client = anthropic.Anthropic(api_key=api_key)

        messages = [{
            "role": "user",
            "content": prompt
        }]

        response = client.messages.create(
            model=self._get_model(),
            max_tokens=max_tokens,
            system=system_prompt or self._get_default_system_prompt(),
            messages=messages
        )

        return response.content[0].text

    @api.model
    def _get_default_system_prompt(self):
        return """You are an expert Odoo developer assistant.

Your role:
1. Understand user requirements for Odoo modules
2. Generate model definitions in JSON format
3. Create view XML structures
4. Write Python business logic
5. Follow Odoo best practices

Guidelines:
- Use proper Odoo naming conventions
- Fields: many2one_id, one2many_ids, many2many_ids
- Models: lowercase with dots (sale.order)
- Always include help text
- Add constraints where appropriate
- Write clean, documented code

Output format: Valid JSON matching ITX Moduler snapshot structure
"""
```

---

### 3. AI Model Creator

```python
# wizards/itx_moduler_ai_wizard.py
class ItxCreatorAIWizard(models.TransientModel):
    _name = 'itx.moduler.ai.wizard'
    _description = 'AI-Assisted Model Creator'

    module_id = fields.Many2one('itx.moduler.module', required=True)
    prompt = fields.Text('Describe what you want to create', required=True)

    # Conversation context
    conversation_history = fields.Text('Previous messages (JSON)')

    # Results
    claude_response = fields.Text('Claude Response', readonly=True)
    generated_models = fields.Many2many(
        'itx.moduler.model',
        string='Generated Models',
        readonly=True
    )

    def action_generate_with_ai(self):
        """Main action: Send to Claude and create snapshots"""

        # Build prompt with context
        full_prompt = self._build_context_aware_prompt()

        # Call Claude
        claude_service = self.env['itx.moduler.claude.service']
        response_text = claude_service.call_claude(full_prompt)

        self.claude_response = response_text

        # Parse JSON response
        try:
            response_data = json.loads(response_text)
        except json.JSONDecodeError:
            # Claude might return markdown code blocks
            response_data = self._extract_json_from_markdown(response_text)

        # Create snapshots
        created_models = self._create_snapshots_from_response(response_data)
        self.generated_models = created_models

        # Save to conversation history
        self._update_conversation_history(full_prompt, response_text)

        return self.action_show_results()

    def _build_context_aware_prompt(self):
        """Build prompt with existing module context"""
        context = f"""
Module: {self.module_id.name}
Description: {self.module_id.shortdesc}

Existing models in this module:
"""
        for model in self.module_id.model_ids:
            context += f"- {model.name}\n"

        context += f"\n\nUser request:\n{self.prompt}"

        return context

    def _create_snapshots_from_response(self, response_data):
        """Convert Claude JSON to snapshot records"""
        created_models = self.env['itx.moduler.model']

        for model_data in response_data.get('models', []):
            # Create model
            model = self.env['itx.moduler.model'].create({
                'name': model_data['name'],
                'model': model_data['model'],
                'description': model_data.get('description', ''),
                'module_id': self.module_id.id,
            })

            # Create fields
            for field_data in model_data.get('fields', []):
                self.env['itx.moduler.model.field'].create({
                    'model_id': model.id,
                    'name': field_data['name'],
                    'field_type': field_data['type'],
                    'field_description': field_data.get('string', ''),
                    'help': field_data.get('help', ''),
                    'required': field_data.get('required', False),
                    'readonly': field_data.get('readonly', False),
                })

            created_models |= model

        return created_models
```

---

### 4. UI Integration

```xml
<!-- views/itx_moduler.xml -->

<!-- Button in module form -->
<button name="action_open_ai_wizard"
        string="🤖 Create with AI"
        type="object"
        class="btn-primary"/>

<!-- AI Wizard Form -->
<record id="itx_moduler_ai_wizard_form" model="ir.ui.view">
    <field name="name">itx.moduler.ai.wizard.form</field>
    <field name="model">itx.moduler.ai.wizard</field>
    <field name="arch" type="xml">
        <form>
            <group>
                <field name="module_id" readonly="1"/>
                <field name="prompt"
                       placeholder="Describe what you want to create...
Example: Create a customer loyalty program with points, rewards, and redemption tracking"
                       widget="text"
                       required="1"/>
            </group>

            <group string="Claude Response" attrs="{'invisible': [('claude_response', '=', False)]}">
                <field name="claude_response" widget="text" readonly="1"/>
            </group>

            <group string="Generated Models" attrs="{'invisible': [('generated_models', '=', [])]}">
                <field name="generated_models" nolabel="1">
                    <tree>
                        <field name="name"/>
                        <field name="model"/>
                        <field name="field_count"/>
                    </tree>
                </field>
            </group>

            <footer>
                <button name="action_generate_with_ai"
                        string="Generate with AI"
                        type="object"
                        class="btn-primary"/>
                <button string="Cancel" class="btn-secondary" special="cancel"/>
            </footer>
        </form>
    </field>
</record>
```

---

## 🎨 User Experience Scenarios

### Scenario 1: Create Model from Description

**User Input:**
```
"I need an employee attendance tracking system with:
- Check-in/out times
- Location tracking
- Work hours calculation
- Leave integration
- Manager approval workflow"
```

**Claude Response:**
```json
{
  "models": [
    {
      "name": "hr.attendance.record",
      "model": "hr.attendance.record",
      "description": "Employee Attendance Record",
      "fields": [
        {
          "name": "employee_id",
          "type": "many2one",
          "relation": "hr.employee",
          "string": "Employee",
          "required": true
        },
        {
          "name": "check_in",
          "type": "datetime",
          "string": "Check In",
          "required": true
        },
        {
          "name": "check_out",
          "type": "datetime",
          "string": "Check Out"
        },
        {
          "name": "worked_hours",
          "type": "float",
          "string": "Worked Hours",
          "compute": "_compute_worked_hours",
          "store": true
        }
      ],
      "methods": [
        {
          "name": "_compute_worked_hours",
          "decorator": "@api.depends('check_in', 'check_out')",
          "code": "for record in self:\n    if record.check_in and record.check_out:\n        delta = record.check_out - record.check_in\n        record.worked_hours = delta.total_seconds() / 3600\n    else:\n        record.worked_hours = 0"
        }
      ]
    }
  ]
}
```

**ITX Moduler Action:**
- Creates `itx.moduler.model` record
- Creates all field snapshots
- Stores method code
- Ready to preview/edit/generate

---

### Scenario 2: Iterative Refinement

**Round 1:**
```
User: "Add overtime calculation"
Claude: Adds overtime_hours field + compute method
```

**Round 2:**
```
User: "Send notification if late >30min"
Claude: Adds late_minutes field + automated action
```

---

### Scenario 3: View Generation

**User:**
```
"Create a dashboard view for attendance with:
- Today's attendance list
- Late arrivals (red)
- On-time arrivals (green)
- Pivot chart by department"
```

**Claude:**
- Generates kanban view XML
- Creates graph view
- Adds filters and groupby
- Proper color coding

---

## 💰 Cost Management

### Token Usage Optimization

```python
class ItxCreatorClaudeService(models.AbstractModel):
    _name = 'itx.moduler.claude.service'

    # Cache for common patterns
    _pattern_cache = {}

    @api.model
    def call_claude_cached(self, prompt, cache_key=None):
        """Call Claude with caching for repeated patterns"""
        if cache_key and cache_key in self._pattern_cache:
            return self._pattern_cache[cache_key]

        response = self.call_claude(prompt)

        if cache_key:
            self._pattern_cache[cache_key] = response

        return response
```

### Monthly Budget Control

```python
# Track API usage
class ItxCreatorAPIUsage(models.Model):
    _name = 'itx.moduler.api.usage'

    date = fields.Date(default=fields.Date.today)
    user_id = fields.Many2one('res.users')
    prompt_tokens = fields.Integer()
    completion_tokens = fields.Integer()
    total_cost = fields.Float(compute='_compute_cost')

    @api.depends('prompt_tokens', 'completion_tokens')
    def _compute_cost(self):
        # Sonnet 4.5 pricing
        INPUT_COST = 3.00 / 1_000_000  # $3 per 1M tokens
        OUTPUT_COST = 15.00 / 1_000_000  # $15 per 1M tokens

        for record in self:
            record.total_cost = (
                record.prompt_tokens * INPUT_COST +
                record.completion_tokens * OUTPUT_COST
            )
```

---

## 🔐 Security Considerations

### API Key Storage
```python
# Use ir.config_parameter (encrypted in some Odoo versions)
# Or use environment variables
import os

def _get_api_key(self):
    # Priority: Environment > Config Parameter
    return (
        os.environ.get('CLAUDE_API_KEY') or
        self.env['ir.config_parameter'].sudo().get_param(
            'itx_moduler.claude_api_key'
        )
    )
```

### User Permissions
```xml
<!-- security/itx_moduler.xml -->
<record id="group_itx_moduler_user" model="res.groups">
    <field name="name">ITX Moduler User</field>
</record>

<record id="group_itx_moduler_ai_user" model="res.groups">
    <field name="name">ITX Moduler AI User</field>
    <field name="implied_ids" eval="[(4, ref('group_itx_moduler_user'))]"/>
    <field name="comment">Can use AI features (costs money!)</field>
</record>
```

---

## 🚀 Rollout Plan

### Phase 1: Basic Integration (Week 1)
- [ ] Add Claude API key config
- [ ] Create claude.service model
- [ ] Basic API call functionality
- [ ] Simple model generation test

### Phase 2: AI Wizard (Week 2)
- [ ] Create AI wizard UI
- [ ] Implement prompt→JSON→snapshot pipeline
- [ ] Add conversation history
- [ ] Error handling & validation

### Phase 3: Advanced Features (Week 3)
- [ ] View generation
- [ ] Method code generation
- [ ] Smart suggestions
- [ ] Code review

### Phase 4: Optimization (Week 4)
- [ ] Response caching
- [ ] Token usage tracking
- [ ] Cost monitoring dashboard
- [ ] User quotas

---

## 📊 Success Metrics

| Metric | Target |
|--------|--------|
| Time to create model | < 2 minutes |
| Code quality score | > 85% |
| User satisfaction | > 4.5/5 |
| Cost per module | < $0.50 |
| Adoption rate | > 70% of users |

---

## 🎯 Next Steps

1. ✅ Complete module renaming
2. ✅ Create snapshot architecture
3. ⏳ Test basic functionality
4. 🔜 Buy Claude API credits ($10 for testing)
5. 🔜 Implement basic AI integration
6. 🔜 Beta test with real users

---

**ITX Moduler + Claude = The Future of Odoo Development** 🚀

*Making System Analysts into Module Developers!*
