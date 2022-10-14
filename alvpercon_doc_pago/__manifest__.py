# -*- coding: utf-8 -*-

{
	'name': 'Tipos documetos de pago',
	'version': '15.0.1.0.0',
	'category': 'Extra Tools',
	'summary': 'Campo Many2one para pagos de caja chica en facturas - Tarjeta de Credito',
	'author': 'Alvpercon',
	'website': 'https://www.alvpercon.com',
	'depends': ['account'],
	'data': [
		"security/ir.model.access.csv",
		'views/account_move_view.xml',
	],
	'installable': True,
	'sequence': 1,
}