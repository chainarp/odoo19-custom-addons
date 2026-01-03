# -*- coding: utf-8 -*-
{
    'name': 'ITX AI Helm',
    'version': '19.0.1.1.0',
    'category': 'Productivity/AI',
    'summary': 'AI-Powered Conversation Framework with 10 Spokes - Ship\'s Wheel to Control the Mighty AI',
    'description': """
ITX AI Helm - Core AI Conversation Framework
==============================================

**Ship's Wheel Metaphor:**
- AI = Mighty Ship (powerful, large)
- Helm (Ship's Wheel) = Control interface
- 10 Spokes = Conversation management capabilities
- Small person grabs the spokes to control the mighty ship

**The 10 Spokes:**

1. **Context Memory (Log Book)** ⭐ - Remember project, decisions, knowledge
2. **Decision Log** - Track all decisions with reasons and impacts
3. **Guided Conversation** - Step-by-step, progressive disclosure
4. **Constraint Validation** - Check conflicts and feasibility
5. **Incremental Refinement** - Build in rounds (skeleton → core → polish)
6. **Why Tracking** - Capture rationale for all decisions
7. **Assumption Checking** - Ask before assuming
8. **Conflict Resolution** - Detect conflicts and suggest resolutions
9. **Progress Awareness** - Always know current state and completion %
10. **Rollback & Iteration** - Safe rollback, iterate on decisions

**Domain-Agnostic Framework:**
- Works with any domain (Odoo development, Audio circuit, etc.)
- Pluggable domain architecture
- Reusable across projects

**Current Status:**
- Version 1.0.0: Spoke 1 (Context Memory) Implementation
- Future: Spokes 2-10 coming in subsequent releases

**Dependencies:**
- Claude API (Anthropic) - for AI conversation
- base, mail modules

**Use Cases:**
- ITX Moduler: Odoo module development with AI guidance
- Future domains: Audio circuit design, Camping vehicle design, etc.
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        # Security
        'security/ir.model.access.csv',
        'security/ai_helm_security.xml',

        # Data - Default sections
        'data/ai_logbook_sections.xml',

        # Views - Original
        'views/ai_project_views.xml',
        'views/ai_context_views.xml',
        'views/ai_logbook_section_views.xml',
        'views/ai_menu.xml',

        # Views - New (Chat & Conversation)
        'views/ai_conversation_views.xml',
        'views/ai_chat_views.xml',
        'views/menu_views.xml',

        # Views - Terminal (เพิ่มใหม่)
        'views/terminal_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # Terminal Libraries (เพิ่มใหม่)
            'itx_ai_helm/static/lib/xterm/xterm.css',
            'itx_ai_helm/static/lib/xterm/xterm.js',
            'itx_ai_helm/static/lib/xterm-addon-fit/xterm-addon-fit.js',

            # Terminal Component (เพิ่มใหม่)
            'itx_ai_helm/static/src/components/terminal/terminal.scss',
            'itx_ai_helm/static/src/components/terminal/terminal.js',
            'itx_ai_helm/static/src/components/terminal/terminal.xml',

            # Chat Components (existing)
            'itx_ai_helm/static/src/components/ai_chat/ai_chat.js',
            'itx_ai_helm/static/src/components/ai_chat/ai_chat.xml',
            'itx_ai_helm/static/src/components/ai_chat/ai_chat.scss',
        ],
    },
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}