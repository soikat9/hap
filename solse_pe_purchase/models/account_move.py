# -*- coding: utf-8 -*-

from odoo import api, fields, tools, models, _
from odoo.exceptions import UserError, Warning, ValidationError
import xml.etree.cElementTree as ET
from lxml import etree
import json
import logging
from . import constantes
_logging = logging.getLogger(__name__)


class PeDatas(models.Model):
	_inherit = 'pe.datas'

	@api.model
	def get_selection_description(self, table_code):
		res=[]
		datas=self.search([('table_code', '=', table_code)])
		if datas:
			res = [(data.code, data.description) for data in datas]
		return res


class AccountMove(models.Model):
	_inherit = 'account.move'

	@api.model
	def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
		res = super(AccountMove, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
		if view_type in ['form']:
			paso_validacion = False
			if self._context.get('params') and 'action' in self._context['params']:
				parametros = self._context['params']
				accion = self.env['ir.actions.act_window'].search([('id', '=', parametros['action'])])
				if 'in_invoice' in accion.domain or 'in_refund' in accion.domain:
					paso_validacion = True

			elif self._context.get('default_move_type'):
				move_type = self._context.get('default_move_type')
				if move_type in ['in_invoice', 'in_refund']:
					paso_validacion = True

			#{'action': 198, 'cids': 1, 'id': '', 'menu_id': 101, 'model': 'account.move', 'view_type': 'form'}
			if paso_validacion:
				str_productos_ter_cant = res['fields']['invoice_line_ids']['views']['tree']['arch']
				root_temp = ET.fromstring(str_productos_ter_cant)
				t2 = ET.tostring(root_temp, encoding='utf8', method='xml')
				xml_productos_ter_cant = etree.XML(t2)
				node = xml_productos_ter_cant.xpath("//field[@name='tipo_afectacion_compra']")[0]
				node.set('invisible', '0')
				json_mod = {
					'column_invisible': False,
				}
				node.set("modifiers", json.dumps(json_mod))
				respuesta = ET.tostring(xml_productos_ter_cant, encoding='utf-8', method='xml')
				res['fields']['invoice_line_ids']['views']['tree']['arch'] = respuesta

		return res

class AccountMoveLine(models.Model):
	_inherit = 'account.move.line'

	tipo_afectacion_compra = fields.Selection(selection='_get_tipo_afectacion_compra', string='Tipo de afectación', default='1000', help='Tipo de afectación Compra')

	@api.model
	def _get_tipo_afectacion_compra(self):
		return self.env['pe.datas'].get_selection_description('PE.CPE.CATALOG5')

	@api.onchange('tipo_afectacion_compra')
	def onchange_tipo_afectacion_compra(self):
		if not self.move_id.move_type in ['in_invoice', 'in_refund']:
			return

		"""
			1000 Total valor de venta – operaciones exportadas
			1001 Total valor de venta - operaciones gravadas
			1002 Total valor de venta - operaciones inafectas
			1003 Total valor de venta - operaciones exoneradas
			1004 Total valor de venta – Operaciones gratuitas
			1005 Sub total de venta
			2001 Percepciones
			2002 Retenciones
			2003 Detracciones
			2004 Bonificaciones
			2005 Total descuentos
			3001 FISE (Ley 29852) Fondo Inclusión Social Energético

			<select class="o_input o_field_widget" name="tipo_afectacion_compra">
			<option value="false" style=""></option>

			<option value="&quot;1000&quot;" style="">Igv impuesto general a las ventas</option>
			<option value="&quot;2000&quot;" style="">Isc impuesto selectivo al consumo</option>
			<option value="&quot;9995&quot;" style="">Exportación</option>
			<option value="&quot;9996&quot;" style="">Gratuito</option>
			<option value="&quot;9997&quot;" style="">Exonerado</option>
			<option value="&quot;9998&quot;" style="">Inafecto</option>
			<option value="&quot;9999&quot;" style="">Otros conceptos de pago</option>
			<option value="&quot;1016&quot;" style="">Impuesto a la venta arroz pilado</option>
			<option value="&quot;7152&quot;" style="">Impuesto al Consumo de las bolsas de plástico</option>
			</select>
		"""
		if self.tipo_afectacion_compra in ('1000', '9999'):
			ids = self.tax_ids.filtered(lambda tax: tax.l10n_pe_edi_tax_code == constantes.IMPUESTO['igv'] and tax.type_tax_use == 'purchase').ids
			res = self.env['account.tax'].search([('l10n_pe_edi_tax_code', '=', constantes.IMPUESTO['igv']), ('id', 'in', ids)])
			if not res:
				res = self.env['account.tax'].search([('l10n_pe_edi_tax_code', '=', constantes.IMPUESTO['igv']), ('type_tax_use', '=', 'purchase')], limit=1)
			self.tax_ids = [(6, 0, ids + res.ids)]
			self._set_free_tax_purchase()

		elif self.tipo_afectacion_compra in ('2000'):
			ids = self.tax_ids.filtered(lambda tax: tax.l10n_pe_edi_tax_code == constantes.IMPUESTO['isc']).ids
			res = self.env['account.tax'].search([('l10n_pe_edi_tax_code', '=', constantes.IMPUESTO['isc']), ('id', 'in', ids)])
			if not res:
				res = self.env['account.tax'].search([('l10n_pe_edi_tax_code', '=', constantes.IMPUESTO['isc'])], limit=1)
			self.tax_ids = [(6, 0, ids + res.ids)]
			self._set_free_tax_purchase()

		elif self.tipo_afectacion_compra in ('9995'):
			ids = self.tax_ids.filtered(lambda tax: tax.l10n_pe_edi_tax_code == constantes.IMPUESTO['exportacion']).ids
			res = self.env['account.tax'].search([('l10n_pe_edi_tax_code', '=', constantes.IMPUESTO['exportacion']), ('id', 'in', ids)])
			if not res:
				res = self.env['account.tax'].search([('l10n_pe_edi_tax_code', '=', constantes.IMPUESTO['exportacion'])], limit=1)
			self.tax_ids = [(6, 0, ids + res.ids)]
			self._set_free_tax_purchase()

		elif self.tipo_afectacion_compra in ('9996'):
			ids = self.tax_ids.filtered(lambda tax: tax.l10n_pe_edi_tax_code == constantes.IMPUESTO['gratuito']).ids
			res = self.env['account.tax'].search([('l10n_pe_edi_tax_code', '=', constantes.IMPUESTO['gratuito']), ('id', 'in', ids)])
			if not res:
				res = self.env['account.tax'].search([('l10n_pe_edi_tax_code', '=', constantes.IMPUESTO['gratuito'])], limit=1)
			self.tax_ids = [(6, 0, ids + res.ids)]
			self._set_free_tax_purchase()

		elif self.tipo_afectacion_compra in ('9997'):
			ids = self.tax_ids.filtered(lambda tax: tax.l10n_pe_edi_tax_code == constantes.IMPUESTO['exonerado']).ids
			res = self.env['account.tax'].search([('l10n_pe_edi_tax_code', '=', constantes.IMPUESTO['exonerado']), ('id', 'in', ids)])
			if not res:
				res = self.env['account.tax'].search([('l10n_pe_edi_tax_code', '=', constantes.IMPUESTO['exonerado'])], limit=1)
			self.tax_ids = [(6, 0, ids + res.ids)]
			self._set_free_tax_purchase()
			
		elif self.tipo_afectacion_compra in ('9998'):
			ids = self.tax_ids.filtered(lambda tax: tax.l10n_pe_edi_tax_code == constantes.IMPUESTO['inafecto']).ids
			res = self.env['account.tax'].search([('l10n_pe_edi_tax_code', '=', constantes.IMPUESTO['inafecto']), ('id', 'in', ids)])
			if not res:
				res = self.env['account.tax'].search([('l10n_pe_edi_tax_code', '=', constantes.IMPUESTO['inafecto'])], limit=1)
			self.tax_ids = [(6, 0, ids + res.ids)]
			self._set_free_tax_purchase()

		elif self.tipo_afectacion_compra in ('7152'):
			ids = self.tax_ids.filtered(lambda tax: tax.l10n_pe_edi_tax_code == constantes.IMPUESTO['ICBPER']).ids
			res = self.env['account.tax'].search([('l10n_pe_edi_tax_code', '=', constantes.IMPUESTO['ICBPER']), ('id', 'in', ids)])
			if not res:
				res = self.env['account.tax'].search([('l10n_pe_edi_tax_code', '=', constantes.IMPUESTO['ICBPER'])], limit=1)
			self.tax_ids = [(6, 0, ids + res.ids)]
			self._set_free_tax_purchase()

	def _set_free_tax_purchase(self):
		if self.tipo_afectacion_compra in ('9996'):
			self.discount = 100
		else:
			if self.discount == 100:
				self.discount = 0
			


		
 
		


