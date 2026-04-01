# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SchedulePlanningWorkroleEntry(models.Model):
    """
    Schedule Planning Entry - Level 3
    One record per employee per day
    """
    _name = 'itx.schedule.planning.workrole.entry'
    _description = 'Schedule Planning Entry'
    _order = 'date, employee_id'
    _rec_name = 'display_name'

    # Parent links
    planning_workrole_id = fields.Many2one(
        comodel_name='itx.schedule.planning.workrole',
        string='Planning Workrole',
        required=True,
        ondelete='cascade',
        index=True
    )
    planning_id = fields.Many2one(
        related='planning_workrole_id.planning_id',
        string='Planning',
        store=True,
        index=True
    )
    workrole_id = fields.Many2one(
        related='planning_workrole_id.workrole_id',
        string='Work Role',
        store=True
    )

    # Core fields
    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Employee',
        required=True,
        ondelete='restrict',
        index=True
    )
    employee_number = fields.Char(
        related='employee_id.employee_number',
        string='Employee Number',
        store=True
    )
    date = fields.Date(
        string='Date',
        required=True,
        index=True
    )

    # Shift information
    shift_type_id = fields.Many2one(
        comodel_name='itx.schedule.shift.type',
        string='Shift Type',
        ondelete='restrict',
        help='Type of shift (Morning, Afternoon, Night, Day Off)'
    )
    shift_type_code = fields.Char(
        related='shift_type_id.code',
        string='Shift Code',
        store=True,
        help='Short code for timeline display (M, A, N, D, OFF)'
    )
    hour_start = fields.Float(
        string='Start Time',
        help='Shift start time (0-24)'
    )
    hour_end = fields.Float(
        string='End Time',
        help='Shift end time (0-24)'
    )
    duration = fields.Float(
        string='Duration (Hours)',
        compute='_compute_duration',
        store=True,
        help='Working hours (excluding break)'
    )

    # Timeline view fields
    date_start = fields.Datetime(
        string='Start DateTime',
        compute='_compute_datetime_fields',
        store=True,
        help='Computed datetime for timeline view'
    )
    date_end = fields.Datetime(
        string='End DateTime',
        compute='_compute_datetime_fields',
        store=True,
        help='Computed datetime for timeline view'
    )
    color = fields.Integer(
        string='Color',
        compute='_compute_color',
        store=True,
        help='Color for timeline/calendar views'
    )

    is_day_off = fields.Boolean(
        string='Day Off',
        default=False,
        help='Scheduled day off'
    )

    # Team info
    workteam_id = fields.Many2one(
        comodel_name='itx.employee.workteam',
        string='Work Team',
        ondelete='restrict',
        help='Team assignment for this entry'
    )

    # Time-off integration
    is_leave = fields.Boolean(
        string='On Leave',
        default=False,
        help='Employee is on approved leave'
    )
    leave_id = fields.Many2one(
        comodel_name='hr.leave',
        string='Leave Request',
        ondelete='set null',
        help='Linked leave request'
    )
    leave_type = fields.Char(
        related='leave_id.holiday_status_id.name',
        string='Leave Type',
        store=True
    )

    # Substitution
    substitute_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Substitute',
        ondelete='set null',
        help='Employee covering this shift'
    )
    is_substitute = fields.Boolean(
        string='Is Substitute',
        default=False,
        help='This entry is for a substitute employee'
    )
    original_employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Original Employee',
        ondelete='set null',
        help='Original employee being substituted'
    )

    # Tracking
    source = fields.Selection(
        selection=[
            ('generated', 'Generated'),
            ('manual', 'Manual'),
            ('swapped', 'Swapped'),
            ('timeoff', 'Time-off'),
        ],
        string='Source',
        default='generated',
        required=True,
        help='How this entry was created'
    )
    note = fields.Text(
        string='Note',
        help='Additional notes'
    )

    # Related fields
    planning_state = fields.Selection(
        related='planning_id.state',
        string='Planning Status',
        store=True
    )
    company_id = fields.Many2one(
        related='planning_id.company_id',
        string='Company',
        store=True
    )

    # Display name
    display_name = fields.Char(
        string='Display Name',
        compute='_compute_display_name',
        store=True
    )

    _employee_date_uniq = models.Constraint(
        'UNIQUE(planning_workrole_id, employee_id, date)',
        'Each employee can only have one entry per day per workrole!',
    )

    @api.depends('hour_start', 'hour_end', 'is_day_off', 'is_leave')
    def _compute_duration(self):
        for entry in self:
            if entry.is_day_off or entry.is_leave:
                entry.duration = 0.0
            elif entry.hour_start is not None and entry.hour_end is not None:
                if entry.hour_end >= entry.hour_start:
                    entry.duration = entry.hour_end - entry.hour_start
                else:
                    # Overnight shift
                    entry.duration = (24 - entry.hour_start) + entry.hour_end
            else:
                entry.duration = 0.0

    @api.depends('date', 'hour_start', 'hour_end', 'is_day_off', 'is_leave')
    def _compute_datetime_fields(self):
        """Compute datetime fields for timeline view."""
        # Standard contract hours for day off/leave display (8 hours)
        DEFAULT_START_HOUR = 8
        DEFAULT_END_HOUR = 16

        for entry in self:
            if not entry.date:
                entry.date_start = False
                entry.date_end = False
                continue

            if entry.is_day_off or entry.is_leave:
                # Day off/leave: show as standard 8-hour block (contract time only)
                # We don't own their personal time outside contract hours!
                entry.date_start = datetime.combine(
                    entry.date,
                    datetime.min.time().replace(hour=DEFAULT_START_HOUR)
                )
                entry.date_end = datetime.combine(
                    entry.date,
                    datetime.min.time().replace(hour=DEFAULT_END_HOUR)
                )
            else:
                # Convert float hours to time
                start_hour = int(entry.hour_start or 0)
                start_min = int(((entry.hour_start or 0) % 1) * 60)
                end_hour = int(entry.hour_end or 0)
                end_min = int(((entry.hour_end or 0) % 1) * 60)

                entry.date_start = datetime.combine(
                    entry.date,
                    datetime.min.time().replace(hour=start_hour, minute=start_min)
                )

                # Handle overnight shift
                end_date = entry.date
                if entry.hour_end < entry.hour_start:
                    end_date = entry.date + timedelta(days=1)

                entry.date_end = datetime.combine(
                    end_date,
                    datetime.min.time().replace(hour=end_hour, minute=end_min)
                )

    @api.depends('shift_type_id', 'is_day_off', 'is_leave')
    def _compute_color(self):
        """Compute color based on shift type or status."""
        for entry in self:
            if entry.is_leave:
                entry.color = 9  # Purple for leave
            elif entry.is_day_off:
                entry.color = 7  # Gray for day off
            elif entry.shift_type_id:
                entry.color = entry.shift_type_id.color
            else:
                entry.color = 0  # Default

    @api.depends('employee_id', 'date', 'shift_type_id')
    def _compute_display_name(self):
        for entry in self:
            parts = []
            if entry.employee_id:
                parts.append(entry.employee_id.name)
            if entry.date:
                parts.append(str(entry.date))
            if entry.shift_type_id:
                parts.append(entry.shift_type_id.name)
            elif entry.is_day_off:
                parts.append('Day Off')
            elif entry.is_leave:
                parts.append('Leave')
            entry.display_name = ' - '.join(parts) if parts else 'New Entry'

    @api.constrains('hour_start', 'hour_end')
    def _check_hours(self):
        for entry in self:
            if entry.hour_start is not None and (entry.hour_start < 0 or entry.hour_start > 24):
                raise ValidationError(_('Start time must be between 0 and 24.'))
            if entry.hour_end is not None and (entry.hour_end < 0 or entry.hour_end > 24):
                raise ValidationError(_('End time must be between 0 and 24.'))

    @api.onchange('shift_type_id')
    def _onchange_shift_type_id(self):
        """Auto-fill times from shift type."""
        if self.shift_type_id:
            self.hour_start = self.shift_type_id.hour_start
            self.hour_end = self.shift_type_id.hour_end
            self.is_day_off = self.shift_type_id.is_day_off

    @api.onchange('is_day_off')
    def _onchange_is_day_off(self):
        """Clear times when day off is selected."""
        if self.is_day_off:
            self.hour_start = 0
            self.hour_end = 0
            self.shift_type_id = False

    @api.onchange('is_leave')
    def _onchange_is_leave(self):
        """Clear shift when leave is marked."""
        if self.is_leave:
            self.hour_start = 0
            self.hour_end = 0
            self.shift_type_id = False
            self.is_day_off = False

    # ===================
    # Helper Methods
    # ===================

    def get_shift_label(self):
        """Get human-readable shift label."""
        self.ensure_one()
        if self.is_leave:
            return self.leave_type or 'Leave'
        if self.is_day_off:
            return 'Day Off'
        if self.shift_type_id:
            return self.shift_type_id.name
        if self.hour_start is not None and self.hour_end is not None:
            start = '{:02d}:{:02d}'.format(int(self.hour_start), int((self.hour_start % 1) * 60))
            end = '{:02d}:{:02d}'.format(int(self.hour_end), int((self.hour_end % 1) * 60))
            return f'{start}-{end}'
        return 'Unassigned'
