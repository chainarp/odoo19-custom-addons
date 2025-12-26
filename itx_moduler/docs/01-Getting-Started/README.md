# ITX Moduler Documentation

AI-Powered Visual Odoo Module Creator with Hardware-Licensed Security

**Version:** 19.0.2.0.0
**Last Updated:** 2025-12-14
**Status:** Phase 1 Implementation

---

## 📚 Documentation Index

### 1. Core Concepts

**[SNAPSHOT_ARCHITECTURE.md](SNAPSHOT_ARCHITECTURE.md)** ⭐ **START HERE**
- Complete snapshot table design
- State workflow: Draft → Validated → Applied → Exported → Archived
- Version & revision management system
- Standard vs Custom module modification rules
- 22 table specifications (16 MVP + 6 advanced)
- Implementation priority & sprints
- **Status:** ✅ Approved for Implementation

**[OCE_MODULE_CREATOR_CONCEPT.md](OCE_MODULE_CREATOR_CONCEPT.md)**
- Original metadata-first philosophy
- Virtual Module concept from itx_oce_module_creator
- Phase 1 vs Phase 2 comparison
- Historical context

### 2. AI Integration

**[CLAUDE_ASSISTANCE.md](CLAUDE_ASSISTANCE.md)**
- AI-powered module creation vision
- Natural language to code generation
- User experience scenarios
- Paradigm shift: Clicking → Describing

**[CLAUDE_API_INTEGRATION.md](CLAUDE_API_INTEGRATION.md)**
- Technical architecture for Claude API
- Service layer implementation
- AI wizard design
- Token usage tracking
- Cost management strategies

### 3. Commercial Product

**[LICENSE_INTEGRATION.md](LICENSE_INTEGRATION.md)**
- ITX Security Shield integration
- Hardware-based licensing (RSA-4096 + AES-256-GCM)
- Pricing tiers:
  - Free: 3 models max, no AI
  - Professional: $99/month, 10 AI requests/day
  - Enterprise: $299/month, unlimited AI
  - Lifetime: $4,999 one-time
- Feature matrix by tier

### 4. Development Plan

**[CONSOLIDATION_PLAN.md](CONSOLIDATION_PLAN.md)**
- Strategic plan to merge 4 modules → 1 ultimate module
- 6-phase implementation (14 weeks)
- Final architecture design
- File structure blueprint
- Success criteria & launch checklist

---

## 🎯 Quick Start

### What is ITX Moduler?

ITX Moduler combines the best features of multiple approaches:

1. **Import & Enhance** (from itx_code_generator)
   - Import existing Odoo modules
   - Reverse engineer models, views, menus
   - Export modified versions

2. **Metadata-First Creation** (from itx_oce_module_creator)
   - Create virtual modules in database
   - Design without files
   - Export when ready

3. **AI-Assisted Development** (planned)
   - Describe what you want in natural language
   - Claude generates models, fields, views
   - Iterative refinement

4. **Visual Builder** (planned)
   - Owl 2.x components
   - Drag-drop interface
   - Real-time preview

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────┐
│         ITX Moduler (Odoo Module)        │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │  Import Engine                      │ │
│  │  - Reverse engineer existing        │ │
│  │  - Map models/views/menus           │ │
│  └───────────────┬────────────────────┘ │
│                  │                       │
│  ┌───────────────▼────────────────────┐ │
│  │  Metadata Layer (Snapshots)         │ │
│  │  - itx.moduler.module               │ │
│  │  - Virtual models/fields/views      │ │
│  │  - State workflow                   │ │
│  └───────────────┬────────────────────┘ │
│                  │                       │
│  ┌───────────────▼────────────────────┐ │
│  │  AI Layer (Future)                  │ │
│  │  - Claude API integration           │ │
│  │  - Natural language → code          │ │
│  └───────────────┬────────────────────┘ │
│                  │                       │
│  ┌───────────────▼────────────────────┐ │
│  │  Visual Builder (Future)            │ │
│  │  - Owl components                   │ │
│  │  - Drag-drop interface              │ │
│  └───────────────┬────────────────────┘ │
│                  │                       │
│  ┌───────────────▼────────────────────┐ │
│  │  Code Generator                     │ │
│  │  - Python/XML generation            │ │
│  │  - Export to ZIP                    │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

---

## 🚀 Current Status

### ✅ Implemented (v19.0.2.0.0)
- Module import from existing Odoo modules
- Model/field/view mapping
- ir.model extensions
- SQL constraint management
- Import wizard
- Export to ZIP capability

### 🔜 Planned (Phases 2-6)
- **Phase 2**: Snapshot metadata layer
- **Phase 3**: Claude AI integration
- **Phase 4**: Owl visual builder
- **Phase 5**: ITX Security Shield licensing
- **Phase 6**: Polish & commercial launch

---

## 📖 For Developers

### Key Models

1. **itx.moduler.module** - Main module wrapper
2. **itx.moduler.module.dependency** - Module dependencies
3. **itx.moduler.pyclass** - Python class tracking
4. **ir.model** (extended) - Model management with constraints
5. **ir.model.server_constrain** - Python server constraints
6. **ir.actions.act_window** (extended) - Action windows
7. **ir.ui.menu** (extended) - Menu structure
8. **ir.ui.view** (extended) - View auto-generation

### Important Files

- `models/itx_moduler_module.py` - Core module model
- `models/ir_model.py` - Advanced model extensions
- `controllers/main.py` - HTTP endpoints & export logic
- `wizards/import_module_wizard.py` - Import wizard

---

## 🤝 Contributing

This is a commercial product in development. For inquiries:
- Website: https://www.itexpert.co.th
- Author: Chainaris P

---

## 📄 License

TBD - Will integrate with ITX Security Shield for commercial licensing

---

**Last Updated**: 2025-12-14
**Version**: 19.0.2.0.0
**Status**: Phase 1 Complete, Phase 2+ Planned
