# -*- coding: utf-8 -*-
# Copyright (c) 2021 Juan Gabriel Fernandez More (kiyoshi.gf@gmail.com)
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

{
	'name': "Perú: Compras",

	'summary': """
		Perú: Compras""",

	'description': """
		Perú: Compras
		Modulo donde se agrega complementos para adaptadar compras a la localización peruana.
	""",

	'author': "F & M Solutions Service S.A.C",
	'website': "https://www.solse.pe",
	'category': 'Financial',
	'version': '15.1.0.0',

	'depends': [
		'account',
		'solse_pe_catalogo',
		'solse_pe_cpe',
	],
	'data': [
		'views/account_move_view.xml',
	],
	'installable': True,
	'price': 60,
	'currency': 'USD',
}