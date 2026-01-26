# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PlanningTemplate(models.Model):
    _name = 'itx.schedule.planning.template'
    _description = 'Schedule Planning Template'
    _order = 'sequence, name'

    name = fields.Char(
        string='Name',
        required=True,
        help='Template name, e.g., 3 Shifts 4 Teams Rotation'
    )
    code = fields.Char(
        string='Code',
        required=True,
        help='Short code for this template'
    )
    description = fields.Text(
        string='Description',
        help='Detailed description of this template'
    )
    is_default = fields.Boolean(
        string='Default',
        default=False,
        help='Use as default template'
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Display order'
    )

    # Rotation Settings
    rotation_direction = fields.Selection(
        selection=[
            ('none', 'No Rotation (Fixed Shift)'),
            ('forward', 'Forward (Morning → Afternoon → Night)'),
            ('backward', 'Backward (Morning → Night → Afternoon)'),
        ],
        string='Rotation Direction',
        default='none',
        required=True,
        help='Direction of shift rotation between periods. None = fixed shift (no rotation)'
    )
    rotation_period_count = fields.Integer(
        string='Rotation Period Count',
        default=1,
        required=True,
        help='Change shift every N periods (1 = every period, 2 = every 2 periods)'
    )
    shifts_per_day = fields.Integer(
        string='Shifts per Day',
        default=3,
        required=True,
        help='Number of shifts per day'
    )

    # Work-Off Pattern
    pattern_id = fields.Many2one(
        comodel_name='itx.schedule.workoff.pattern',
        string='Work-Off Pattern',
        required=True,
        help='Work-off pattern to use (e.g., 7-On 3-Off)'
    )
    work_days = fields.Integer(
        related='pattern_id.work_days',
        string='Work Days',
        store=True
    )
    off_days = fields.Integer(
        related='pattern_id.off_days',
        string='Off Days',
        store=True
    )
    pattern_length = fields.Integer(
        related='pattern_id.pattern_length',
        string='Pattern Length',
        store=True
    )

    # Shift Duration
    shift_duration = fields.Float(
        string='Shift Duration (Hours)',
        default=8.0,
        required=True,
        help='Working hours per shift (excluding break)'
    )
    break_duration = fields.Float(
        string='Break Duration (Hours)',
        default=1.0,
        required=True,
        help='Break time in hours'
    )
    total_shift_hours = fields.Float(
        string='Total Shift Hours',
        compute='_compute_total_shift_hours',
        store=True,
        help='Total shift time (work + break)'
    )

    # Day Break Pattern
    day_break_pattern = fields.Selection(
        selection=[
            ('4w1b4w', '4 Work - 1 Break - 4 Work'),
            ('5w1b3w', '5 Work - 1 Break - 3 Work'),
            ('custom', 'Custom'),
        ],
        string='Day Break Pattern',
        default='4w1b4w',
        help='Pattern of work and break within a shift'
    )
    day_break_work_before = fields.Integer(
        string='Work Before Break (Hours)',
        default=4,
        help='Hours of work before the break'
    )
    day_break_work_after = fields.Integer(
        string='Work After Break (Hours)',
        default=4,
        help='Hours of work after the break'
    )

    # Shift Times
    shift_time_ids = fields.One2many(
        comodel_name='itx.schedule.planning.template.shift',
        inverse_name='template_id',
        string='Shift Times',
        help='Define start/end times for each shift'
    )

    active = fields.Boolean(
        string='Active',
        default=True,
        help='Set to False to hide without deleting'
    )

    _code_uniq = models.Constraint(
        'UNIQUE(code)',
        'Template code must be unique!',
    )

    @api.depends('shift_duration', 'break_duration')
    def _compute_total_shift_hours(self):
        for record in self:
            record.total_shift_hours = record.shift_duration + record.break_duration

    @api.constrains('rotation_period_count')
    def _check_rotation_period_count(self):
        for record in self:
            if record.rotation_period_count < 1:
                raise ValidationError(_('Rotation period count must be at least 1.'))

    @api.constrains('shifts_per_day')
    def _check_shifts_per_day(self):
        for record in self:
            if record.shifts_per_day < 1:
                raise ValidationError(_('Shifts per day must be at least 1.'))

    @api.constrains('shift_duration', 'break_duration')
    def _check_durations(self):
        for record in self:
            if record.shift_duration <= 0:
                raise ValidationError(_('Shift duration must be greater than 0.'))
            if record.break_duration < 0:
                raise ValidationError(_('Break duration cannot be negative.'))

    @api.constrains('is_default')
    def _check_single_default(self):
        """Ensure only one template is set as default."""
        for record in self:
            if record.is_default:
                other_defaults = self.search([
                    ('is_default', '=', True),
                    ('id', '!=', record.id)
                ])
                if other_defaults:
                    other_defaults.write({'is_default': False})

    @api.onchange('day_break_pattern')
    def _onchange_day_break_pattern(self):
        if self.day_break_pattern == '4w1b4w':
            self.day_break_work_before = 4
            self.day_break_work_after = 4
        elif self.day_break_pattern == '5w1b3w':
            self.day_break_work_before = 5
            self.day_break_work_after = 3

    @api.model
    def get_default_template(self):
        """Return the default template or first active template."""
        template = self.search([('is_default', '=', True)], limit=1)
        if not template:
            template = self.search([], limit=1)
        return template


class PlanningTemplateShift(models.Model):
    _name = 'itx.schedule.planning.template.shift'
    _description = 'Template Shift Time'
    _order = 'sequence'

    template_id = fields.Many2one(
        comodel_name='itx.schedule.planning.template',
        string='Template',
        required=True,
        ondelete='cascade'
    )
    name = fields.Char(
        string='Name',
        required=True,
        help='Shift name, e.g., Morning, Afternoon, Night'
    )
    code = fields.Char(
        string='Code',
        required=True,
        help='Short code, e.g., MORNING, AFTERNOON, NIGHT'
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        required=True,
        help='Order in rotation (1, 2, 3...)'
    )
    hour_start = fields.Float(
        string='Start Time',
        required=True,
        help='Shift start time (0-24)'
    )
    hour_end = fields.Float(
        string='End Time',
        required=True,
        help='Shift end time (0-24)'
    )
    is_overnight = fields.Boolean(
        string='Overnight',
        compute='_compute_is_overnight',
        store=True,
        help='Shift spans midnight'
    )
    color = fields.Integer(
        string='Color',
        default=0,
        help='Color for display'
    )

    @api.depends('hour_start', 'hour_end')
    def _compute_is_overnight(self):
        for record in self:
            record.is_overnight = record.hour_end < record.hour_start

    def name_get(self):
        result = []
        for record in self:
            start = '{:02d}:{:02d}'.format(int(record.hour_start), int((record.hour_start % 1) * 60))
            end = '{:02d}:{:02d}'.format(int(record.hour_end), int((record.hour_end % 1) * 60))
            name = f'{record.name} ({start}-{end})'
            result.append((record.id, name))
        return result
