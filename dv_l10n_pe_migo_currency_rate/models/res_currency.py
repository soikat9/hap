from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

import requests
import logging
_logger = logging.getLogger(__name__)
from datetime import datetime


class ResCurrency(models.Model):
    _inherit = 'res.currency'

    def update_exchange_rate(self):
        token = self.env.company.migo_token_api
        url = "https://api.migo.pe/api/v1/exchange/date"
        payload = {
            "token": token,
            "fecha": datetime.today().strftime('%Y-%m-%d')
        }

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        response = requests.post(url, json=payload, headers=headers).json()
        if not token:
            raise ValidationError('Token no encontrado')
        _logger.info(response)
        if not response['success']:
            return

        usd_sell = self.env['res.currency'].search(
            [('name', '=', 'USD'), ('rate_type', '=', 'sale')], limit=1)
        if usd_sell:
            data_sale = {
                'name': fields.Date.context_today(self),
                'rate': 1 / float(response['precio_venta']),
                'rate_pe': response["precio_venta"],
                'currency_id': usd_sell.id
            }
            try:
                self.env['res.currency.rate'].create(data_sale)
            except Exception as e:
                _logger.info(e)
            
        usd_buy = self.env['res.currency'].search(
            [('name', '=', 'USD'), ('rate_type', '=', 'purchase')], limit=1)
        if usd_buy:
            data_purchase = {
                'name': fields.Date.context_today(self),
                'rate': 1 / float(response["precio_compra"]),
                'rate_pe': response["precio_compra"],
                'currency_id': usd_buy.id
            }
            try:
                self.env['res.currency.rate'].create(data_purchase)
            except Exception as e:
                _logger.info(e)
            
    @api.model
    def auto_update(self):
        self.update_exchange_rate()
