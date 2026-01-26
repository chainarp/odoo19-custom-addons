# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class EmployeeWorkteam(models.Model):
    _name = 'itx.employee.workteam'
    _description = 'Employee Work Team'
    _order = 'workrole_id, sequence, name'

    name = fields.Char(
        string='Name',
        required=True,
        help='Team name, e.g., Team A, Team B'
    )
    code = fields.Char(
        string='Code',
        required=True,
        help='Short code, e.g., A, B, C, D'
    )
    workrole_id = fields.Many2one(
        comodel_name='itx.employee.workrole',
        string='Work Role',
        required=True,
        ondelete='cascade',
        help='Work role this team belongs to'
    )
    employee_ids = fields.Many2many(
        comodel_name='hr.employee',
        relation='itx_workteam_employee_rel',
        column1='workteam_id',
        column2='employee_id',
        string='Members',
        help='Team members'
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Rotation sequence order'
    )
    color = fields.Integer(
        string='Color',
        default=0,
        help='Color for display in timeline/kanban views'
    )
    active = fields.Boolean(
        string='Active',
        default=True,
        help='Set to False to hide without deleting'
    )

    # Computed fields
    employee_count = fields.Integer(
        string='Member Count',
        compute='_compute_employee_count',
        store=True
    )

    _code_workrole_uniq = models.Constraint(
        'UNIQUE(code, workrole_id)',
        'Team code must be unique within a work role!',
    )

    @api.depends('employee_ids')
    def _compute_employee_count(self):
        for record in self:
            record.employee_count = len(record.employee_ids)

    @api.constrains('employee_ids', 'workrole_id')
    def _check_employees_in_workrole(self):
        """Ensure team members are also in the parent workrole."""
        for record in self:
            if record.workrole_id and record.employee_ids:
                workrole_employees = record.workrole_id.employee_ids
                invalid_employees = record.employee_ids - workrole_employees
                if invalid_employees:
                    raise ValidationError(_(
                        'The following employees are not in the work role "%s": %s'
                    ) % (record.workrole_id.name, ', '.join(invalid_employees.mapped('name'))))

    def name_get(self):
        result = []
        for record in self:
            if record.workrole_id:
                name = f'{record.workrole_id.name} / {record.name}'
            else:
                name = record.name
            result.append((record.id, name))
        return result

    @api.model
    def _name_search(self, name, domain=None, operator='ilike', limit=None, order=None):
        domain = domain or []
        if name:
            domain = ['|', '|',
                      ('code', operator, name),
                      ('name', operator, name),
                      ('workrole_id.name', operator, name)] + domain
        return self._search(domain, limit=limit, order=order)
