{
    'name': 'Simple WebSocket Alert',
    'version': '19.0.0.0.1',
    'category': 'Point of Sale',
    'summary': 'Simple WebSocket Alert for POS',
    'description': """
        Simple WebSocket Alert for POS
    """,
    'depends': ['sale', 'bus'],
    'assets': {
        'web.assets_backend': [
            'pos_simple_alert/static/src/js/order_notification_service.js',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}