# Spoke 1: Context Memory - Detailed Design

**Module:** `itx_ai_helm` (ชื่อเดิม: itx_ai_steerer - เปลี่ยนชื่อ 2025-12-29)
**Date:** 2025-12-27 (Updated: 2025-12-29)
**Status:** Design Complete - Ready for Implementation

---

## 🎯 Overview

**Spoke 1: Context Memory** เป็น spoke แรกและสำคัญที่สุดของ AI Helm

### ปรัชญา:
```
"AI ต้องจำได้ว่าเรากำลังทำอะไร คุยเรื่องอะไร และตัดสินใจอะไรมาแล้วบ้าง"
```

### Metaphor:
```
เหมือน "สมุดจด" (Log Book) ที่:
- มีโครงสร้างตาม domain
- จดเฉพาะ "สาระ" (ที่ส่งผลกับโปรเจค)
- จัดเก็บแบบ organized พร้อม timeline
- ค้นหากลับมาอ่านได้
```

---

## 🎨 Big Picture

### Workflow Overview:
```
User (SA/Developer)
    ↓ Working on project
┌────────────────────────┐
│  itx_helloworld        │ ← Project (Module/Addon)
│  (via itx_moduler)     │
└───────────┬────────────┘
            │ คุยกับ AI
            ▼
┌────────────────────────────────────────────────┐
│         itx_ai_helm (AI)                       │
│                                                 │
│  รู้อัตโนมัติ:                                 │
│  • domain_id = 'odoo_development'              │
│  • project_id = 'itx_helloworld'               │
│                                                 │
│  เตรียม "Log Book" สำหรับ project นี้          │
└────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────┐
│  Log Book Structure (ตาม Domain)                │
│                                                  │
│  สำหรับ domain = 'odoo_development':            │
│  ลอก SDLC มาใช้เป็นโครงสร้าง:                  │
│                                                  │
│  📔 Requirements                                │
│     • คุยเรื่อง requirements                    │
│     • จดสิ่งที่เป็นสาระ                         │
│                                                  │
│  📔 Design                                       │
│     • คุยเรื่อง design, patterns                │
│     • จดการตัดสินใจ + เหตุผล                    │
│                                                  │
│  📔 Implementation                               │
│     • คุยเรื่อง coding                          │
│     • จดวิธีแก้ปัญหา                            │
│                                                  │
│  📔 Testing                                      │
│  📔 Deployment                                   │
│                                                  │
│  📔 Odoo Knowledge (แยกมา)                      │
│     • ความรู้เรื่อง Odoo ทั่วไป (version-based) │
│     • Note สำหรับ "พี่คลอดชาติหน้า"             │
│     • เช่น: Tree → List (v17)                   │
└─────────────────────────────────────────────────┘
```

---

## 🔑 Key Concepts

### 1. Domain vs Project

#### Domain Level (ใหญ่):
```
domain_id = 'odoo_development'

ความรู้ทั่วไป:
- Odoo framework knowledge
- Patterns & Best practices
- Version-specific changes
- Common pitfalls

ไม่ผูกกับ project ใดๆ
project_id = NULL
```

#### Project Level (เล็ก):
```
project_id = 123  # itx_helloworld

ความรู้เฉพาะ business:
- Requirements ของ project นี้
- Design decisions ของ project นี้
- Implementation notes
- Testing results

ผูกกับ project เฉพาะ
domain_id = 'odoo_development'
```

---

### 2. Log Book Concept

#### ไม่ใช่:
- ❌ Static context snapshot
- ❌ Configuration data
- ❌ ทุกอย่างที่คุยกัน

#### แต่เป็น:
- ✅ "สมุดจด" ที่มีโครงสร้าง
- ✅ จดเฉพาะ "สาระ"
- ✅ Organized ตาม domain structure
- ✅ มี timeline

---

### 3. "สาระ" คืออะไร?

**Definition:**
```
"สาระ" = สิ่งที่ส่งผลกระทบต่อโปรเจค
```

**ตัวอย่าง:**

**เป็นสาระ ✅:**
- การตัดสินใจ: "ใช้ state machine pattern"
- Requirements: "ต้องการ approval workflow"
- Design: "Models: purchase.request, purchase.request.line"
- Bug fix: "แก้ปัญหา N+1 query ด้วย prefetch"
- Knowledge: "Odoo v19: group_ids → privilege_id.group_ids"

**ไม่ใช่สาระ ❌:**
- Small talk: "สวัสดีครับ"
- Confirmation: "ครับ เข้าใจแล้ว"
- ถาม-ตอบทั่วไป: "Field type มีอะไรบ้าง?"

---

### 4. UI Flow: User ตัดสินใจเก็บ/ทิ้ง

```
┌─────────────────────────────────────────┐
│  Chat (แบบพิมพ์นิยม - Balloon Style)    │
├─────────────────────────────────────────┤
│                                          │
│  👤 User: "ใช้ state machine ไหม"       │
│                                          │
│  🤖 AI: "ดีครับ! แนะนำให้ใช้            │
│         draft → manager → approved       │
│         เพราะเป็น Odoo best practice     │
│         และ scalable"                    │
│                                          │
│  ┌──────────────────────────────────┐   │
│  │ 💡 AI ตรวจพบการตัดสินใจ:        │   │
│  │                                   │   │
│  │ 📋 เรื่อง: State Machine Pattern │   │
│  │                                   │   │
│  │ 📔 แนะนำจัดเก็บใน: Design        │   │
│  │                                   │   │
│  │ 📝 สรุป:                          │   │
│  │ ใช้ state field แบบ              │   │
│  │ draft→manager→approved            │   │
│  │                                   │   │
│  │ 🤔 เหตุผล:                        │   │
│  │ • Best practice สำหรับ approval   │   │
│  │ • Scalable, ขยายได้ในอนาคต       │   │
│  │                                   │   │
│  │ 💥 Impact:                        │   │
│  │ • ต้องเพิ่ม state field           │   │
│  │ • ต้องเพิ่ม action_submit()       │   │
│  │ • ต้องเพิ่ม action_approve()      │   │
│  │                                   │   │
│  │ [💾 เก็บ] [🗑️ ทิ้ง]              │   │
│  └──────────────────────────────────┘   │
│                                          │
│  (ถ้า user กด "เก็บ" → save to logbook) │
│  (ถ้า user กด "ทิ้ง" → discard)         │
│                                          │
└─────────────────────────────────────────┘

Note:
- ปุ่ม "เก็บ/ทิ้ง" จัดการ content จาก
  "การตัดสินใจล่าสุดที่เก็บ/ทิ้ง" ถึง "ปุ่มที่กดอยู่นี้"
```

---

### 5. AI Responsibilities

**หน้าที่ของ AI:**

1. **Detect Decisions/Knowledge**
   - วิเคราะห์ conversation
   - หาการตัดสินใจ
   - หาความรู้ที่เป็นประโยชน์

2. **Search Best Logbook Section**
   - เข้าใจ content
   - Search section ที่เหมาะสม
   - แนะนำการจัดเก็บ

3. **Summarize**
   - สรุปการตัดสินใจ
   - อธิบายเหตุผล
   - ระบุ impact

4. **Organize**
   - จัดเก็บใน section ที่ถูกต้อง
   - Add classification
   - Add timestamp

---

## 📊 Database Design

### Model 1: `itx.ai.context` (Core - ใช้เดิม Extended)

```python
class AiContext(models.Model):
    """
    Context Container - เก็บ log book entries

    ใช้ของเดิมแต่ extend:
    - เพิ่ม domain_id
    - context_type เป็น dynamic (ตาม domain structure)
    - context_data เก็บ entries แบบ flexible
    """
    _name = 'itx.ai.context'
    _description = 'AI Context Container'
    _order = 'version desc'

    # === Keys ===
    session_id = fields.Many2one(
        'itx.ai.session',
        string='Session',
        required=True,
        ondelete='cascade',
        index=True,
        help='Session ที่สร้าง context นี้'
    )

    domain_id = fields.Char(
        'Domain',
        index=True,
        help='Domain type (e.g., odoo_development, audio_circuit)'
    )

    project_id = fields.Many2one(
        'itx.ai.project',
        string='Project',
        ondelete='cascade',
        index=True,
        help='Project ที่เกี่ยวข้อง (NULL = domain-level knowledge)'
    )

    # === Context Type (Dynamic!) ===
    context_type = fields.Char(
        'Context Type',
        required=True,
        index=True,
        help='''
        Dynamic context type based on domain structure

        Examples:
        - logbook_requirements
        - logbook_design
        - logbook_implementation
        - odoo_knowledge_v17
        - odoo_knowledge_v19
        - audio_knowledge_general

        Format: [category]_[section]
        '''
    )

    # === Version Control ===
    version = fields.Integer(
        'Version',
        default=1,
        help='Context version - increments when updated'
    )

    active_version = fields.Boolean(
        'Active Version',
        default=True,
        index=True,
        help='Only one version can be active per type per session/project'
    )

    # === Data Storage (Flexible JSON) ===
    context_data = fields.Serialized(
        'Context Data',
        help='''
        Log book entries stored as JSON

        Structure:
        {
            "entries": [
                {
                    "timestamp": "2025-12-27T10:30:00",
                    "classification": "design/pattern",
                    "content": "ใช้ state machine pattern",
                    "summary": "State: draft→manager→approved",
                    "reason": "Best practice, scalable",
                    "impact": "ต้องเพิ่ม state field + methods",
                    "type": "decision",  # decision / knowledge / note
                    "keywords": ["state", "pattern", "workflow"],
                },
                ...
            ]
        }
        '''
    )

    # === Metadata ===
    snapshot_date = fields.Datetime(
        'Snapshot Date',
        default=fields.Datetime.now,
        index=True,
    )

    data_size = fields.Integer(
        'Data Size (bytes)',
        compute='_compute_data_size',
        store=True,
    )

    entry_count = fields.Integer(
        'Entry Count',
        compute='_compute_entry_count',
        store=True,
        help='Number of entries in this context'
    )

    # === Constraints ===
    _sql_constraints = [
        ('unique_active_per_type',
         '''UNIQUE(session_id, project_id, context_type, active_version)
            WHERE active_version = true''',
         'Only one active context per type per session/project!'),
    ]

    @api.depends('context_data')
    def _compute_data_size(self):
        import json
        for record in self:
            if record.context_data:
                record.data_size = len(json.dumps(record.context_data))
            else:
                record.data_size = 0

    @api.depends('context_data')
    def _compute_entry_count(self):
        for record in self:
            if record.context_data and 'entries' in record.context_data:
                record.entry_count = len(record.context_data['entries'])
            else:
                record.entry_count = 0

    def add_entry(self, entry_data):
        """
        Add new entry to log book

        Args:
            entry_data (dict): Entry data
                {
                    'content': '...',
                    'summary': '...',
                    'reason': '...',
                    'impact': '...',
                    'type': 'decision' / 'knowledge' / 'note',
                    'classification': 'design/pattern',
                }
        """
        self.ensure_one()

        # Get current entries
        context_data = self.context_data or {}
        entries = context_data.get('entries', [])

        # Add timestamp, keywords
        from datetime import datetime
        entry_data['timestamp'] = datetime.now().isoformat()

        # Extract keywords from content
        entry_data['keywords'] = self._extract_keywords(entry_data['content'])

        # Add to entries
        entries.append(entry_data)

        # Update context_data
        context_data['entries'] = entries
        self.context_data = context_data

        # Update index
        self._update_search_index(entry_data)

    def _extract_keywords(self, text):
        """Extract keywords from text (simple version)"""
        # TODO: Better keyword extraction
        # For now: split by space, lowercase, unique
        import re
        words = re.findall(r'\w+', text.lower())
        # Filter out common words
        stopwords = {'the', 'is', 'at', 'which', 'on', 'and', 'a', 'an'}
        keywords = [w for w in words if w not in stopwords and len(w) > 2]
        return list(set(keywords))[:10]  # Top 10 unique

    def _update_search_index(self, entry_data):
        """Update search index for this entry"""
        keywords = entry_data.get('keywords', [])

        for keyword in keywords:
            index = self.env['itx.ai.logbook.index'].search([
                ('keyword', '=', keyword),
                ('context_id', '=', self.id),
            ], limit=1)

            if index:
                index.frequency += 1
            else:
                self.env['itx.ai.logbook.index'].create({
                    'keyword': keyword,
                    'context_id': self.id,
                    'section_type': self.context_type,
                    'frequency': 1,
                })
```

---

### Model 2: `itx.ai.logbook.section` (Metadata)

```python
class AiLogbookSection(models.Model):
    """
    Logbook Section Definition (Metadata)

    ไม่ได้เก็บ content จริงๆ
    แค่ define ว่ามี section อะไรบ้าง
    """
    _name = 'itx.ai.logbook.section'
    _description = 'Logbook Section Definition'
    _order = 'sequence, name'

    # === Keys ===
    domain_id = fields.Char(
        'Domain',
        required=True,
        index=True,
        help='Domain type (e.g., odoo_development)'
    )

    section_id = fields.Char(
        'Section ID',
        required=True,
        help='Unique section ID (e.g., requirements, design, odoo_knowledge_v19)'
    )

    # === Info ===
    name = fields.Char(
        'Section Name',
        required=True,
        help='Display name (e.g., Requirements, Design)'
    )

    description = fields.Text(
        'Description',
        help='What this section is for'
    )

    # === Type ===
    is_default = fields.Boolean(
        'Default Section',
        default=False,
        help='Default section that comes with domain'
    )

    is_domain_knowledge = fields.Boolean(
        'Domain Knowledge',
        default=False,
        help='Section สำหรับความรู้ทั่วไป (ไม่ผูก project)'
    )

    # === Classification Hints (ช่วย AI) ===
    keywords = fields.Text(
        'Keywords',
        help='Keywords (comma-separated) ที่บ่งบอกว่า content น่าจะอยู่ section นี้'
    )

    example_topics = fields.Text(
        'Example Topics',
        help='ตัวอย่าง topics ที่ควรอยู่ใน section นี้'
    )

    # === Display ===
    sequence = fields.Integer('Sequence', default=10)
    icon = fields.Char('Icon', help='Icon name (e.g., "📋", "📔")')

    # === Constraints ===
    _sql_constraints = [
        ('unique_section',
         'UNIQUE(domain_id, section_id)',
         'Section ID must be unique per domain!'),
    ]

    @api.model
    def get_sections_for_domain(self, domain_id):
        """
        Get all sections for domain
        Returns ordered list
        """
        return self.search([
            ('domain_id', '=', domain_id),
        ], order='sequence, name')

    @api.model
    def suggest_section(self, domain_id, content):
        """
        Suggest best section for content

        Args:
            domain_id: Domain
            content: Content text

        Returns:
            section recordset or None
        """
        sections = self.get_sections_for_domain(domain_id)

        best_score = 0
        best_section = None

        for section in sections:
            score = self._calculate_match_score(section, content)
            if score > best_score:
                best_score = score
                best_section = section

        return best_section

    def _calculate_match_score(self, section, content):
        """Calculate match score between section and content"""
        score = 0
        content_lower = content.lower()

        # Check keywords
        if section.keywords:
            keywords = [k.strip() for k in section.keywords.split(',')]
            for keyword in keywords:
                if keyword.lower() in content_lower:
                    score += 10

        # Check example topics
        if section.example_topics:
            topics = [t.strip() for t in section.example_topics.split(',')]
            for topic in topics:
                if topic.lower() in content_lower:
                    score += 5

        return score
```

---

### Model 3: `itx.ai.logbook.index` (Search Optimization)

```python
class AiLogbookIndex(models.Model):
    """
    Search Index สำหรับ log book

    เก็บ keywords เพื่อ search ให้เร็ว
    (แก้ปัญหา dynamic sections ค้นหาช้า)
    """
    _name = 'itx.ai.logbook.index'
    _description = 'Logbook Search Index'

    # === Keys ===
    keyword = fields.Char(
        'Keyword',
        required=True,
        index=True,
        help='Indexed keyword'
    )

    context_id = fields.Many2one(
        'itx.ai.context',
        required=True,
        ondelete='cascade',
        index=True,
        help='Context ที่ keyword นี้อยู่'
    )

    section_type = fields.Char(
        'Section Type',
        index=True,
        help='Context type (e.g., logbook_design)'
    )

    # === Stats ===
    frequency = fields.Integer(
        'Frequency',
        default=1,
        help='จำนวนครั้งที่ keyword นี้ปรากฏ'
    )

    last_seen = fields.Datetime(
        'Last Seen',
        default=fields.Datetime.now,
    )

    # === Constraints ===
    _sql_constraints = [
        ('unique_keyword_context',
         'UNIQUE(keyword, context_id)',
         'Keyword must be unique per context!'),
    ]

    @api.model
    def search_contexts(self, keywords, domain_id=None, project_id=None):
        """
        Search contexts by keywords

        Args:
            keywords (list): List of keywords
            domain_id: Filter by domain
            project_id: Filter by project

        Returns:
            contexts ordered by relevance
        """
        # Find matching indexes
        domain = [('keyword', 'in', keywords)]

        indexes = self.search(domain)

        # Group by context, sum frequency
        context_scores = {}
        for index in indexes:
            context = index.context_id

            # Filter by domain/project if specified
            if domain_id and context.domain_id != domain_id:
                continue
            if project_id and context.project_id.id != project_id:
                continue

            if context.id not in context_scores:
                context_scores[context.id] = 0

            context_scores[context.id] += index.frequency

        # Sort by score
        sorted_contexts = sorted(
            context_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # Return contexts
        context_ids = [c[0] for c in sorted_contexts]
        return self.env['itx.ai.context'].browse(context_ids)
```

---

## 💡 Use Cases & Examples

### Use Case 1: เริ่ม Session ใหม่

```python
def start_new_session(self, project):
    """
    เริ่ม session ใหม่
    สร้าง log book contexts ตาม domain structure
    """
    # 1. Create session
    session = self.env['itx.ai.session'].create({
        'project_id': project.id,
        'state': 'active',
    })

    domain_id = project.domain_type  # e.g., 'odoo_development'

    # 2. Get sections for this domain
    sections = self.env['itx.ai.logbook.section'].get_sections_for_domain(domain_id)

    # 3. Create context for each section
    for section in sections:
        # Domain-level knowledge (project_id = NULL)
        if section.is_domain_knowledge:
            project_id = False
        else:
            project_id = project.id

        # Create context
        self.env['itx.ai.context'].create({
            'session_id': session.id,
            'domain_id': domain_id,
            'project_id': project_id,
            'context_type': section.section_id,
            'version': 1,
            'active_version': True,
            'context_data': {'entries': []},
        })

    return session
```

---

### Use Case 2: User คุยเรื่อง State Pattern

```python
# === Conversation ===
User: "ใช้ state machine pattern ไหมครับ"
AI: "ดีครับ! แนะนำให้ใช้ draft→manager→approved"

# === AI Processing ===

# 1. Detect Decision
decision = {
    'content': 'ใช้ state machine pattern สำหรับ approval workflow',
    'summary': 'State: draft → manager → approved',
    'reason': 'Best practice สำหรับ Odoo, scalable, ขยายได้',
    'impact': 'ต้องเพิ่ม state field, action_submit(), action_approve()',
    'type': 'decision',
}

# 2. Suggest Section
section = self.env['itx.ai.logbook.section'].suggest_section(
    domain_id='odoo_development',
    content=decision['content'],
)
# → ได้ section: 'logbook_design'

# 3. Show to User
self._show_save_suggestion(
    decision=decision,
    section=section,
    summary=decision['summary'],
    reason=decision['reason'],
    impact=decision['impact'],
)

# 4. User กด [เก็บ]
# → Save entry
context = self.env['itx.ai.context'].search([
    ('session_id', '=', session.id),
    ('project_id', '=', project.id),
    ('context_type', '=', 'logbook_design'),
    ('active_version', '=', True),
], limit=1)

context.add_entry({
    'content': decision['content'],
    'summary': decision['summary'],
    'reason': decision['reason'],
    'impact': decision['impact'],
    'type': 'decision',
    'classification': 'design/pattern',
})

# 5. Result in database:
"""
itx.ai.context:
    context_type: 'logbook_design'
    context_data: {
        'entries': [
            {
                'timestamp': '2025-12-27T10:30:00',
                'classification': 'design/pattern',
                'content': 'ใช้ state machine pattern...',
                'summary': 'State: draft→manager→approved',
                'reason': 'Best practice...',
                'impact': 'ต้องเพิ่ม state field...',
                'type': 'decision',
                'keywords': ['state', 'machine', 'pattern', 'workflow'],
            }
        ]
    }

itx.ai.logbook.index:
    keyword: 'state', context_id: X, frequency: 1
    keyword: 'pattern', context_id: X, frequency: 1
    keyword: 'workflow', context_id: X, frequency: 1
"""
```

---

### Use Case 3: Odoo Knowledge (Note ให้ชาติหน้า)

```python
# === Conversation ===
User: "พี่คลอด Tree view เปลี่ยนชื่อเป็นอะไรใน v17"
AI: "ขอโทษครับ ผมทำผิด! Tree → List ใน Odoo v17"

# === AI Processing ===

# 1. Detect Knowledge
knowledge = {
    'topic': 'View changes in Odoo v17',
    'content': 'Tree view เปลี่ยนชื่อเป็น List view',
    'note': '⚠️ Note for next life: AI ชาติเก่าผิดตรงนี้ทุกคน!',
    'apply_to': ['v17', 'v18', 'v19'],
    'type': 'knowledge',
}

# 2. This is domain-level knowledge (not project-specific)
section = 'odoo_knowledge_v17'

# 3. Save to domain-level context (project_id = NULL)
context = self.env['itx.ai.context'].search([
    ('domain_id', '=', 'odoo_development'),
    ('project_id', '=', False),  # ← NULL = domain-level
    ('context_type', '=', 'odoo_knowledge_v17'),
    ('active_version', '=', True),
], limit=1)

context.add_entry({
    'content': knowledge['content'],
    'topic': knowledge['topic'],
    'note': knowledge['note'],
    'apply_to': knowledge['apply_to'],
    'type': 'knowledge',
    'classification': 'odoo/view_changes',
})

# 4. Result:
"""
itx.ai.context:
    domain_id: 'odoo_development'
    project_id: NULL  ← Domain-level!
    context_type: 'odoo_knowledge_v17'
    context_data: {
        'entries': [
            {
                'timestamp': '2025-12-27T11:15:00',
                'classification': 'odoo/view_changes',
                'topic': 'View changes in Odoo v17',
                'content': 'Tree view เปลี่ยนชื่อเป็น List view',
                'note': '⚠️ Note for next life...',
                'apply_to': ['v17', 'v18', 'v19'],
                'type': 'knowledge',
            }
        ]
    }
"""
```

---

### Use Case 4: ดึง Context สำหรับส่งให้ AI

```python
def get_full_context_for_ai(self, session):
    """
    ดึง context ทั้งหมดสำหรับส่งให้ AI

    Returns:
        dict: {
            'domain_knowledge': [...],
            'project_logbook': [...],
        }
    """
    project = session.project_id
    domain_id = project.domain_type

    # 1. Get domain-level knowledge
    domain_contexts = self.env['itx.ai.context'].search([
        ('domain_id', '=', domain_id),
        ('project_id', '=', False),  # NULL = domain-level
        ('active_version', '=', True),
    ])

    # 2. Get project-level logbook
    project_contexts = self.env['itx.ai.context'].search([
        ('project_id', '=', project.id),
        ('active_version', '=', True),
    ])

    # 3. Extract entries
    domain_entries = []
    for ctx in domain_contexts:
        entries = ctx.context_data.get('entries', [])
        for entry in entries:
            entry['section'] = ctx.context_type
        domain_entries.extend(entries)

    project_entries = []
    for ctx in project_contexts:
        entries = ctx.context_data.get('entries', [])
        for entry in entries:
            entry['section'] = ctx.context_type
        project_entries.extend(entries)

    # 4. Sort by timestamp (recent first)
    domain_entries.sort(key=lambda x: x['timestamp'], reverse=True)
    project_entries.sort(key=lambda x: x['timestamp'], reverse=True)

    return {
        'domain_knowledge': domain_entries,
        'project_logbook': project_entries,
    }


# === Usage in Claude API ===
def build_system_prompt(self, session):
    """Build system prompt with context"""

    context = self.get_full_context_for_ai(session)

    prompt = f"""
You are an AI assistant for Odoo Development.

Project: {session.project_id.name}

=== Domain Knowledge (Odoo Development) ===
{self._format_entries(context['domain_knowledge'])}

=== Project Logbook ({session.project_id.name}) ===
{self._format_entries(context['project_logbook'])}

Remember all decisions and knowledge above.
Refer to them when needed.
"""
    return prompt
```

---

### Use Case 5: Search Logbook

```python
def search_logbook(self, keywords, project_id=None):
    """
    Search logbook by keywords

    Args:
        keywords (list): Keywords to search
        project_id: Filter by project (optional)

    Returns:
        list: Matching entries
    """
    # Use index for fast search
    contexts = self.env['itx.ai.logbook.index'].search_contexts(
        keywords=keywords,
        project_id=project_id,
    )

    results = []
    for context in contexts:
        entries = context.context_data.get('entries', [])

        # Filter entries matching keywords
        for entry in entries:
            entry_keywords = entry.get('keywords', [])
            if any(k in entry_keywords for k in keywords):
                results.append({
                    'section': context.context_type,
                    'entry': entry,
                    'context_id': context.id,
                })

    return results


# Example:
results = search_logbook(['state', 'pattern'], project_id=123)
# Returns:
# [
#   {
#     'section': 'logbook_design',
#     'entry': {
#       'timestamp': '2025-12-27T10:30:00',
#       'content': 'ใช้ state machine pattern...',
#       ...
#     },
#     'context_id': 456,
#   },
#   ...
# ]
```

---

## 🎨 Classification & Timeline

### Classification System

**Format:** `category/subcategory`

**Examples:**
```
Project-Level:
- requirements/feature
- requirements/constraint
- design/pattern
- design/architecture
- design/model
- design/security
- implementation/model
- implementation/view
- implementation/bug_fix
- testing/unit_test
- testing/integration_test

Domain-Level:
- odoo/view_changes
- odoo/security_v19
- odoo/orm_pattern
- odoo/best_practice
- odoo/common_pitfall
```

---

### Timeline View

**Display entries chronologically:**

```
Timeline: itx_helloworld

📅 2025-12-27

10:30 | 📔 Design / Pattern
      | ใช้ state machine pattern
      | State: draft→manager→approved
      | เหตุผล: Best practice, scalable
      [View Details]

11:15 | 📚 Odoo Knowledge / v19
      | group_ids → privilege_id.group_ids
      | Note: เปลี่ยนใน Odoo 19
      [View Details]

14:00 | 📋 Requirements / Feature
      | เพิ่ม budget control
      | แต่ละแผนกมีงบจำกัด
      [View Details]

15:30 | 💻 Implementation / Model
      | สร้าง model: purchase.request
      | Fields: name, department_id, state, line_ids
      [View Details]

📅 2025-12-26
...
```

---

## 🔍 Search Strategy

### Strategy 1: Index-based Search (Fast)
```python
# Use itx.ai.logbook.index
results = env['itx.ai.logbook.index'].search_contexts(
    keywords=['state', 'pattern']
)
# Fast! Uses index
```

### Strategy 2: Full-text Search (Accurate)
```python
# Search in context_data (slower but more accurate)
contexts = env['itx.ai.context'].search([
    ('project_id', '=', project_id),
    ('active_version', '=', True),
])

results = []
for ctx in contexts:
    entries = ctx.context_data.get('entries', [])
    for entry in entries:
        if keyword in entry['content'].lower():
            results.append(entry)
```

### Strategy 3: AI-powered Search (Smart)
```python
# Ask AI to search based on semantic meaning
query = "หาข้อมูลเกี่ยวกับ approval workflow"

# AI analyzes query → extract keywords + intent
# AI searches logbook
# AI ranks by relevance
```

---

## 🎯 Summary

### Key Points:

1. **Log Book Concept** ✅
   - "สมุดจด" ที่มีโครงสร้าง
   - จดเฉพาะสาระ (ที่ส่งผลต่อโปรเจค)
   - Dynamic sections ตาม domain

2. **Two Levels** ✅
   - Domain Knowledge (project_id = NULL)
   - Project Logbook (project_id = specific)

3. **User Control** ✅
   - User ตัดสินใจเก็บ/ทิ้ง
   - AI แนะนำ + สรุป
   - UI: Balloon style with buttons

4. **Database Design** ✅
   - `itx.ai.context` - Core storage (flexible JSON)
   - `itx.ai.logbook.section` - Metadata (define structure)
   - `itx.ai.logbook.index` - Search optimization

5. **Classification & Timeline** ✅
   - Organized by classification
   - Sortable by timestamp
   - Timeline view

6. **Search** ✅
   - Index-based (fast)
   - Full-text (accurate)
   - AI-powered (smart)

---

## 🚀 Next Steps

1. **Implement Models**
   - Create Python files
   - Add constraints
   - Add methods

2. **Create Default Sections**
   - Odoo Development sections (SDLC)
   - Odoo Knowledge sections (version-based)

3. **Build UI**
   - Chat balloon
   - Save suggestion popup
   - Timeline view

4. **Integrate with Claude API**
   - Decision detection
   - Section suggestion
   - Context building

5. **Test**
   - End-to-end scenarios
   - Search performance
   - Timeline display

---

**Status:** Design Complete - Ready for Implementation
**Next:** Implement models and test with real conversations

---

*Created: 2025-12-27*
*Type: Detailed Design Document*
*Version: 1.0.0*
