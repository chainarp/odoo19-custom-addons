# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ItxModulerAddModuleWizard(models.TransientModel):
    _name = 'itx.moduler.add.module.wizard'
    _description = 'Add Module to Workspace Wizard'

    # Selection field to track which option user chose
    action_type = fields.Selection([
        ('create', 'Create New Module'),
        ('load', 'Load from Odoo'),
        ('import', 'Import from ZIP File'),
    ], string='Action Type', default='load')

    # Fields for Create option (Phase 2)
    module_name = fields.Char(string='Module Name', help='Technical name (e.g., my_custom_module)')
    module_title = fields.Char(string='Module Title', help='Display name (e.g., My Custom Module)')
    module_author = fields.Char(string='Author', default=lambda self: self.env.user.name)
    module_description = fields.Text(string='Description')

    # Fields for Import option (Phase 3)
    zip_file = fields.Binary(string='ZIP File', help='Upload module ZIP file')
    zip_filename = fields.Char(string='Filename')

    def action_create_module(self):
        """Create a new blank module (Phase 2 - Coming Soon)"""
        self.ensure_one()

        raise UserError(_(
            '🚧 Coming Soon!\n\n'
            'The "Create New Module" feature is under development.\n'
            'It will allow you to create a blank module from scratch.\n\n'
            'For now, please use "Load from Odoo" to load an existing module.'
        ))

    def action_load_from_odoo(self):
        """Load module from Odoo database (Phase 1 - Available Now)"""
        self.ensure_one()

        # Close this wizard and open the module selection wizard
        return {
            'name': 'Load Module from Odoo',
            'type': 'ir.actions.act_window',
            'res_model': 'import.module.wizard',
            'view_mode': 'form',
            'target': 'new',
        }

    def action_import_from_zip(self):
        """Import module from ZIP file (Phase 3 - Coming Soon)"""
        self.ensure_one()

        raise UserError(_(
            '🚧 Coming Soon!\n\n'
            'The "Import from ZIP" feature is under development.\n'
            'It will allow you to upload and extract module ZIP files.\n\n'
            'For now, please use "Load from Odoo" to load an existing module.'
        ))

    def action_confirm(self):
        """Dispatcher method based on selected action type"""
        self.ensure_one()

        if self.action_type == 'create':
            return self.action_create_module()
        elif self.action_type == 'load':
            return self.action_load_from_odoo()
        elif self.action_type == 'import':
            return self.action_import_from_zip()
        else:
            raise UserError(_('Please select an action type'))
