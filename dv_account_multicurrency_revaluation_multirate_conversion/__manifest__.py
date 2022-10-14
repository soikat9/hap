{
    'name': """
        Custom Account Multicurrency Revaluation MultirateReport Conversion |
        Reporte Personalizado de Revaluación de Moneda
    """,

    'summary': """
        Adds currency rate type filter on multicurrency revaluation report. |
        Agrega filtro de tipo de tasa de cambio en el reporte de revaluación de moneda.
    """,

    'description': """
        
    """,

    'author': 'Develogers ',
    'website': 'https://develogers.com',
    'support': 'especialistas@develogers.com',
    'live_test_url': 'https://demo.develogers.com',
    'license': 'LGPL-3',

    'category': 'Invoice',
    'version': '15.0',
    
    'price': 99.99,
    'currency': 'EUR',
    
    'depends': [
        'dv_account_reports_base',
        'dv_account_account_currency_multirate_conversion',
    ],

    'data': [
        'security/ir.model.access.csv',
        'views/account_report_templates.xml',
        'views/search_template_view.xml',
        'views/account_multicurrency_revaluation_conversion_views.xml',
        'wizard/multicurrency_conversion_wizard.xml',
    ],
    
    'images': ['static/description/banner.gif'],
    
    'application': True,
    'installable': True,
    'auto_install': False,
}