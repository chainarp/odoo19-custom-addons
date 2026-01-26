# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SchedulePlanningWorkrole(models.Model):
    """
    Schedule Planning Workrole - Level 2
    Configuration per work role within a planning
    """
    _name = 'itx.schedule.planning.workrole'
    _description = 'Schedule Planning Work Role'
    _order = 'sequence, id'

    planning_id = fields.Many2one(
        comodel_name='itx.schedule.planning',
        string='Planning',
        required=True,
        ondelete='cascade',
        index=True
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10
    )

    # Link to master data
    workrole_id = fields.Many2one(
        comodel_name='itx.employee.workrole',
        string='Work Role',
        required=True,
        ondelete='restrict',
        help='Work role from master data (e.g., APM Driver, Operator)'
    )
    template_id = fields.Many2one(
        comodel_name='itx.schedule.planning.template',
        string='Template',
        required=True,
        ondelete='restrict',
        help='Schedule template to use for generation'
    )

    # Responsible person for this workrole
    responsible_id = fields.Many2one(
        comodel_name='res.users',
        string='Responsible',
        help='Manager responsible for this work role schedule'
    )

    # Generation settings
    min_employees_per_shift = fields.Integer(
        string='Min Employees per Shift',
        default=1,
        required=True,
        help='Minimum number of employees required per shift'
    )

    # Team snapshots for carry-over to next period
    team_snapshot_ids = fields.One2many(
        comodel_name='itx.schedule.planning.workrole.team',
        inverse_name='planning_workrole_id',
        string='Team Snapshots',
        copy=True,
        help='Initial/final values per team for generation continuity'
    )

    # Entries (Level 3)
    entry_ids = fields.One2many(
        comodel_name='itx.schedule.planning.workrole.entry',
        inverse_name='planning_workrole_id',
        string='Schedule Entries',
        copy=False
    )

    # Related fields for easy access
    planning_state = fields.Selection(
        related='planning_id.state',
        string='Planning Status',
        store=True
    )
    date_start = fields.Date(
        related='planning_id.date_start',
        string='Start Date',
        store=True
    )
    date_end = fields.Date(
        related='planning_id.date_end',
        string='End Date',
        store=True
    )

    # Computed fields
    employee_count = fields.Integer(
        string='Employee Count',
        compute='_compute_counts',
        store=True
    )
    entry_count = fields.Integer(
        string='Entry Count',
        compute='_compute_counts',
        store=True
    )
    gap_count = fields.Integer(
        string='Gap Count',
        compute='_compute_gap_count',
        help='Number of understaffed shifts'
    )

    _planning_workrole_uniq = models.Constraint(
        'UNIQUE(planning_id, workrole_id)',
        'Each work role can only appear once per planning!',
    )

    @api.depends('entry_ids', 'entry_ids.employee_id')
    def _compute_counts(self):
        for record in self:
            record.entry_count = len(record.entry_ids)
            record.employee_count = len(record.entry_ids.mapped('employee_id'))

    def _compute_gap_count(self):
        # TODO: Implement gap detection
        for record in self:
            record.gap_count = 0

    @api.constrains('min_employees_per_shift')
    def _check_min_employees(self):
        for record in self:
            if record.min_employees_per_shift < 1:
                raise ValidationError(_('Minimum employees per shift must be at least 1.'))

    def name_get(self):
        result = []
        for record in self:
            name = f'{record.planning_id.name} / {record.workrole_id.name}'
            result.append((record.id, name))
        return result

    # ===================
    # Generation Helpers
    # ===================

    def prepare_team_snapshots(self):
        """
        Initialize team snapshots from master data.
        Called when adding a workrole to planning.
        """
        self.ensure_one()
        TeamSnapshot = self.env['itx.schedule.planning.workrole.team']

        # Get teams from workrole master data
        teams = self.workrole_id.team_ids

        for team in teams:
            # Check if snapshot already exists
            existing = self.team_snapshot_ids.filtered(
                lambda t: t.team_id == team
            )
            if not existing:
                TeamSnapshot.create({
                    'planning_workrole_id': self.id,
                    'team_id': team.id,
                    'initial_shift_sequence': 1,
                    'initial_day_in_pattern': 1,
                })

    def copy_snapshots_from_previous(self, previous_workrole):
        """
        Copy final values from previous period as initial values.
        """
        self.ensure_one()
        for prev_snapshot in previous_workrole.team_snapshot_ids:
            my_snapshot = self.team_snapshot_ids.filtered(
                lambda t: t.team_id == prev_snapshot.team_id
            )
            if my_snapshot:
                my_snapshot.write({
                    'initial_shift_sequence': prev_snapshot.final_shift_sequence or 1,
                    'initial_day_in_pattern': prev_snapshot.final_day_in_pattern or 1,
                })


class SchedulePlanningWorkroleTeam(models.Model):
    """
    Team Snapshot - carries state between periods
    Stores initial and final values for continuous schedule generation
    """
    _name = 'itx.schedule.planning.workrole.team'
    _description = 'Schedule Planning Team Snapshot'
    _order = 'sequence, id'

    planning_workrole_id = fields.Many2one(
        comodel_name='itx.schedule.planning.workrole',
        string='Planning Workrole',
        required=True,
        ondelete='cascade',
        index=True
    )
    team_id = fields.Many2one(
        comodel_name='itx.employee.workteam',
        string='Team',
        required=True,
        ondelete='restrict'
    )
    sequence = fields.Integer(
        related='team_id.sequence',
        string='Sequence',
        store=True
    )

    # Initial values (input for generation)
    initial_shift_sequence = fields.Integer(
        string='Initial Shift',
        default=1,
        required=True,
        help='Starting shift sequence (1=Morning, 2=Afternoon, 3=Night)'
    )
    initial_day_in_pattern = fields.Integer(
        string='Initial Day in Pattern',
        default=1,
        required=True,
        help='Starting day number in work-off pattern (e.g., 1-10 for 7on-3off)'
    )

    # Final values (computed after generation, used for next period)
    final_shift_sequence = fields.Integer(
        string='Final Shift',
        readonly=True,
        help='Ending shift sequence after this period'
    )
    final_day_in_pattern = fields.Integer(
        string='Final Day in Pattern',
        readonly=True,
        help='Ending day number in pattern after this period'
    )

    _workrole_team_uniq = models.Constraint(
        'UNIQUE(planning_workrole_id, team_id)',
        'Each team can only appear once per workrole planning!',
    )

    def name_get(self):
        result = []
        for record in self:
            name = f'{record.team_id.name} (Shift {record.initial_shift_sequence}, Day {record.initial_day_in_pattern})'
            result.append((record.id, name))
        return result
