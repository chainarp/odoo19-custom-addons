# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ShiftType(models.Model):
    _name = 'itx.schedule.shift.type'
    _description = 'Shift Type'
    _order = 'sequence, name'

    name = fields.Char(
        string='Name',
        required=True,
        translate=True,
        help='Shift name, e.g., Morning Shift, Afternoon Shift, Night Shift'
    )
    code = fields.Char(
        string='Code',
        required=True,
        help='Short code, e.g., MORNING, AFTERNOON, NIGHT'
    )
    hour_start = fields.Float(
        string='Start Time',
        required=True,
        default=6.0,
        help='Shift start time (0-24), e.g., 6.0 = 06:00'
    )
    hour_end = fields.Float(
        string='End Time',
        required=True,
        default=14.0,
        help='Shift end time (0-24), e.g., 14.0 = 14:00'
    )
    duration = fields.Float(
        string='Duration (Hours)',
        compute='_compute_duration',
        store=True,
        help='Shift duration in hours'
    )
    is_overnight = fields.Boolean(
        string='Overnight',
        compute='_compute_is_overnight',
        store=True,
        help='Shift spans midnight'
    )
    is_day_off = fields.Boolean(
        string='Day Off',
        default=False,
        help='This is a day off (no working hours)'
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Display order and rotation sequence'
    )
    color = fields.Integer(
        string='Color',
        default=0,
        help='Color for display in timeline views'
    )
    active = fields.Boolean(
        string='Active',
        default=True,
        help='Set to False to hide without deleting'
    )

    _code_uniq = models.Constraint(
        'UNIQUE(code)',
        'Shift type code must be unique!',
    )

    @api.depends('hour_start', 'hour_end', 'is_day_off')
    def _compute_duration(self):
        for record in self:
            if record.is_day_off:
                record.duration = 0.0
            elif record.hour_end >= record.hour_start:
                record.duration = record.hour_end - record.hour_start
            else:
                # Overnight shift
                record.duration = (24.0 - record.hour_start) + record.hour_end

    @api.depends('hour_start', 'hour_end')
    def _compute_is_overnight(self):
        for record in self:
            record.is_overnight = record.hour_end < record.hour_start

    @api.constrains('hour_start', 'hour_end')
    def _check_hours(self):
        for record in self:
            if not record.is_day_off:
                if not (0 <= record.hour_start < 24):
                    raise ValidationError(_('Start time must be between 0 and 24.'))
                if not (0 <= record.hour_end < 24):
                    raise ValidationError(_('End time must be between 0 and 24.'))

    def name_get(self):
        result = []
        for record in self:
            if record.is_day_off:
                name = f'{record.name} (Day Off)'
            else:
                start = '{:02d}:{:02d}'.format(int(record.hour_start), int((record.hour_start % 1) * 60))
                end = '{:02d}:{:02d}'.format(int(record.hour_end), int((record.hour_end % 1) * 60))
                name = f'{record.name} ({start}-{end})'
            result.append((record.id, name))
        return result

    @api.model
    def _name_search(self, name, domain=None, operator='ilike', limit=None, order=None):
        domain = domain or []
        if name:
            domain = ['|', ('code', operator, name), ('name', operator, name)] + domain
        return self._search(domain, limit=limit, order=order)
