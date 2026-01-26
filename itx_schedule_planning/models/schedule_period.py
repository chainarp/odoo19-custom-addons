# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class SchedulePeriod(models.Model):
    _name = 'itx.schedule.period'
    _description = 'Schedule Period'
    _order = 'date_start desc'

    name = fields.Char(
        string='Name',
        required=True,
        help='Period name, e.g., March 2026'
    )
    date_start = fields.Date(
        string='Start Date',
        required=True,
        help='Period start date (default: 26th of month)'
    )
    date_end = fields.Date(
        string='End Date',
        required=True,
        help='Period end date (default: 25th of next month)'
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('active', 'Active'),
            ('closed', 'Closed'),
        ],
        string='Status',
        default='draft',
        required=True,
        help='Period status'
    )
    days_count = fields.Integer(
        string='Days',
        compute='_compute_days_count',
        store=True,
        help='Number of days in period'
    )
    planning_ids = fields.One2many(
        comodel_name='itx.schedule.planning',
        inverse_name='period_id',
        string='Plannings',
        help='Schedule plannings in this period'
    )
    planning_count = fields.Integer(
        string='Planning Count',
        compute='_compute_planning_count',
        store=True
    )
    active = fields.Boolean(
        string='Active',
        default=True
    )

    _date_check = models.Constraint(
        'CHECK(date_end > date_start)',
        'End date must be after start date!',
    )

    @api.depends('date_start', 'date_end')
    def _compute_days_count(self):
        for record in self:
            if record.date_start and record.date_end:
                record.days_count = (record.date_end - record.date_start).days + 1
            else:
                record.days_count = 0

    @api.depends('planning_ids')
    def _compute_planning_count(self):
        for record in self:
            record.planning_count = len(record.planning_ids)

    @api.constrains('date_start', 'date_end')
    def _check_date_overlap(self):
        """Check for overlapping periods."""
        for record in self:
            overlapping = self.search([
                ('id', '!=', record.id),
                ('date_start', '<=', record.date_end),
                ('date_end', '>=', record.date_start),
            ])
            if overlapping:
                raise ValidationError(_(
                    'Period dates overlap with: %s'
                ) % ', '.join(overlapping.mapped('name')))

    @api.model
    def _get_default_dates(self, reference_date=None):
        """
        Calculate default period dates.
        Default: 26th of month to 25th of next month.
        """
        if not reference_date:
            reference_date = fields.Date.context_today(self)

        # If we're before the 26th, use current month
        # If we're on or after 26th, use next month
        if reference_date.day < 26:
            start_date = reference_date.replace(day=26) - relativedelta(months=1)
        else:
            start_date = reference_date.replace(day=26)

        end_date = start_date + relativedelta(months=1, days=-1)

        return {
            'date_start': start_date,
            'date_end': end_date,
        }

    @api.model
    def create_next_period(self):
        """Create the next period based on the latest one."""
        last_period = self.search([], order='date_end desc', limit=1)

        if last_period:
            date_start = last_period.date_end + relativedelta(days=1)
            date_end = date_start + relativedelta(months=1, days=-1)
            name = date_start.strftime('%B %Y')
        else:
            defaults = self._get_default_dates()
            date_start = defaults['date_start']
            date_end = defaults['date_end']
            name = date_start.strftime('%B %Y')

        return self.create({
            'name': name,
            'date_start': date_start,
            'date_end': date_end,
            'state': 'draft',
        })

    def action_activate(self):
        """Activate the period."""
        for record in self:
            if record.state != 'draft':
                raise ValidationError(_('Only draft periods can be activated.'))
            record.state = 'active'

    def action_close(self):
        """Close the period."""
        for record in self:
            if record.state != 'active':
                raise ValidationError(_('Only active periods can be closed.'))
            record.state = 'closed'

    def action_reset_to_draft(self):
        """Reset to draft (for corrections)."""
        for record in self:
            if record.state == 'closed':
                raise ValidationError(_('Closed periods cannot be reset.'))
            record.state = 'draft'

    def action_view_plannings(self):
        """Open plannings for this period."""
        self.ensure_one()
        return {
            'name': _('Plannings'),
            'type': 'ir.actions.act_window',
            'res_model': 'itx.schedule.planning',
            'view_mode': 'tree,form',
            'domain': [('period_id', '=', self.id)],
            'context': {'default_period_id': self.id},
        }
