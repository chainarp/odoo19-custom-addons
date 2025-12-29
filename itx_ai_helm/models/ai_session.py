# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AiSession(models.Model):
    """
    Conversation Session

    Represents one conversation session with AI.
    Each session has messages and can build/use contexts.
    """
    _name = 'itx.ai.session'
    _description = 'AI Conversation Session'
    _order = 'create_date desc'

    name = fields.Char(
        'Session Name',
        compute='_compute_name',
        store=True,
        readonly=False
    )

    project_id = fields.Many2one(
        'itx.ai.project',
        string='Project',
        required=True,
        ondelete='cascade',
        index=True
    )

    # Messages
    message_ids = fields.One2many(
        'itx.ai.message',
        'session_id',
        string='Messages'
    )

    message_count = fields.Integer(
        'Message Count',
        compute='_compute_message_count',
        store=True
    )

    # Contexts used in this session
    context_ids = fields.One2many(
        'itx.ai.context',
        'session_id',
        string='Session Contexts'
    )

    # State
    state = fields.Selection([
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
    ], default='active', string='Status')

    # Metadata
    user_id = fields.Many2one(
        'res.users',
        string='User',
        default=lambda self: self.env.user
    )

    start_date = fields.Datetime(
        'Start Date',
        default=fields.Datetime.now,
        readonly=True
    )

    end_date = fields.Datetime('End Date')

    active = fields.Boolean(default=True)

    # Stats
    total_tokens = fields.Integer(
        'Total Tokens Used',
        compute='_compute_stats',
        store=True
    )

    total_cost = fields.Float(
        'Total Cost (USD)',
        compute='_compute_stats',
        store=True
    )

    @api.depends('project_id', 'create_date')
    def _compute_name(self):
        for session in self:
            if not session.name:
                if session.project_id:
                    session_num = len(session.project_id.session_ids)
                    session.name = f'{session.project_id.name} - Session {session_num}'
                else:
                    session.name = f'Session {session.id or "New"}'

    @api.depends('message_ids')
    def _compute_message_count(self):
        for session in self:
            session.message_count = len(session.message_ids)

    @api.depends('message_ids.tokens_used', 'message_ids.cost')
    def _compute_stats(self):
        for session in self:
            session.total_tokens = sum(session.message_ids.mapped('tokens_used'))
            session.total_cost = sum(session.message_ids.mapped('cost'))

    def action_complete(self):
        """Mark session as completed"""
        self.write({
            'state': 'completed',
            'end_date': fields.Datetime.now(),
        })

    def action_reopen(self):
        """Reopen completed session"""
        self.write({
            'state': 'active',
            'end_date': False,
        })

    def send_message(self, content):
        """
        Send message to AI (future implementation with Claude API)

        Args:
            content (str): User message content

        Returns:
            dict: AI response
        """
        self.ensure_one()

        # Create user message
        user_msg = self.env['itx.ai.message'].create({
            'session_id': self.id,
            'role': 'user',
            'content': content,
        })

        # TODO: Call Claude API
        # TODO: Get AI response
        # TODO: Create AI message

        # Placeholder response
        return {
            'message': 'AI response will be implemented with Claude API integration',
            'user_message_id': user_msg.id,
        }
