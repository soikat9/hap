# -*- coding: utf-8 -*-
{
	'name': "CPE SUNAT",

	'summary': """
		Emision de comprobantes electronicos a SUNAT - Perú""",

	'description': """
		Facturación electrónica - Perú 
		Emision de comprobantes electronicos a SUNAT - Perú
	""",

	'author': "F & M Solutions Service S.A.C",
	'website': "https://www.solse.pe",
	'category': 'Financial',
	'version': '1.0',

	'depends': [
		'solse_pe_edi',
		'account_debit_note',
	],
	'data': [
		'security/solse_pe_cpe_security.xml',
		'security/ir.model.access.csv',
		'data/cpe_data.xml',
		'data/tareas_programadas.xml',
		'data/template_email_cpe.xml',
		'views/account_move_view.xml',
		'views/cpe_certificate_view.xml',
		'views/cpe_server_view.xml',
		'views/company_view.xml',
		'views/solse_cpe_view.xml',
		'views/account_payment_term_view.xml',
		'report/report_invoice.xml',
		'report/report_invoice_ticket.xml',
		'wizard/account_invoice_debit_view.xml',
		'wizard/account_payment_register_views.xml',
		
	],
	'assets': {
		'web.report_assets_common': [
			'/solse_pe_cpe/static/src/css/reportes.css',
		],
	},
	'installable': True,
	'price': 600,
	'currency': 'USD',
}