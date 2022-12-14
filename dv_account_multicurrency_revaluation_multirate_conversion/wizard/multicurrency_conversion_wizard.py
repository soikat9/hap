# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, fields, _
from odoo.tools import float_is_zero, format_date
from odoo.exceptions import UserError

import json
from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)

class MulticurrencyRevaluationWizard(models.TransientModel):
    _name = 'account.multicurrency.revaluation.conversion.wizard'
    _description = 'Multicurrency Revaluation Conversion Wizard'

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    journal_id = fields.Many2one('account.journal', related="company_id.account_revaluation_journal_id", string='Journal', domain=[('type', '=', 'general')], required=True, readonly=False)
    date = fields.Date(default=lambda self: self._context.get('date').get('date_to'), required=True)  # TODO change defult dates
    reversal_date = fields.Date(required=True)
    expense_provision_account_id = fields.Many2one('account.account', related="company_id.account_revaluation_expense_provision_account_id", string='Expense account', required=True, readonly=False)
    income_provision_account_id = fields.Many2one('account.account', related="company_id.account_revaluation_income_provision_account_id", string='Income Account', required=True, readonly=False)
    preview_data = fields.Text(compute="_compute_preview_data")
    show_warning_move_id = fields.Many2one('account.move', compute='_compute_show_warning')

    @api.model
    def default_get(self, default_fields):
        rec = super(MulticurrencyRevaluationWizard, self).default_get(default_fields)
        if 'reversal_date' in default_fields:
            rec['reversal_date'] = fields.Date.to_date(self._context.get('date').get('date_to')) + relativedelta(days=1)
        if not self._context.get('revaluation_no_loop') and not self.with_context(revaluation_no_loop=True)._compute_move_vals()['line_ids']:
            raise UserError(_('No adjustment needed'))
        return rec

    @api.depends('expense_provision_account_id', 'income_provision_account_id', 'reversal_date')
    def _compute_show_warning(self):
        for record in self:
            last_move = self.env['account.move.line'].search([
                ('account_id', 'in', (record.expense_provision_account_id + record.income_provision_account_id).ids),
                ('date', '<', record.reversal_date),
                ('is_conversion_process_move', '=', True),
            ], order='date desc', limit=1).move_id
            record.show_warning_move_id = False if last_move.reversed_entry_id else last_move

    @api.depends('expense_provision_account_id', 'income_provision_account_id', 'date', 'journal_id')
    def _compute_preview_data(self):
        for record in self:
            preview_vals = [self.env['account.move']._move_dict_to_preview_vals(self._compute_move_vals(), self.env.ref('base.USD'))]
            preview_columns = [
                {'field': 'account_id', 'label': _('Account')},
                {'field': 'name', 'label': _('Label')},
                {'field': 'debit', 'label': _('Debit'), 'class': 'text-right text-nowrap'},
                {'field': 'credit', 'label': _('Credit'), 'class': 'text-right text-nowrap'},
            ]
            record.preview_data = json.dumps({
                'groups_vals': preview_vals,
                'options': {
                    'columns': preview_columns,
                },
            })

    @api.model
    def _compute_move_vals(self):
        options = self._context
        self = self.with_context(report_options=options)
        line_dict = self.env['account.multicurrency.revaluation.conversion']._get_values(options=options, line_id='report_include--True')['children'][('report_include', None, True)]
        value_getter = self.env['account.multicurrency.revaluation.conversion']._get_column_details(options=options)[-1].getter
        move_lines = []
        if line_dict and line_dict['children']:
            for (_key1, _key2, currency_id), account_info in line_dict['children'].items():
                for (_key1, _key2, account_id), values in account_info['children'].items():
                    balance = value_getter(values['values'])[0]
                    account_account_id = self.env['account.account'].browse(account_id)
                    rate = self._context['currency_rates'][str(currency_id)]['rate']
                    if not float_is_zero(balance, precision_digits=self.company_id.currency_id.decimal_places):
                        debit = balance if balance > 0 else 0
                        credit = -balance if balance < 0 else 0
                        move_lines.append((0, 0, {
                            'name': _('Provision for {comp_cur} (1 {for_cur} = {rate} {comp_cur})').format(
                                for_cur=self.env['res.currency'].browse(currency_id).display_name,
                                comp_cur=self.env.company.currency_id.display_name,
                                rate=rate
                            ),    
                            'debit': 0.0,
                            'credit': 0.0,
                            'rate': rate,
                            'amount_currency': abs(balance) if debit > 0 else -abs(balance),
                            'currency_id': account_account_id.multirate_conversion_currency_id.id,
                            'account_id': account_id,
                        }))
                        debit = -balance if balance < 0 else 0
                        credit = balance if balance > 0 else 0
                        move_lines.append((0, 0, {
                            'name': (_('Expense Provision for {for_cur}') if balance < 0 else _('Income Provision for {for_cur}')).format(
                                for_cur=self.env['res.currency'].browse(currency_id).display_name,
                            ),
                            'debit': 0.0,
                            'credit': 0.0,
                            'rate': rate,
                            'amount_currency': -abs(balance) if credit > 0 else abs(balance),
                            'currency_id': account_account_id.multirate_conversion_currency_id.id,
                            'account_id': self.expense_provision_account_id.id if balance < 0 else self.income_provision_account_id.id,
                        }))
        move_vals = {
            'ref': _('Foreign currencies adjustment entry as of %s', format_date(self.env, self.date)),
            'journal_id': self.journal_id.id,
            'date': self.date,
            'line_ids': move_lines,
            'is_conversion_process_move': True,
        }
        return move_vals

    def create_entries(self):
        self.ensure_one()
        move_vals = self._compute_move_vals()
        if move_vals['line_ids']:
            for line in move_vals['line_ids']:
                line[2]['debit'] = line[2]['debit']*line[2]['rate']
                line[2]['credit'] = line[2]['credit']*line[2]['rate']
                del line[2]['rate']
            _logger.info('Creating move %s', move_vals)
            move = self.env['account.move'].create(move_vals)
            move._post()
            reverse_move = move._reverse_moves(default_values_list=[{
                'ref': _('Reversal of: %s', move.ref),
            }])
            reverse_move.date = self.reversal_date
            reverse_move._post()

            form = self.env.ref('account.view_move_form', False)
            ctx = self.env.context.copy()
            ctx.pop('id', '')
            return {
                'type': 'ir.actions.act_window',
                'res_model': "account.move",
                'res_id': move.id,
                'view_mode': "form",
                'view_id': form.id,
                'views': [(form.id, 'form')],
                'context': ctx,
            }
        raise UserError(_("No provision needed was found."))