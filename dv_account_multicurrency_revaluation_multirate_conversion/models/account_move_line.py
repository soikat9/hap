from odoo import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    is_conversion_process_move = fields.Boolean(
        related='move_id.is_conversion_process_move', store=True)
