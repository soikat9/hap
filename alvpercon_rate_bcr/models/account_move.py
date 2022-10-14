# -*- coding: utf-8 -*-

from odoo import api, fields, tools, models, _
from odoo.exceptions import UserError, Warning, ValidationError
import logging
_logging = logging.getLogger(__name__)

class AccountMove(models.Model):
	_inherit = 'account.move'

	es_diario_apert = fields.Boolean('Es diario de apertura' , help="Activar solo para diarios de apertura y después de ingresar los registros")

class AccountMoveLine(models.Model):
	_inherit = 'account.move.line'

	tipo_cambio = fields.Float('Tipo de cambio', compute="_compute_tipo_cambio" , digits=(12,3))
	tipo_cambio_r = fields.Float('Tipo_cambio', related ="tipo_cambio", store=True)
	debit_d = fields.Float('Débito Dolar', compute="_compute_debito_cambio" , digits=(12,2) , store=True)
	debit_da = fields.Float('Débito_Dolar', related="debit_d" , store=True )
	credit_d = fields.Float('Crédito Dolar', compute="_compute_credito_cambio" , digits=(12,2) , store=True)
	credit_da = fields.Float('Crédito Dolar', related="credit_d" , store=True)
	date_related = fields.Date("Fecha relacionada", related="move_id.invoice_date")
	invoice_date = fields.Date("Fecha Factura", compute="_compute_invoice_date")
	amount_currency_d = fields.Float('Importe en Dólares', compute="_compute_importe_d" , digits=(12,2) )
	date_acc_entry = fields.Date("Fecha Asiento", related="origin_move_line_id.invoice_date") # campo instalado desde solse_target_move
	es_x_apertrel = fields.Boolean("Movimiento por Apertura", related="move_id.es_x_apertura")
	es_diario_apertd = fields.Boolean('Es diario de apertura' , related="move_id.es_diario_apert")
	doc_rel_id = fields.Date('Fecha relacionado' , related="move_id.reversed_entry_id.invoice_date") #fecha para nota de credito
 
	@api.depends('date_related', 'doc_rel_id','date_acc_entry')
	def _compute_invoice_date(self):
	#def actualiza_fecha(self):	
	
		for reg in self:
			reg.invoice_date = reg.date_related
			if reg.doc_rel_id == False:
				if reg.invoice_date == False:
					if reg.date_acc_entry == False:
						reg.invoice_date = reg.date
					else:
						reg.invoice_date = reg.date_acc_entry
			else:
				reg.invoice_date = reg.doc_rel_id



	#@api.depends('currency_id', 'date', 'company_id')
	@api.depends('invoice_date', 'es_x_apertrel','es_diario_apertd','amount_currency')
	def _compute_tipo_cambio(self):
		for reg in self:
			#if not reg.date or not reg.currency_id or not reg.company_id:
			if not reg.invoice_date or not reg.currency_id or not reg.company_id:
			
				reg.tipo_cambio = 2
				continue
			currency_rate_id = [
				('name','=',str(reg.invoice_date)),
				('company_id','=',reg.company_id.id),
				('currency_id','=',2),
			]
			currency_rate_id = self.env['res.currency.rate'].sudo().search(currency_rate_id)
			#for regs in currency_rate_id:
			if currency_rate_id:
				if reg.journal_id.id == 4:
					reg.tipo_cambio = 0
				else:
					if reg.es_x_apertrel == False: # ****** en caso de facturas de apertura ventas
						#reg.tipo_cambio = currency_rate_id.rate_pe
						reg.tipo_cambio = 1/currency_rate_id.rate
					else:
						if reg.es_diario_apertd == False:
							reg.tipo_cambio = 1/currency_rate_id.rate
						else:
							if reg.amount_currency == 0:
								reg.tipo_cambio = 0
							else:
								reg.tipo_cambio = (reg.debit + reg.credit)/abs(reg.amount_currency)
								reg.tipo_cambio_r = (reg.debit + reg.credit)/abs(reg.amount_currency)
						#************************************
						# if currency_rate_id.name == "USD":
						# 	reg.tipo_cambio = 1/currency_rate_id.rate
						# 	##reg.tipo_cambio = (reg.debit + reg.credit)/abs(reg.amount_currency)
						# else:
						# 	reg.tipo_cambio = 1/currency_rate_id.rate
						#*********************************************
			else:
				#reg.tipo_cambio = 1
				# si no esta registrado el tipo de cambio, busca el tipo de cambio mas cercano
				
				#************************************
				# @api.depends('invoice_date')
				# def _compute_tipo_cambio_sistema(self):
				for reg in self:
					moneda_dolar = self.env["res.currency"].search([("name", "=", "USD")], limit=1)
					tipo_cambio = 1.0
					tipo_cambio = moneda_dolar._convert(1.0, reg.company_id.currency_id, reg.company_id, reg.invoice_date, round=False)
					reg.tipo_cambio = tipo_cambio
				#***********************************
				#***********************************
				# @api.depends('invoice_date')
				# def _compute_tipo_cambio_sistema(self):
				#**************************************
					# for reg in self:
					# 	moneda_dolar = self.env["res.currency"].search([("name", "=", "USD")], limit=1)
					# 	tipo_cambio = 1.0
					# 	if reg.currency_id.id == moneda_dolar.id:
					# 		tipo_cambio = moneda_dolar._convert(1.0, reg.company_id.currency_id, reg.company_id, reg.invoice_date)
					# 	reg.tipo_cambio = tipo_cambio
		#************************************
	@api.depends('currency_id', 'amount_currency', 'es_x_apertrel','tipo_cambio_r')
	def _compute_debito_cambio(self):
		for reg in self:
			if reg.currency_id.id == 2  or reg.currency_id.id == 168:
				if reg.amount_currency >=0:
					#reg.debit_d = "{0:.4f}".format(reg.amount_currency)
					reg.debit_d = round((reg.amount_currency),2)
				else:
					reg.debit_d = 0

			else:
				if reg.tipo_cambio_r == 0:
						reg.debit_d = 0
				else:
					if reg.amount_currency >=0:
						if reg.es_x_apertrel == False:
							#reg.debit_d = "{0:.4f}".format(reg.amount_currency/reg.tipo_cambio)
							#reg.debit_d = "{0:.4f}".format(reg.amount_currency/reg.tipo_cambio_r)
							reg.debit_d = round((reg.amount_currency/reg.tipo_cambio_r),2)
						else:
							
							if reg.amount_currency == 0:
								reg.debit_d = 0
							else:
								#reg.debit_d = "{0:.4f}".format(reg.amount_currency/reg.tipo_cambio_r)
								reg.debit_d = round((reg.amount_currency/reg.tipo_cambio_r),2)
					else:
						reg.debit_d = 0
				
	@api.depends('currency_id', 'amount_currency', 'es_x_apertrel','tipo_cambio_r')
	def _compute_credito_cambio(self):
		for reg in self:
			if reg.currency_id.id == 2 or reg.currency_id.id == 168:
				if reg.amount_currency >=0:
					reg.credit_d = 0
				else:
					reg.credit_d = round(abs(reg.amount_currency),2)
    
			else:
				if reg.amount_currency >=0:
					reg.credit_d = 0
				else:
					if reg.tipo_cambio_r == 0:
						reg.credit_d = 0
					else:
						if reg.es_x_apertrel == False:
							#reg.credit_d = round(abs(reg.amount_currency/reg.tipo_cambio),3)
							reg.credit_d = round(abs(reg.amount_currency/reg.tipo_cambio_r),2)
						else:
							#reg.credit_d = round(abs(reg.amount_currency),3)
							#reg.credit_d = round(abs(reg.amount_currency/reg.tipo_cambio),3)
							if reg.amount_currency == 0:
								reg.credit_d = 0
							else:
								reg.credit_d = round(abs(reg.amount_currency/reg.tipo_cambio_r),2)
		
	def _compute_importe_d(self):
		for reg in self:
			reg.amount_currency_d = round(reg.debit_d - reg.credit_d,2)
