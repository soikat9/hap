# -*- coding: utf-8 -*-

from odoo import models, fields, api

class DocumentoPago(models.Model):
    _name = 'documento.pago'
    _description ="Tabla de documentos de pago"
    
    name = fields.Char(string='Tipo Documento de Pago')

class AccountMove(models.Model):
	_inherit = 'account.move'

	tipo_pago_doc = fields.Many2one("documento.pago", string='Documento Proveniente de')
		
