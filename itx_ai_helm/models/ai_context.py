# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
import re
import json


class AiContext(models.Model):
    """
    Context Container - Spoke 1: Context Memory (Log Book)

    Stores conversation context and knowledge entries organized by:
    - Domain level (domain_id set, project_id NULL): General knowledge (e.g., Odoo v19 changes)
    - Project level (both domain_id and project_id set): Project-specific knowledge

    Uses flexible JSON storage for entries with dynamic classification.
    """
    _name = 'itx.ai.context'
    _description = 'AI Context Container (Log Book)'
    _order = 'version desc, create_date desc'

    # Keys - Critical for hierarchy
    session_id = fields.Many2one(
        'itx.ai.session',
        string='Session',
        index=True,
        help='Conversation session (optional - can have context without active session)'
    )

    domain_id = fields.Char(
        'Domain',
        required=True,
        index=True,
        help='Domain identifier (e.g., odoo_development, audio_circuit)'
    )

    project_id = fields.Many2one(
        'itx.ai.project',
        string='Project',
        ondelete='cascade',
        index=True,
        help='NULL = domain-level knowledge, Set = project-specific knowledge'
    )

    # Dynamic context type based on domain structure
    context_type = fields.Char(
        'Context Type',
        required=True,
        index=True,
        help='Examples: logbook_requirements, logbook_design, odoo_knowledge_v17'
    )

    # Flexible JSON storage
    context_data = fields.Serialized(
        'Context Data',
        help='Structure: {"entries": [{"timestamp", "classification", "content", "summary", "reason", "impact", "keywords"}, ...]}'
    )

    # Version control
    version = fields.Integer('Version', default=1, readonly=True)
    active_version = fields.Boolean('Active Version', default=True, index=True)

    # Metadata
    entry_count = fields.Integer('Entry Count', compute='_compute_entry_count', store=True)
    last_entry_date = fields.Datetime('Last Entry', compute='_compute_last_entry_date', store=True)
    data_size = fields.Integer('Data Size (bytes)', compute='_compute_data_size', store=True)

    _sql_constraints = [
        ('unique_active_per_type',
         'UNIQUE(session_id, project_id, context_type, active_version) WHERE active_version = true',
         'Only one active context per type per session/project!'),
    ]

    @api.depends('context_data')
    def _compute_entry_count(self):
        """Count entries in context_data"""
        for record in self:
            if record.context_data and 'entries' in record.context_data:
                record.entry_count = len(record.context_data['entries'])
            else:
                record.entry_count = 0

    @api.depends('context_data')
    def _compute_last_entry_date(self):
        """Get timestamp of last entry"""
        for record in self:
            if record.context_data and 'entries' in record.context_data:
                entries = record.context_data['entries']
                if entries:
                    last_entry = max(entries, key=lambda x: x.get('timestamp', ''))
                    record.last_entry_date = last_entry.get('timestamp')
                else:
                    record.last_entry_date = False
            else:
                record.last_entry_date = False

    @api.depends('context_data')
    def _compute_data_size(self):
        """Calculate data size in bytes"""
        for record in self:
            if record.context_data:
                record.data_size = len(json.dumps(record.context_data))
            else:
                record.data_size = 0

    def add_entry(self, entry_data):
        """
        Add new entry to log book with timestamp and keywords

        Args:
            entry_data (dict): {
                'classification': 'category/subcategory',
                'content': 'The actual content',
                'summary': 'Brief summary',
                'reason': 'Why this matters',
                'impact': 'What this affects',
                'type': 'decision|knowledge|note'
            }

        Returns:
            dict: The created entry with timestamp and keywords
        """
        self.ensure_one()

        context_data = self.context_data or {}
        entries = context_data.get('entries', [])

        # Add timestamp
        entry_data['timestamp'] = datetime.now().isoformat()

        # Extract keywords
        entry_data['keywords'] = self._extract_keywords(entry_data['content'])

        # Add to entries
        entries.append(entry_data)
        context_data['entries'] = entries

        # Update context_data
        self.context_data = context_data

        # Update search index
        self._update_search_index(entry_data)

        return entry_data

    def search_logbook(self, query, classification=None, date_from=None, date_to=None):
        """
        Search logbook entries

        Args:
            query (str): Search keywords
            classification (str): Filter by classification (e.g., 'design/pattern')
            date_from (datetime): Filter entries from this date
            date_to (datetime): Filter entries to this date

        Returns:
            list: Matching entries
        """
        self.ensure_one()

        if not self.context_data or 'entries' not in self.context_data:
            return []

        entries = self.context_data['entries']
        results = []

        # Normalize query
        query_keywords = self._extract_keywords(query) if query else []

        for entry in entries:
            # Filter by classification
            if classification and not entry.get('classification', '').startswith(classification):
                continue

            # Filter by date range
            entry_date = entry.get('timestamp')
            if date_from and entry_date < date_from.isoformat():
                continue
            if date_to and entry_date > date_to.isoformat():
                continue

            # Filter by keywords
            if query_keywords:
                entry_keywords = entry.get('keywords', [])
                # Check if any query keyword matches entry keywords
                if not any(qk in entry_keywords for qk in query_keywords):
                    continue

            results.append(entry)

        return results

    def _extract_keywords(self, text):
        """
        Extract keywords from text for indexing

        Simple implementation: lowercase words, remove common words

        Args:
            text (str): Text to extract keywords from

        Returns:
            list: List of keywords
        """
        if not text:
            return []

        # Common words to ignore (Thai + English)
        stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'been', 'be',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should',
            'could', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those',
            'ที่', 'และ', 'หรือ', 'ใน', 'ของ', 'เป็น', 'มี', 'ได้', 'จะ', 'ว่า'
        }

        # Extract words (alphanumeric + Thai)
        words = re.findall(r'\w+', text.lower())

        # Filter keywords
        keywords = [w for w in words if len(w) > 2 and w not in stopwords]

        # Remove duplicates while preserving order
        seen = set()
        unique_keywords = []
        for kw in keywords:
            if kw not in seen:
                seen.add(kw)
                unique_keywords.append(kw)

        return unique_keywords[:20]  # Limit to 20 keywords

    def _update_search_index(self, entry_data):
        """
        Update search index with entry keywords

        Args:
            entry_data (dict): Entry with keywords
        """
        self.ensure_one()

        keywords = entry_data.get('keywords', [])
        index_model = self.env['itx.ai.logbook.index']

        for keyword in keywords:
            # Check if keyword already indexed for this context
            index = index_model.search([
                ('keyword', '=', keyword),
                ('context_id', '=', self.id)
            ], limit=1)

            if index:
                # Update frequency
                index.frequency += 1
                index.last_seen = fields.Datetime.now()
            else:
                # Create new index
                index_model.create({
                    'keyword': keyword,
                    'context_id': self.id,
                    'section_type': self.context_type,
                    'frequency': 1,
                    'last_seen': fields.Datetime.now(),
                })

    def get_timeline_view(self):
        """
        Get entries organized by timeline

        Returns:
            list: Entries sorted by timestamp (newest first)
        """
        self.ensure_one()

        if not self.context_data or 'entries' not in self.context_data:
            return []

        entries = self.context_data['entries']

        # Sort by timestamp (newest first)
        sorted_entries = sorted(
            entries,
            key=lambda x: x.get('timestamp', ''),
            reverse=True
        )

        return sorted_entries

    def get_classification_tree(self):
        """
        Get entries organized by classification

        Returns:
            dict: Tree structure {category: {subcategory: [entries]}}
        """
        self.ensure_one()

        if not self.context_data or 'entries' not in self.context_data:
            return {}

        entries = self.context_data['entries']
        tree = {}

        for entry in entries:
            classification = entry.get('classification', 'uncategorized')
            parts = classification.split('/')

            category = parts[0] if parts else 'uncategorized'
            subcategory = parts[1] if len(parts) > 1 else 'general'

            if category not in tree:
                tree[category] = {}

            if subcategory not in tree[category]:
                tree[category][subcategory] = []

            tree[category][subcategory].append(entry)

        return tree

    def create_new_version(self):
        """
        Create new version of this context (for version control)

        Returns:
            recordset: New version record
        """
        self.ensure_one()

        # Mark current as inactive
        self.active_version = False

        # Create new version
        new_version = self.copy({
            'version': self.version + 1,
            'active_version': True,
        })

        return new_version
