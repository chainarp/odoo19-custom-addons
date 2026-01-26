# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class SchedulePlanning(models.Model):
    """
    Schedule Planning Header - Level 1
    One record per period (e.g., March 2026)
    """
    _name = 'itx.schedule.planning'
    _description = 'Schedule Planning'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_start desc, id desc'

    name = fields.Char(
        string='Name',
        required=True,
        tracking=True,
        help='Planning name, e.g., Schedule Mar 2026'
    )
    period_id = fields.Many2one(
        comodel_name='itx.schedule.period',
        string='Period',
        required=True,
        ondelete='restrict',
        tracking=True,
        help='Period this planning belongs to'
    )
    date_start = fields.Date(
        related='period_id.date_start',
        string='Start Date',
        store=True,
        readonly=True
    )
    date_end = fields.Date(
        related='period_id.date_end',
        string='End Date',
        store=True,
        readonly=True
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('published', 'Published'),
            ('active', 'Active'),
            ('archived', 'Archived'),
        ],
        string='Status',
        default='draft',
        required=True,
        tracking=True,
        help='Draft: Generated, editable by Manager\n'
             'Published: Visible to employees, editable by Time-off system\n'
             'Active: Running, synced with Attendance\n'
             'Archived: Closed, read-only'
    )
    version = fields.Integer(
        string='Version',
        default=1,
        readonly=True,
        help='Version number (incremented on clone)'
    )
    parent_id = fields.Many2one(
        comodel_name='itx.schedule.planning',
        string='Cloned From',
        readonly=True,
        ondelete='set null',
        help='Parent planning this was cloned from'
    )

    # Workrole lines (Level 2)
    workrole_ids = fields.One2many(
        comodel_name='itx.schedule.planning.workrole',
        inverse_name='planning_id',
        string='Work Roles',
        copy=True,
        help='Work roles included in this planning'
    )

    # Workflow tracking
    published_date = fields.Datetime(
        string='Published Date',
        readonly=True,
        copy=False
    )
    published_by = fields.Many2one(
        comodel_name='res.users',
        string='Published By',
        readonly=True,
        copy=False
    )
    activated_date = fields.Datetime(
        string='Activated Date',
        readonly=True,
        copy=False
    )
    activated_by = fields.Many2one(
        comodel_name='res.users',
        string='Activated By',
        readonly=True,
        copy=False
    )
    archived_date = fields.Datetime(
        string='Archived Date',
        readonly=True,
        copy=False
    )
    archived_by = fields.Many2one(
        comodel_name='res.users',
        string='Archived By',
        readonly=True,
        copy=False
    )

    # Computed summary
    workrole_count = fields.Integer(
        string='Work Role Count',
        compute='_compute_counts',
        store=True
    )
    total_employees = fields.Integer(
        string='Total Employees',
        compute='_compute_counts',
        store=True
    )
    total_entries = fields.Integer(
        string='Total Entries',
        compute='_compute_counts',
        store=True
    )
    gap_count = fields.Integer(
        string='Gap Count',
        compute='_compute_gap_count',
        help='Number of understaffed shifts detected'
    )

    active = fields.Boolean(
        string='Active',
        default=True
    )

    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )

    note = fields.Html(
        string='Notes',
        help='Internal notes about this planning'
    )

    @api.depends('workrole_ids', 'workrole_ids.entry_ids')
    def _compute_counts(self):
        for planning in self:
            planning.workrole_count = len(planning.workrole_ids)
            entries = planning.workrole_ids.mapped('entry_ids')
            planning.total_entries = len(entries)
            planning.total_employees = len(entries.mapped('employee_id'))

    def _compute_gap_count(self):
        # TODO: Implement gap detection logic
        for planning in self:
            planning.gap_count = 0

    # ===================
    # Workflow Actions
    # ===================

    def action_publish(self):
        """Publish the planning - make visible to employees."""
        for planning in self:
            if planning.state != 'draft':
                raise UserError(_('Only draft plannings can be published.'))
            # TODO: Check constraints before publishing
            planning.write({
                'state': 'published',
                'published_date': fields.Datetime.now(),
                'published_by': self.env.uid,
            })
            planning._send_publish_notification()
        return True

    def action_activate(self):
        """Activate the planning - start using for attendance."""
        for planning in self:
            if planning.state != 'published':
                raise UserError(_('Only published plannings can be activated.'))
            planning.write({
                'state': 'active',
                'activated_date': fields.Datetime.now(),
                'activated_by': self.env.uid,
            })
        return True

    def action_archive(self):
        """Archive the planning - close and make read-only."""
        for planning in self:
            if planning.state not in ('published', 'active'):
                raise UserError(_('Only published or active plannings can be archived.'))
            planning.write({
                'state': 'archived',
                'archived_date': fields.Datetime.now(),
                'archived_by': self.env.uid,
            })
        return True

    def action_reset_to_draft(self):
        """Reset to draft state (only from published, not from active/archived)."""
        for planning in self:
            if planning.state != 'published':
                raise UserError(_('Only published plannings can be reset to draft.'))
            planning.write({
                'state': 'draft',
                'published_date': False,
                'published_by': False,
            })
        return True

    def action_clone(self):
        """Clone this planning with incremented version."""
        self.ensure_one()
        new_planning = self.copy({
            'name': _('%s (Copy)', self.name),
            'version': self.version + 1,
            'parent_id': self.id,
            'state': 'draft',
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'itx.schedule.planning',
            'res_id': new_planning.id,
            'view_mode': 'form',
            'target': 'current',
        }

    # ===================
    # Notifications
    # ===================

    def _send_publish_notification(self):
        """Send notification to all employees when schedule is published."""
        # TODO: Implement email/inbox notification
        self.message_post(
            body=_('Schedule has been published.'),
            message_type='notification',
            subtype_xmlid='mail.mt_note'
        )

    # ===================
    # Helper Methods
    # ===================

    def get_entries_by_date(self, date):
        """Get all entries for a specific date."""
        self.ensure_one()
        return self.workrole_ids.mapped('entry_ids').filtered(
            lambda e: e.date == date
        )

    def get_entries_by_employee(self, employee_id):
        """Get all entries for a specific employee."""
        self.ensure_one()
        return self.workrole_ids.mapped('entry_ids').filtered(
            lambda e: e.employee_id.id == employee_id
        )

    def action_view_entries(self):
        """Open entries view for this planning."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Schedule Entries'),
            'res_model': 'itx.schedule.planning.workrole.entry',
            'view_mode': 'list,calendar,form',
            'domain': [('planning_id', '=', self.id)],
            'context': {'default_planning_id': self.id},
        }
