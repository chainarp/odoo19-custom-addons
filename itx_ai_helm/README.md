# ITX AI Helm - AI-Powered Conversation Framework

**Version:** 1.0.0
**Status:** Development - Spoke 1 Implementation
**Date:** 2025-12-29

---

## 🚢 Ship's Wheel Metaphor

```
AI = Mighty Ship (powerful, large)
Helm (Ship's Wheel) = ITX AI Helm (control interface)
10 Spokes = The conversation management capabilities
Small person grabs the spokes to control the mighty ship
```

---

## 🎯 What is ITX AI Helm?

ITX AI Helm is a **domain-agnostic AI conversation framework** that provides structured conversation management for AI-assisted applications.

**Key Features:**
- ⛵ **The 10 Spokes** - Comprehensive conversation management capabilities
- 🎨 **Domain-agnostic** - Works with any domain (Odoo, Audio circuit, etc.)
- 🔌 **Pluggable** - Add domain knowledge via plugins
- 🧩 **Reusable** - Use across multiple projects
- 🤖 **AI-Powered** - Integrates with Claude API

---

## 🎯 The 10 Spokes

| Spoke | Name | Status | Description |
|-------|------|--------|-------------|
| **1** | **Context Memory (Log Book)** ⭐ | ✅ v1.0.0 | Structured knowledge storage with timeline & classification |
| **2** | Decision Log | 🔜 Future | Track decisions with reasons and impacts |
| **3** | Guided Conversation | 🔜 Future | Step-by-step, progressive disclosure |
| **4** | Constraint Validation | 🔜 Future | Check conflicts and feasibility |
| **5** | Incremental Refinement | 🔜 Future | Build in rounds (skeleton → core → polish) |
| **6** | Why Tracking | 🔜 Future | Capture rationale for all decisions |
| **7** | Assumption Checking | 🔜 Future | Ask before assuming |
| **8** | Conflict Resolution | 🔜 Future | Detect conflicts and suggest resolutions |
| **9** | Progress Awareness | 🔜 Future | Always know current state and completion % |
| **10** | Rollback & Iteration | 🔜 Future | Safe rollback, iterate on decisions |

---

## 📦 Installation

### 1. Install the module

```bash
# Copy to your Odoo addons directory
cp -r itx_ai_helm /path/to/odoo/addons/

# Restart Odoo
sudo systemctl restart odoo

# Update apps list and install
# Odoo UI → Apps → Update Apps List → Search "ITX AI Helm" → Install
```

### 2. Configure Claude API

```python
# Settings → Technical → System Parameters
Key: itx.ai.claude.api_key
Value: sk-ant-api03-...your-claude-api-key...
```

**Get Claude API Key:**
1. Go to https://console.anthropic.com/
2. Create account / Login
3. Go to API Keys
4. Create new key
5. Copy and paste to Odoo system parameter

---

## 🚀 Quick Start

### Create Your First AI Project

```python
# Via Python
project = env['itx.ai.project'].create({
    'name': 'My First Project',
    'domain_type': 'odoo_development',  # or custom domain
})

# Create session
session = env['itx.ai.session'].create({
    'project_id': project.id,
})

# Add context entry (Log Book)
context = env['itx.ai.context'].search([
    ('project_id', '=', project.id),
    ('context_type', '=', 'logbook_requirements'),
], limit=1)

if not context:
    context = env['itx.ai.context'].create({
        'domain_id': 'odoo_development',
        'project_id': project.id,
        'context_type': 'logbook_requirements',
        'context_data': {'entries': []},
    })

# Add entry
context.add_entry({
    'classification': 'requirements/features',
    'content': 'User wants purchase request system with approval workflow',
    'summary': 'Purchase request with approval',
    'reason': 'Business needs formal approval process',
    'impact': 'Requires models, workflow, and UI',
    'type': 'decision',
})
```

---

## 📖 Spoke 1: Context Memory (Log Book)

### Concept

Think of it as a **structured notebook** that:
- Organizes knowledge by domain structure (e.g., SDLC for Odoo)
- Separates domain knowledge from project knowledge
- Stores only "สาระ" (substance) - content that impacts the project
- Provides timeline and classification views

### Two-Level Hierarchy

**1. Domain Level** (project_id = NULL)
- General knowledge (e.g., "Odoo v19 changes from v17")
- Reusable across projects
- "Notes for next life AI"

**2. Project Level** (project_id = specific)
- Project-specific knowledge
- Business requirements
- Design decisions

### Models

**`itx.ai.context`** - Core storage
- Flexible JSON entries
- Version control
- Search optimization

**`itx.ai.logbook.section`** - Section definitions
- Domain-specific structure
- SDLC for Odoo: Requirements, Design, Implementation, Testing, Deployment
- Odoo Knowledge sections (per version)

**`itx.ai.logbook.index`** - Search index
- Keyword-based search
- Performance optimization

### Use Cases

**1. Save Design Decision**
```python
context.add_entry({
    'classification': 'design/pattern',
    'content': 'Use mail.thread mixin for audit trail',
    'summary': 'Added chatter to purchase.request',
    'reason': 'Need audit trail and communication history',
    'impact': 'purchase.request model',
    'type': 'decision',
})
```

**2. Store Odoo Knowledge**
```python
# Domain-level (project_id=NULL)
odoo_knowledge = env['itx.ai.context'].create({
    'domain_id': 'odoo_development',
    'project_id': False,  # NULL = domain level
    'context_type': 'odoo_knowledge_v19',
    'context_data': {'entries': []},
})

odoo_knowledge.add_entry({
    'classification': 'odoo/view_changes',
    'content': 'Odoo 19: Tree view renamed to List view in arch',
    'summary': 'Tree → List in v19',
    'reason': 'Framework change',
    'impact': 'All view definitions',
    'type': 'knowledge',
})
```

**3. Search Log Book**
```python
# Search by keyword
results = context.search_logbook('approval workflow')

# Search by classification
results = context.search_logbook('', classification='design/pattern')

# Timeline view
timeline = context.get_timeline_view()

# Classification tree
tree = context.get_classification_tree()
```

---

## 🔌 Domain Plugins

### Creating Custom Domain

```python
# models/domain_myapp.py

from odoo import models, api

class MyAppDomain(models.AbstractModel):
    _name = 'itx.ai.domain.myapp'
    _inherit = 'itx.ai.domain.abstract'

    @api.model
    def get_domain_name(self):
        return 'My Application Development'

    @api.model
    def get_logbook_sections(self):
        """Define sections for this domain"""
        return [
            {
                'section_id': 'requirements',
                'name': 'Requirements',
                'sequence': 10,
            },
            {
                'section_id': 'design',
                'name': 'Design',
                'sequence': 20,
            },
            # ... more sections
        ]
```

---

## 🛠️ Development

### Project Structure

```
itx_ai_helm/
├── __init__.py
├── __manifest__.py
├── README.md
│
├── models/                    # Core models
│   ├── __init__.py
│   ├── ai_project.py         # Projects
│   ├── ai_session.py         # Sessions
│   ├── ai_message.py         # Chat messages
│   ├── ai_context.py         # Spoke 1: Context storage
│   ├── ai_logbook_section.py # Section definitions
│   └── ai_logbook_index.py   # Search index
│
├── views/                     # UI views
│   ├── ai_project_views.xml
│   ├── ai_context_views.xml
│   ├── ai_logbook_section_views.xml
│   └── ai_menu.xml
│
├── security/                  # Access control
│   └── ir.model.access.csv
│
├── data/                      # Default data
│   └── ai_logbook_sections.xml
│
├── controllers/               # Web controllers (future)
│   └── __init__.py
│
├── services/                  # AI services (future)
│   ├── claude_api_client.py
│   └── context_builder.py
│
└── static/src/                # Frontend (future)
    └── components/
        └── chat_widget/
```

---

## 📚 Documentation

Full documentation available in `/docs/06-Planning/`:

- **[ITX_AI_HELM_VISION.md](../itx_moduler/docs/06-Planning/ITX_AI_HELM_VISION.md)** - Complete vision & architecture
- **[SPOKE_1_CONTEXT_MEMORY_DESIGN.md](../itx_moduler/docs/06-Planning/SPOKE_1_CONTEXT_MEMORY_DESIGN.md)** - Spoke 1 detailed design

---

## 🗺️ Roadmap

### Version 1.0.0 (Current) - Spoke 1
- ✅ Core models (Project, Session, Message)
- ✅ Context Memory (Log Book)
- ✅ Logbook sections
- ✅ Search optimization
- ✅ Basic views

### Version 1.1.0 (Next) - Spoke 2
- Decision Log
- Why tracking
- Basic AI chat interface

### Version 2.0.0 (Future) - Spokes 3-5
- Guided Conversation
- Constraint Validation
- Incremental Refinement

### Version 3.0.0 (Future) - Spokes 6-10
- Assumption Checking
- Conflict Resolution
- Progress Awareness
- Rollback & Iteration

---

## 💰 Operational Costs

### Claude API Usage

```
Per Project (estimated):
- Context size: ~2,000 tokens
- Messages per session: 20
- Total: ~40,000 tokens
- Cost: ~$0.50 per project

Monthly (10 projects):
- Cost: ~$5/month
```

**Very affordable for AI-powered development!**

---

## 📄 License

LGPL-3

---

## 🙋 Support

For questions and issues:
- GitHub: [Your repo URL]
- Email: [Your email]

---

**Created:** 2025-12-29
**Author:** Your Company
**Version:** 1.0.0
