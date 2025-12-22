# -*- coding: utf-8 -*-
{
    'name': "ITX Moduler",

    'summary': "AI-Powered Odoo Module Creator",

    'description': """
ITX Moduler - Your AI-Powered Odoo Module Development IDE

Features:
- Import existing Odoo modules for customization
- Create new modules from scratch with snapshot architecture
- Edit models, fields, views, menus visually
- AI-assisted development (describe what you want, Claude generates code)
- Generate production-ready Python/XML code
- Export complete modules as ZIP files

Perfect for System Analysts who want to design and create Odoo modules
without deep technical programming knowledge.
    """,

    'author': "Chainaris P",
    'website': "https://www.itexpert.co.th",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Extra Tools',
    'version': '19.0.2.0.0',
    'icon': '/itx_moduler/static/description/itx_code_generator_icon_128x128.png',
    # any module necessary for this one to work correctly
    'depends': ['base', 'mail'],

    # always loaded
    'data': [
        'security/itx_moduler.xml',
        'security/ir.model.access.csv',
        'wizards/import_module_wizard.xml',
        'wizards/itx_moduler_add_module_wizard_views.xml',
        'views/itx_moduler.xml',
        'views/itx_moduler_settings.xml',
        'views/ir_actions.xml',
        'views/ir_model.xml',
        'views/ir_uis.xml',
        'views/res_groups.xml',
        # Sprint 1 & 2: Snapshot Models Views
        'views/itx_moduler_model_views.xml',
        'views/itx_moduler_ui_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
}
