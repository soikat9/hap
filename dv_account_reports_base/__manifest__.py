{
    'name': """
        Custom Accounting Reports Community |
    """,

    'summary': """
        
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

    'price': 199.99,
    'currency': 'EUR',

    'depends': [
        'web',
        'account',
    ],

    'data': [
        'security/ir.model.access.csv',
        'views/account_report_view.xml',
        'views/report_financial.xml',
        'views/search_template_view.xml',
        'views/partner_view.xml',
        #'views/res_config_settings_views.xml',
        'views/account_activity.xml',
    ],

    'assets': {
        'dv_account_reports_base.assets_financial_report': [
            ('include', 'web._assets_helpers'),
            'web/static/lib/bootstrap/scss/_variables.scss',
            ('include', 'web._assets_bootstrap'),
            'web/static/fonts/fonts.scss',
            'dv_account_reports_base/static/src/scss/account_financial_report.scss',
            'dv_account_reports_base/static/src/scss/account_report_print.scss',
        ],
        'web.assets_backend': [
            'dv_account_reports_base/static/src/js/mail_activity.js',
            'dv_account_reports_base/static/src/js/account_reports.js',
            'dv_account_reports_base/static/src/js/action_manager_account_report_dl.js',
            'dv_account_reports_base/static/src/scss/account_financial_report.scss',
        ],
        'web.assets_qweb': [
            'dv_account_reports_base/static/src/xml/**/*',
        ],
    },

    'images': ['static/description/banner.gif'],

    'application': True,
    'installable': True,
    'auto_install': False,
}
