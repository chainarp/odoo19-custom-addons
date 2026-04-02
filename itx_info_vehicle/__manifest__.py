# -*- coding: utf-8 -*-
{
    'name': 'ITX Info Vehicle',
    'version': '19.0.1.2.0',
    'category': 'Inventory/Inventory',
    'summary': 'Vehicle Information Management for Salvage Car Parts',
    'description': """
ITX Info Vehicle - Salvage Car Parts Management
================================================

Manage vehicle information hierarchy for salvage car parts business:
- Brand → Model → Generation → Spec (4-level hierarchy)
- Master Data: Body Types, Engines
- Part Categories (hierarchical)
- Auto-generate Internal Reference
- Product integration with vehicle compatibility

Features:
- Vehicle hierarchy management (Brand/Model/Generation/Spec)
- Support Minor Change (Pre-MC/Post-MC) as separate Generation records
- Body Type and Engine master tables
- Hierarchical part categories
- Auto-generate Internal Reference from abbreviations
- Extend product.template with vehicle part fields
- Compatible Specs (Many2many) for cross-compatibility
- Part Brand and Part Number fields

Developed by IT Expert Training & Outsourcing Co. (Thailand)
    """,
    'author': 'IT Expert Training & Outsourcing Co.',
    'website': 'https://www.itexpert.co.th',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'product',
        'stock',
    ],
    'data': [
        # Security
        'security/ir.model.access.csv',
        # Data
        'data/ir_sequence_data.xml',
        'data/part_category_data.xml',
        'data/vehicle_brand_data.xml',
        'data/vehicle_model_data.xml',
        'data/vehicle_generation_data.xml',
        'data/mgr_body_type_data.xml',
        'data/mgr_engine_data.xml',
        'data/vehicle_spec_data.xml',
        # Demo Vehicle Parts (16 records สำหรับ demo)
        'data/demo_vehicle_parts.xml',
        # Views
        'views/mgr_body_type_views.xml',
        'views/mgr_engine_views.xml',
        'views/vehicle_brand_views.xml',
        'views/vehicle_model_views.xml',
        'views/vehicle_generation_views.xml',
        'views/vehicle_spec_views.xml',
        'views/part_category_views.xml',
        'views/product_template_views.xml',
        'views/menuitems.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
