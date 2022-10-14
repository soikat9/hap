# -*- coding: utf-8 -*-

{
	'name': 'Tipo de cambio para Perú',
	'version': '15.0.1.0.0',
	'category': 'Extra Tools',
	'summary': 'Automatización de tipo de cambio para Perú',
	'author': "F & M Solutions Service S.A.C",
	'website': "http://www.solse.pe",
	'depends': [
		'base',
		'l10n_pe_currency',
		'solse_vat_pe',
	],
	'data': [
		'security/ir.model.access.csv',
		'data/ir_cron_data.xml',
		'views/account_move_view.xml',
		'views/res_currency_views.xml',
		'wizard/rango_fecha_view.xml',
	],
	'installable': True,
	'sequence': 1,
}
