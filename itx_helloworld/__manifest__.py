{
    'name': "ITX Hello World",

    'summary': "Test addon for ITX Security Shield integration",

    'description': """
ITX Hello World - Test Addon
=============================

This is a test addon for demonstrating ITX Security Shield integration.

Features:
---------
* Simple model with basic fields
* List and form views
* Menu items
* Demo data

Purpose:
--------
Use this addon to test hardware fingerprinting and license validation
with ITX Security Shield.
    """,

    'author': "ITX Corporation",
    'website': "https://www.itxcorp.com",

    'category': 'Tools',
    'version': '19.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['itx_security_shield', 'base'],

    # always loaded
    'data': [
        'security/itx_helloworld_groups.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'data/ir_actions_server.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/license_info_wizard_views.xml',
        'report/itx_helloworld_report.xml',
        'report/itx_helloworld_report_template.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
}

