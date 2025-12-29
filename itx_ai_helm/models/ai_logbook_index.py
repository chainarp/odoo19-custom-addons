# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AiLogbookIndex(models.Model):
    """
    Search Index for Log Book

    Stores keywords to enable fast search.
    Solves the problem of slow search with dynamic sections.
    """
    _name = 'itx.ai.logbook.index'
    _description = 'Logbook Search Index'

    # Keys
    keyword = fields.Char(
        'Keyword',
        required=True,
        index=True,
        help='Indexed keyword'
    )

    context_id = fields.Many2one(
        'itx.ai.context',
        string='Context',
        required=True,
        ondelete='cascade',
        index=True,
        help='Context containing this keyword'
    )

    section_type = fields.Char(
        'Section Type',
        index=True,
        help='Context type (e.g., logbook_design)'
    )

    # Stats
    frequency = fields.Integer(
        'Frequency',
        default=1,
        help='Number of times this keyword appears'
    )

    last_seen = fields.Datetime(
        'Last Seen',
        default=fields.Datetime.now,
    )

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
            domain_id (str): Filter by domain
            project_id (int): Filter by project ID

        Returns:
            recordset: Contexts ordered by relevance
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
