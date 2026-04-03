# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ItxInfoVehicleTemplatePart(models.Model):
    _name = 'itx.info.vehicle.template.part'
    _description = 'Vehicle Part Template'
    _order = 'category_id, name'

    # === Standard Fields ===
    code = fields.Char(
        string='Code',
        required=True,
        index=True,
        help='Unique code, e.g., HEADLIGHT_LH, BUMPER_FR',
    )
    name = fields.Char(
        string='Name (Thai)',
        required=True,
        index=True,
        help='Thai name, self-explanatory, e.g., ไฟหน้าซ้าย, กันชนหน้า',
    )
    name_en = fields.Char(
        string='Name (English)',
        index=True,
        help='English name, e.g., Left Headlight, Front Bumper',
    )
    abbr = fields.Char(
        string='Abbreviation',
        size=10,
        required=True,
        index=True,
        help='Abbreviation for Internal Reference, e.g., HLT-L, BMP-F',
    )
    desc = fields.Text(
        string='Description',
        help='Additional description and context',
    )

    # === Optional Link ===
    category_id = fields.Many2one(
        comodel_name='itx.info.vehicle.part.category',
        string='Default Category',
        index=True,
        help='Suggested part category',
    )

    active = fields.Boolean(
        string='Active',
        default=True,
    )

    # === Constraints ===
    _sql_constraints = [
        ('code_uniq', 'UNIQUE(code)', 'Part template code must be unique!'),
        ('abbr_uniq', 'UNIQUE(abbr)', 'Part template abbreviation must be unique!'),
    ]

    # === Onchange Methods ===
    @api.onchange('name')
    def _onchange_name_set_code(self):
        """Auto-generate code from Thai name"""
        if self.name and not self.code:
            # Simple transliteration for common words
            code = self.name.replace(' ', '_').replace('(', '').replace(')', '')
            self.code = code.upper()[:30]

    @api.onchange('name_en')
    def _onchange_name_en_set_abbr(self):
        """Auto-generate abbr from English name"""
        if self.name_en and not self.abbr:
            words = self.name_en.split()
            if len(words) >= 2:
                # Take first letter of each word
                self.abbr = ''.join(w[0] for w in words[:4]).upper()
            else:
                self.abbr = self.name_en[:4].upper()

    # === CRUD Methods ===
    def name_get(self):
        result = []
        for rec in self:
            name = f"[{rec.abbr}] {rec.name}"
            if rec.name_en:
                name += f" ({rec.name_en})"
            result.append((rec.id, name))
        return result

    @api.model
    def _name_search(self, name='', domain=None, operator='ilike', limit=None, order=None):
        """Search by code, name, name_en, or abbr"""
        domain = domain or []
        if name:
            domain = ['|', '|', '|',
                      ('code', operator, name),
                      ('name', operator, name),
                      ('name_en', operator, name),
                      ('abbr', operator, name)] + domain
        return self._search(domain, limit=limit, order=order)
