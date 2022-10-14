from odoo import models, fields


class AccountMove(models.Model):
    _inherit = 'account.move'

    is_exchange_difference_process_move = fields.Boolean(string="Es Asiento de Proceso por Diferencia de Cambio")