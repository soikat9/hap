# -*- coding: utf-8 -*-

from odoo import api, fields, tools, models, _
from odoo.exceptions import UserError, Warning
import logging
_logging = logging.getLogger(__name__)

class SolseCPE(models.Model):
	_inherit = 'solse.cpe'

	no_enviar_rnoaceptados = fields.Boolean("No reintentar envió")
	cant_intentos = fields.Integer("Cant. Intentos", default=0, help="Cantidad de reintentos de envio a sunat")

	def obtener_dominio_pendientes(self):
		dominio = [('type', 'in', ['sync']), ('no_enviar_rnoaceptados', '=', False), ('estado_sunat', 'not in', ['05', '11', '13'])]
		dominio.append(('cant_intentos', '<', 6))

		#send_date
		return dominio

	def procesar_cpes_reenviar(self, cpe_count=None):
		pendientes = self.env['solse.cpe'].search(self.obtener_dominio_pendientes())
		pendientes_procesar = pendientes[0:cpe_count] if cpe_count else pendientes
		for cpe in pendientes_procesar:
			cpe.action_cancel()
			cpe.action_draft()
			cpe.action_generate()
			cpe.action_send()
			cpe.write({"cant_intentos": cpe.cant_intentos + 1})

		cant_pendientes = len(pendientes) - len(pendientes_procesar)
		if cant_pendientes > 0:
			self.env.ref('solse_pe_cpe_log.ir_cron_procesar_cpe')._trigger()
		