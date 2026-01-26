# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class EmployeeWorkrole(models.Model):
    _name = 'itx.employee.workrole'
    _description = 'Employee Work Role'
    _order = 'sequence, name'

    name = fields.Char(
        string='Name',
        required=True,
        help='Work role name, e.g., APM Driver, APM Operator, Maintenance'
    )
    code = fields.Char(
        string='Code',
        required=True,
        help='Short code, e.g., DRIVER, OPERATOR, MAINT'
    )
    description = fields.Text(
        string='Description',
        help='Detailed description of this work role'
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Display order'
    )
    team_ids = fields.One2many(
        comodel_name='itx.employee.workteam',
        inverse_name='workrole_id',
        string='Teams',
        help='Teams within this work role'
    )
    employee_ids = fields.Many2many(
        comodel_name='hr.employee',
        relation='itx_workrole_employee_rel',
        column1='workrole_id',
        column2='employee_id',
        string='Employees',
        help='Employees qualified for this work role'
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
        string='Employee Count',
        compute='_compute_employee_count',
        store=True
    )
    team_count = fields.Integer(
        string='Team Count',
        compute='_compute_team_count',
        store=True
    )

    _code_uniq = models.Constraint(
        'UNIQUE(code)',
        'Work role code must be unique!',
    )

    @api.depends('employee_ids')
    def _compute_employee_count(self):
        for record in self:
            record.employee_count = len(record.employee_ids)

    @api.depends('team_ids')
    def _compute_team_count(self):
        for record in self:
            record.team_count = len(record.team_ids)

    @api.constrains('code')
    def _check_code(self):
        for record in self:
            if record.code and not record.code.replace('_', '').isalnum():
                raise ValidationError(_('Code must contain only alphanumeric characters and underscores.'))

    def name_get(self):
        result = []
        for record in self:
            name = f'[{record.code}] {record.name}' if record.code else record.name
            result.append((record.id, name))
        return result

    @api.model
    def _name_search(self, name, domain=None, operator='ilike', limit=None, order=None):
        domain = domain or []
        if name:
            domain = ['|', ('code', operator, name), ('name', operator, name)] + domain
        return self._search(domain, limit=limit, order=order)
