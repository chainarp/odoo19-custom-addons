{
    'name': "CT Vehicle Master",

    'summary': "Manage vehicle parts with brand and model information",

    'description': """
Vehicle Parts Management
========================
This module extends Product to support vehicle parts:
- Link products to vehicle brands and models from Fleet
- Track part numbers
- Display vehicle specifications (fuel type, transmission, etc.)
- Filter and group products by vehicle brand/model
    """,

    'author': "CT",
    'website': "https://www.yourcompany.com",

    'category': 'Inventory/Inventory',
    'version': '19.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'fleet', 'product'],

    # always loaded
    'data': [
        'views/views.xml',
        'views/product_template_views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
}

