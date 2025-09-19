# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)


class AccountTax(models.Model):
    _inherit = 'account.tax'

    is_stamp = fields.Boolean(string="Droit de Timbre",
                              help='Timbre Fiscal', default=False)

    is_stamp_achat= fields.Boolean(string="Timbre Achat",default=False)


class AccountInvoice(models.Model):
    # commented on migration
    #_inherit = "account.invoice"
    _inherit = "account.move"

    def _get_default_timbre(self):
        timbre = False
        try:
            timbre = self.env.ref('l10n_timbre.tva_timbre')
        except Exception as e:
            raise
        return timbre
    def _get_default_timbre_achat(self):
        timbreachat = False
        try:
            timbreachat = self.env.ref('l10n_timbre.tva_timbre_achat')
        except Exception as e:
            raise
        return timbreachat

    timbre_id = fields.Many2one('account.tax', string='Droit de timbre', readonly=True,states={'draft': [('readonly', False)]}, domain=[('is_stamp', '=', True)],default=lambda self: self.env['account.tax'].search([('is_stamp', '=', True)]))
    # states={'draft': [('readonly', False)]}
    timbre_achat_id = fields.Many2one('account.tax', string='T.Achat', readonly=True,states={'draft': [('readonly', False)]}, domain=[('is_stamp_achat', '=', True)],default=lambda self: self.env['account.tax'].search([('is_stamp_achat', '=', True)]))

    # @api.depends('exo_timbre')
    # def _find_no_tax(self):
    #     no tax= self.env['account.invoice'].search([('exo_timbre','=',True)])
    #     pass
    amount_timbre = fields.Monetary(
        string='Timbre',readonly=True, compute='_compute_timbre_amount', currency_field='currency_id',digits=dp.get_precision('Product Price'))
    amount_tmimbre_achat = fields.Float(string='T.Achat',readonly=True, compute='_compute_timbre_achat_amount')

    def get_timbre_values(self):
        tax_grouped = {}
        timbre = self.timbre_id
        taxes = timbre.compute_all(
            0, self.currency_id, 1.0, False, self.partner_id)['taxes']

        for tax in taxes:
            vals = {
                'tax_line_id': tax['id'],
                'type': 'tax',
                'name': tax['name'],
                'price_unit': tax['amount'],
                'quantity': 1,
                'price': tax['amount'],
                'account_id': tax['account_id'],
                'account_analytic_id': tax['analytic'],
                'invoice_id': self.id,
            }
            return vals
    def get_timbre_achat_values(self):
        tax_grouped = {}
        timbre_achat = self.timbre_achat_id
        taxes = timbre_achat.compute_all(
            0, False, 1.0, False, self.partner_id)['taxes']

        for tax in taxes:
            vals = {
                'tax_line_id': tax['id'],
                'type': 'tax',
                'name': tax['name'],
                'price_unit': tax['amount'],
                'quantity': 1,
                'price': tax['amount'],
                'account_id': tax['account_id'],
                'account_analytic_id': tax['analytic'],
                'invoice_id': self.id,
            }
            return vals


    #@api.multi
    @api.depends('timbre_id')
    def _compute_timbre_amount(self):
        for inv in self:
            if inv.timbre_id:
                inv.amount_timbre = inv.timbre_id.amount
            else:
                inv.amount_timbre = 0.0

            inv._compute_amount()
    #@api.multi
    @api.depends('timbre_achat_id')
    def _compute_timbre_achat_amount(self):
        for inv in self:
            if inv.timbre_achat_id:

                inv.amount_tmimbre_achat = inv.timbre_achat_id.amount
            else:
                inv.amount_tmimbre_achat = 0.0

            inv._compute_amount()

    #
    # @api.onchange('timbre_id')
    # def _onchange_timbre_id(self):
    #     if not self.id.__class__.__name__ == 'NewId':
    #         self.compute_taxes()
    #
    # @api.onchange('timbre_achat_id')
    # def _onchange_timbre_achat_id(self):
    #     if not self.id.__class__.__name__ == 'NewId':
    #         self.compute_taxes()
    #
    # @api.model
    # def tax_line_move_line_get(self):
    #     res = super(AccountInvoice, self).tax_line_move_line_get()
    #     timbre = self.timbre_id
    #     timbre_achat = self.timbre_achat_id
    #     if timbre:
    #        res.append(self.get_timbre_values())
    #     if timbre_achat:
    #         res.append(self.get_timbre_achat_values())
    #     return res
    #
    # # commented on migration
    # #@api.one
    # #@api.depends('invoice_line_ids.price_subtotal','line_ids.amount_residual', 'tax_line_ids.amount', 'currency_id', 'company_id', 'date_invoice', 'move_type', 'amount_timbre', 'amount_tmimbre_achat')
    # @api.depends('invoice_line_ids.price_subtotal','line_ids.amount_residual', 'currency_id', 'company_id', 'move_type', 'amount_timbre', 'amount_tmimbre_achat')
    # def _compute_amount(self):
    #     super(AccountInvoice,self)._compute_amount()
    #     if self.move_type == 'out_invoice':
    #         self.amount_total += self.amount_timbre
    #     if self.move_type == "in_invoice":
    #         self.amount_total += self.amount_tmimbre_achat
    #     if self.move_type == 'out_refund':
    #         #print'Hello'
    #         # self.timbre_id =''
    #         pass
    #     if self.exo_timbre == True:
    #         self.timbre_id =''
    #         pass
    #     if self.exo_tva == True:
    #         self.amount_tax= 0.0
    #         self.amount_total = self.amount_untaxed - self.amount_tax
    #         self.amount_total += self.amount_timbre
    #         pass
    #
    #
    # #@api.multi
    # #@api.depends('invoice_line_ids.price_subtotal','move_id.line_ids.amount_residual', 'tax_line_ids.amount', 'currency_id', 'company_id', 'date_invoice', 'type')
    # @api.depends('invoice_line_ids.price_subtotal','move_id.line_ids.amount_residual', 'currency_id', 'company_id', 'move_type')
    # def _compute_residual(self):
    #     super(AccountInvoice,self)._compute_residual()
    #     if self.exo_tva == True:
    #         self.residual = self.amount_untaxed - self.amount_tax
    #         self.residual += self.amount_timbre
    #         for r in self.tax_line_ids:
    #             r.amount = 0.0
    #             pass

        #
        #     self.amount_total += self.amount_timbre
        # else:
        #     self.amount_timbre = 0.0
            # self.amount += self.amount_timbre
