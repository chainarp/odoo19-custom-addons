# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AiProject(models.Model):
    """
    AI-Assisted Project (Domain-agnostic)

    Represents a project that uses AI assistance.
    Can be used for any domain: Odoo development, Audio circuit, etc.
    """
    _name = 'itx.ai.project'
    _description = 'AI Project'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(
        'Project Name',
        required=True,
        tracking=True,
        help='Name of the AI-assisted project'
    )

    # Domain
    domain_type = fields.Selection(
        selection='_get_domain_types',
        string='Domain',
        required=True,
        tracking=True,
        help='Domain of this project (e.g., odoo_development)'
    )

    domain_data = fields.Serialized(
        'Domain Data',
        help='Domain-specific data storage'
    )

    # Description
    description = fields.Html('Description')

    # Sessions
    session_ids = fields.One2many(
        'itx.ai.session',
        'project_id',
        string='Conversation Sessions'
    )

    session_count = fields.Integer(
        'Session Count',
        compute='_compute_session_count',
        store=True
    )

    # Contexts (Log Book)
    context_ids = fields.One2many(
        'itx.ai.context',
        'project_id',
        string='Context / Log Book'
    )

    # Progress
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('on_hold', 'On Hold'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], default='draft', tracking=True, string='Status')

    # Metadata
    user_id = fields.Many2one(
        'res.users',
        string='Responsible',
        default=lambda self: self.env.user,
        tracking=True
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company
    )

    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('name_unique', 'UNIQUE(name, company_id)', 'Project name must be unique per company!'),
    ]

    @api.model
    def _get_domain_types(self):
        """
        Get available domains from plugins

        Override this method or use ir.config_parameter to add domains
        """
        return [
            ('odoo_development', 'Odoo Module Development'),
            ('audio_circuit', 'Audio Circuit Design'),
            ('camping_vehicle', 'Camping Vehicle Design'),
            ('general', 'General Purpose'),
        ]

    @api.depends('session_ids')
    def _compute_session_count(self):
        for project in self:
            project.session_count = len(project.session_ids)

    def action_view_sessions(self):
        """Open sessions for this project"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Sessions - {self.name}',
            'res_model': 'itx.ai.session',
            'view_mode': 'tree,form',
            'domain': [('project_id', '=', self.id)],
            'context': {'default_project_id': self.id},
        }

    def action_view_logbook(self):
        """Open log book (contexts) for this project"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Log Book - {self.name}',
            'res_model': 'itx.ai.context',
            'view_mode': 'tree,form',
            'domain': [('project_id', '=', self.id)],
            'context': {
                'default_project_id': self.id,
                'default_domain_id': self.domain_type,
            },
        }

    def create_session(self):
        """Create new conversation session for this project"""
        self.ensure_one()
        session = self.env['itx.ai.session'].create({
            'project_id': self.id,
            'name': f'{self.name} - Session {len(self.session_ids) + 1}',
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'New Session',
            'res_model': 'itx.ai.session',
            'res_id': session.id,
            'view_mode': 'form',
            'target': 'current',
        }
