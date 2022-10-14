from odoo import models, fields, api

class AccountAccount(models.Model):
    _inherit = 'account.account'

    currency_multirate_affected = fields.Boolean(string='Execute Exchange Difference')
    multirate_currency_id = fields.Many2one('res.currency', string='Currency')
    
    @api.onchange('currency_multirate_affected')
    def _onchange_currency_multirate_affected(self):
        if not self.currency_multirate_affected:
            self.multirate_currency_id = False

