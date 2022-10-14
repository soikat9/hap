from odoo import models, fields, api

class AccountAccount(models.Model):
    _inherit = 'account.account'
    
    @api.onchange('currency_multirate_conversion_affected')
    def _onchange_currency_multirate_conversion_affected(self):
        if self.currency_multirate_conversion_affected:
            self.currency_multirate_affected = False
            self.multirate_currency_id = False
        else:
            self.multirate_conversion_currency_id = False
    
    @api.onchange('currency_multirate_affected')
    def _onchange_currency_multirate_affected(self):
        if self.currency_multirate_affected:
            self.currency_multirate_conversion_affected = False
            self.multirate_conversion_currency_id = False
        else:
            self.multirate_currency_id = False
        
            
            