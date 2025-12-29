# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AiMessage(models.Model):
    """
    Chat Message

    Represents one message in a conversation session.
    Can be from user, AI assistant, or system.
    """
    _name = 'itx.ai.message'
    _description = 'AI Chat Message'
    _order = 'create_date asc'

    session_id = fields.Many2one(
        'itx.ai.session',
        string='Session',
        required=True,
        ondelete='cascade',
        index=True
    )

    role = fields.Selection([
        ('user', 'User'),
        ('assistant', 'AI Assistant'),
        ('system', 'System'),
    ], required=True, string='Role')

    content = fields.Text(
        'Message Content',
        required=True
    )

    # AI Response Metadata
    tokens_used = fields.Integer(
        'Tokens Used',
        help='Number of tokens used for this message (AI only)'
    )

    cost = fields.Float(
        'Cost (USD)',
        digits=(10, 4),
        help='Cost for this message (AI only)'
    )

    response_time = fields.Float(
        'Response Time (seconds)',
        help='Time taken to generate response (AI only)'
    )

    model = fields.Char(
        'AI Model',
        help='AI model used (e.g., claude-sonnet-4.5-20250929)'
    )

    # Attachments (future)
    attachment_ids = fields.Many2many(
        'ir.attachment',
        string='Attachments'
    )

    # Metadata
    create_date = fields.Datetime(
        'Created',
        readonly=True
    )

    @api.model
    def create(self, vals):
        """Override create to set default values"""
        if vals.get('role') == 'user':
            # User messages don't have AI metadata
            vals.update({
                'tokens_used': 0,
                'cost': 0.0,
                'response_time': 0.0,
            })
        return super().create(vals)
