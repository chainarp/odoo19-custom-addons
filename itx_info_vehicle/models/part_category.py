# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ItxInfoVehiclePartCategory(models.Model):
    _name = 'itx.info.vehicle.part.category'
    _description = 'Vehicle Part Category'
    _parent_name = 'parent_id'
    _parent_store = True
    _order = 'complete_name'

    # === Standard Fields ===
    code = fields.Char(
        string='Code',
        required=True,
        index=True,
        help='Category code, e.g., ENGINE, TRANS',
    )
    name = fields.Char(
        string='Name',
        required=True,
        index=True,
        help='Category name',
    )
    desc = fields.Text(
        string='Description',
        help='Additional description',
    )
    abbr = fields.Char(
        string='Abbreviation',
        size=10,
        required=True,
        index=True,
        help='Abbreviation for Internal Reference, e.g., ENG, TRN',
    )

    # === Hierarchy Fields ===
    parent_id = fields.Many2one(
        comodel_name='itx.info.vehicle.part.category',
        string='Parent Category',
        index=True,
        ondelete='cascade',
    )
    child_ids = fields.One2many(
        comodel_name='itx.info.vehicle.part.category',
        inverse_name='parent_id',
        string='Child Categories',
    )
    parent_path = fields.Char(
        index=True,
        unaccent=False,
    )
    default_location_id = fields.Many2one(
        comodel_name='stock.location',
        string='Default Stock Location',
        domain="[('usage', '=', 'internal')]",
        help='Default destination when a part of this category is stocked in '
             'from dismantling. Used as fallback if the part template has no override.',
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )

    # === Computed Fields ===
    complete_name = fields.Char(
        string='Complete Name',
        compute='_compute_complete_name',
        recursive=True,
        store=True,
    )
    child_count = fields.Integer(
        string='Child Count',
        compute='_compute_child_count',
    )

    # === Constraints ===
    _sql_constraints = [
        ('code_uniq', 'UNIQUE(code)', 'Part category code must be unique!'),
        ('abbr_uniq', 'UNIQUE(abbr)', 'Part category abbreviation must be unique!'),
    ]

    @api.constrains('parent_id')
    def _check_parent_recursion(self):
        if not self._check_recursion():
            raise ValidationError(
                'Error! You cannot create recursive categories.'
            )

    # === Compute Methods ===
    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for rec in self:
            if rec.parent_id:
                rec.complete_name = f"{rec.parent_id.complete_name} / {rec.name}"
            else:
                rec.complete_name = rec.name

    @api.depends('child_ids')
    def _compute_child_count(self):
        for rec in self:
            rec.child_count = len(rec.child_ids)

    # === Onchange Methods ===
    @api.onchange('name')
    def _onchange_name_set_abbr(self):
        """Auto-generate abbr from name (first 3 uppercase chars)"""
        if self.name and not self.abbr:
            clean = ''.join(c for c in self.name if c.isalnum())
            self.abbr = clean[:3].upper()

    @api.onchange('name')
    def _onchange_name_set_code(self):
        """Auto-generate code from name (uppercase)"""
        if self.name and not self.code:
            self.code = self.name.upper().replace(' ', '_')

    # === CRUD Methods ===
    def name_get(self):
        return [(rec.id, f"[{rec.abbr}] {rec.complete_name}") for rec in self]
