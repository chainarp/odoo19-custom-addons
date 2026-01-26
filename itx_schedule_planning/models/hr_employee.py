# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    employee_number = fields.Char(
        string='Employee Number',
        index=True,
        tracking=True,
        help='Employee number assigned by company (e.g., EMP001, A1234)'
    )
    workrole_id = fields.Many2one(
        comodel_name='itx.employee.workrole',
        string='Work Role',
        tracking=True,
        help='Work role this employee is assigned to (e.g., APM Driver, Operator)'
    )
    workteam_id = fields.Many2one(
        comodel_name='itx.employee.workteam',
        string='Work Team',
        tracking=True,
        domain="[('workrole_id', '=', workrole_id)]",
        help='Team within the work role (e.g., Team A, Team B)'
    )

    _employee_number_uniq = models.Constraint(
        'UNIQUE(employee_number)',
        'Employee number must be unique!',
    )

    @api.onchange('workrole_id')
    def _onchange_workrole_id(self):
        """Clear workteam when workrole changes."""
        if self.workrole_id:
            # Check if current workteam belongs to new workrole
            if self.workteam_id and self.workteam_id.workrole_id != self.workrole_id:
                self.workteam_id = False
        else:
            self.workteam_id = False

    @api.constrains('workrole_id', 'workteam_id')
    def _check_workteam_workrole(self):
        """Ensure workteam belongs to the selected workrole."""
        for employee in self:
            if employee.workteam_id and employee.workrole_id:
                if employee.workteam_id.workrole_id != employee.workrole_id:
                    raise ValidationError(_(
                        'Work Team "%(team)s" does not belong to Work Role "%(role)s".',
                        team=employee.workteam_id.name,
                        role=employee.workrole_id.name
                    ))
