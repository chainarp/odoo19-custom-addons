# -*- coding: utf-8 -*-

from odoo import models, fields


class ResGroups(models.Model):
    _inherit = 'res.groups'

    m2o_module = fields.Many2one(
        'itx.moduler.module',
        string='Module',
        help="Module",
        ondelete='cascade'
    )
