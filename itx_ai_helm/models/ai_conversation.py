# itx_ai_helm/models/ai_conversation.py

from odoo import models, fields, api
import json
from datetime import datetime


class AIConversation(models.Model):
    _name = 'ai.conversation'
    _description = 'AI Conversation History'
    _order = 'create_date desc'

    name = fields.Char('Title', required=True)
    user_id = fields.Many2one('res.users', 'User', default=lambda self: self.env.user)
    message_ids = fields.One2many('ai.conversation.message', 'conversation_id', 'Messages')
    workspace = fields.Char('Workspace Path')
    active = fields.Boolean('Active', default=True)

    @api.model
    def create_new_conversation(self):
        """Create a new conversation"""
        count = self.search_count([('user_id', '=', self.env.user.id)])
        name = f"Conversation {count + 1} - {fields.Datetime.now()}"
        return self.create({
            'name': name,
            'user_id': self.env.user.id,
        })


class AIConversationMessage(models.Model):
    _name = 'ai.conversation.message'
    _description = 'AI Conversation Messages'
    _order = 'create_date'

    conversation_id = fields.Many2one('ai.conversation', 'Conversation', required=True, ondelete='cascade')
    message_type = fields.Selection([
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
        ('error', 'Error')
    ], 'Type', required=True)
    content = fields.Text('Content', required=True)
    code_blocks = fields.Text('Code Blocks')  # JSON stored
    status = fields.Selection([
        ('sending', 'Sending'),
        ('complete', 'Complete'),
        ('error', 'Error')
    ], 'Status', default='complete')

    @api.model
    def format_for_display(self):
        """Format message for frontend display"""
        code_blocks = []
        if self.code_blocks:
            try:
                code_blocks = json.loads(self.code_blocks)
            except:
                pass

        return {
            'id': self.id,
            'type': self.message_type,
            'content': self.content,
            'code_blocks': code_blocks,
            'status': self.status,
            'timestamp': self.create_date.isoformat() if self.create_date else ''
        }