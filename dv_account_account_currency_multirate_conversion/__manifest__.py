{
    'name': """
        Account Currency Rate Conversion Type |
    """,

    'summary': """
         |
    """,

    'description': """
         |
    """,

    'author': 'Develogers',
    'website': 'https://develogers.com',
    'support': 'especialistas@develogers.com',
    'live_test_url': 'https://demo.develogers.com',
    'license': 'LGPL-3',

    'category': 'Invoice',
    'version': '15.0',

    'price': 29.99,
    'currency': 'EUR',
    
    'depends': [
        'base',
        'account',
        'dv_l10n_latam_currency_multirate',
    ],

    'data': [
        'views/account_account_views.xml',
    ],

    'images': ['static/description/banner.gif'],
    
    'application': True,
    'installable': True,
    'auto_install': False,
}
