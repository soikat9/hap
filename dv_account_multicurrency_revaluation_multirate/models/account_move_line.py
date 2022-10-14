from odoo import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    currency_name = fields.Char(related='currency_id.name', store=True)
    is_exchange_difference_process_move = fields.Boolean(
        related='move_id.is_exchange_difference_process_move', store=True)
