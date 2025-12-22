# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ImportModuleWizard(models.TransientModel):
    _name = 'import.module.wizard'
    _description = 'Load Odoo Module Wizard'

    module_ids = fields.Many2many(
        'ir.module.module',
        string='Modules to Load',
        domain=[('state', '=', 'installed'), ('name', 'not in', ['base', 'web'])],
        required=True
    )

    def action_import_modules(self):
        """Load selected modules into itx.moduler.module workspace"""
        CodeGeneratorModule = self.env['itx.moduler.module']
        loaded_modules = self.env['itx.moduler.module']

        for module in self.module_ids:
            new_module = CodeGeneratorModule.create_from_odoo_module(module.id)
            loaded_modules |= new_module

        # Return action to show loaded modules
        return {
            'name': 'Loaded Modules',
            'type': 'ir.actions.act_window',
            'res_model': 'itx.moduler.module',
            'view_mode': 'kanban,list,form',
            'domain': [('id', 'in', loaded_modules.ids)],
            'context': {'create': True},
        }
