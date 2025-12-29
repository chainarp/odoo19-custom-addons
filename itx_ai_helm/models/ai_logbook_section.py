# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AiLogbookSection(models.Model):
    """
    Logbook Section Definition (Metadata only, not content)

    Defines available sections per domain.
    Does not store actual content - content is in itx.ai.context.
    """
    _name = 'itx.ai.logbook.section'
    _description = 'Logbook Section Definition'
    _order = 'sequence, name'

    # Keys
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

    # Info
    name = fields.Char(
        'Section Name',
        required=True,
        help='Display name (e.g., Requirements, Design)'
    )

    description = fields.Text(
        'Description',
        help='What this section is for'
    )

    # Type
    is_default = fields.Boolean(
        'Default Section',
        default=False,
        help='Default section that comes with domain'
    )

    is_domain_knowledge = fields.Boolean(
        'Domain Knowledge',
        default=False,
        help='Section for general knowledge (not tied to specific project)'
    )

    # Classification hints for AI
    keywords = fields.Text(
        'Keywords',
        help='Keywords (comma-separated) indicating content belongs to this section'
    )

    example_topics = fields.Text(
        'Example Topics',
        help='Example topics that should be in this section'
    )

    # Display
    sequence = fields.Integer('Sequence', default=10)
    icon = fields.Char('Icon', help='Icon (e.g., "📋", "📔")')

    _sql_constraints = [
        ('unique_section',
         'UNIQUE(domain_id, section_id)',
         'Section ID must be unique per domain!'),
    ]

    @api.model
    def get_sections_for_domain(self, domain_id):
        """
        Get all sections for domain

        Args:
            domain_id (str): Domain identifier

        Returns:
            recordset: Sections ordered by sequence
        """
        return self.search([
            ('domain_id', '=', domain_id),
        ], order='sequence, name')

    @api.model
    def suggest_section(self, domain_id, content):
        """
        Suggest best section for content based on keywords

        Args:
            domain_id (str): Domain identifier
            content (str): Content text

        Returns:
            recordset: Best matching section or None
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
        """
        Calculate match score between section and content

        Args:
            section (recordset): Section to match
            content (str): Content text

        Returns:
            int: Match score
        """
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
