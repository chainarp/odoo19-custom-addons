# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class WorkoffPattern(models.Model):
    _name = 'itx.schedule.workoff.pattern'
    _description = 'Work-Off Pattern'
    _order = 'sequence, name'

    name = fields.Char(
        string='Name',
        required=True,
        help='Pattern name, e.g., 7-On 3-Off or Mon-Fri'
    )
    code = fields.Char(
        string='Code',
        required=True,
        help='Short code, e.g., 7ON3OFF or WEEKDAY'
    )

    # Pattern Type
    pattern_type = fields.Selection(
        selection=[
            ('consecutive', 'Consecutive (e.g., 7-On 3-Off)'),
            ('weekday', 'Weekday-based (e.g., Mon-Fri)'),
        ],
        string='Pattern Type',
        default='consecutive',
        required=True,
        help='Consecutive: fixed number of work/off days in sequence. '
             'Weekday: specific days of the week.'
    )

    # Consecutive pattern fields
    work_days = fields.Integer(
        string='Work Days',
        default=7,
        help='Number of consecutive working days (for consecutive pattern)'
    )
    off_days = fields.Integer(
        string='Off Days',
        default=3,
        help='Number of consecutive days off (for consecutive pattern)'
    )
    pattern_length = fields.Integer(
        string='Pattern Length',
        compute='_compute_pattern_length',
        store=True,
        help='Total days in pattern'
    )

    # Weekday pattern fields (True = Work, False = Off)
    weekday_mon = fields.Boolean(
        string='Monday',
        default=True,
        help='Work on Monday'
    )
    weekday_tue = fields.Boolean(
        string='Tuesday',
        default=True,
        help='Work on Tuesday'
    )
    weekday_wed = fields.Boolean(
        string='Wednesday',
        default=True,
        help='Work on Wednesday'
    )
    weekday_thu = fields.Boolean(
        string='Thursday',
        default=True,
        help='Work on Thursday'
    )
    weekday_fri = fields.Boolean(
        string='Friday',
        default=True,
        help='Work on Friday'
    )
    weekday_sat = fields.Boolean(
        string='Saturday',
        default=False,
        help='Work on Saturday'
    )
    weekday_sun = fields.Boolean(
        string='Sunday',
        default=False,
        help='Work on Sunday'
    )
    weekday_work_days = fields.Integer(
        string='Work Days/Week',
        compute='_compute_weekday_work_days',
        store=True,
        help='Number of work days per week'
    )

    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Display order'
    )
    is_default = fields.Boolean(
        string='Default',
        default=False,
        help='Use as default pattern'
    )
    active = fields.Boolean(
        string='Active',
        default=True,
        help='Set to False to hide without deleting'
    )

    _code_uniq = models.Constraint(
        'UNIQUE(code)',
        'Pattern code must be unique!',
    )

    @api.depends('pattern_type', 'work_days', 'off_days')
    def _compute_pattern_length(self):
        for record in self:
            if record.pattern_type == 'consecutive':
                record.pattern_length = (record.work_days or 0) + (record.off_days or 0)
            else:
                # Weekday pattern always repeats every 7 days
                record.pattern_length = 7

    @api.depends('weekday_mon', 'weekday_tue', 'weekday_wed', 'weekday_thu',
                 'weekday_fri', 'weekday_sat', 'weekday_sun')
    def _compute_weekday_work_days(self):
        for record in self:
            record.weekday_work_days = sum([
                record.weekday_mon or False,
                record.weekday_tue or False,
                record.weekday_wed or False,
                record.weekday_thu or False,
                record.weekday_fri or False,
                record.weekday_sat or False,
                record.weekday_sun or False,
            ])

    @api.constrains('pattern_type', 'work_days', 'off_days')
    def _check_consecutive_days(self):
        for record in self:
            if record.pattern_type == 'consecutive':
                if record.work_days <= 0:
                    raise ValidationError(_('Work days must be greater than 0.'))
                if record.off_days < 0:
                    raise ValidationError(_('Off days cannot be negative.'))

    @api.constrains('pattern_type', 'weekday_mon', 'weekday_tue', 'weekday_wed',
                    'weekday_thu', 'weekday_fri', 'weekday_sat', 'weekday_sun')
    def _check_weekday_pattern(self):
        for record in self:
            if record.pattern_type == 'weekday':
                if record.weekday_work_days == 0:
                    raise ValidationError(_('At least one work day must be selected.'))

    @api.constrains('is_default')
    def _check_single_default(self):
        """Ensure only one pattern is set as default."""
        for record in self:
            if record.is_default:
                other_defaults = self.search([
                    ('is_default', '=', True),
                    ('id', '!=', record.id)
                ])
                if other_defaults:
                    other_defaults.write({'is_default': False})

    def name_get(self):
        result = []
        for record in self:
            if record.pattern_type == 'consecutive':
                name = f'{record.name} ({record.work_days}-On {record.off_days}-Off)'
            else:
                # Build weekday string
                days = []
                if record.weekday_mon: days.append('Mon')
                if record.weekday_tue: days.append('Tue')
                if record.weekday_wed: days.append('Wed')
                if record.weekday_thu: days.append('Thu')
                if record.weekday_fri: days.append('Fri')
                if record.weekday_sat: days.append('Sat')
                if record.weekday_sun: days.append('Sun')
                name = f'{record.name} ({", ".join(days)})'
            result.append((record.id, name))
        return result

    @api.model
    def get_default_pattern(self):
        """Return the default pattern or first active pattern."""
        pattern = self.search([('is_default', '=', True)], limit=1)
        if not pattern:
            pattern = self.search([], limit=1)
        return pattern

    def is_work_day(self, date):
        """
        Check if a given date is a work day according to this pattern.

        For consecutive patterns, this requires knowing the start date of the cycle.
        For weekday patterns, it's based on the day of the week.

        Args:
            date: date object to check

        Returns:
            bool: True if work day, False if off day
        """
        self.ensure_one()
        if self.pattern_type == 'weekday':
            weekday = date.weekday()  # 0=Monday, 6=Sunday
            weekday_map = {
                0: self.weekday_mon,
                1: self.weekday_tue,
                2: self.weekday_wed,
                3: self.weekday_thu,
                4: self.weekday_fri,
                5: self.weekday_sat,
                6: self.weekday_sun,
            }
            return weekday_map.get(weekday, False)
        else:
            # For consecutive pattern, need cycle_start_date
            # This should be called with additional context
            raise ValidationError(_(
                'For consecutive patterns, use is_work_day_consecutive() '
                'with cycle_start_date parameter.'
            ))

    def is_work_day_consecutive(self, date, cycle_start_date):
        """
        Check if a given date is a work day for consecutive pattern.

        Args:
            date: date object to check
            cycle_start_date: date when the work cycle started

        Returns:
            bool: True if work day, False if off day
        """
        self.ensure_one()
        if self.pattern_type != 'consecutive':
            return self.is_work_day(date)

        days_since_start = (date - cycle_start_date).days
        position_in_cycle = days_since_start % self.pattern_length

        # First work_days positions are work days
        return position_in_cycle < self.work_days
