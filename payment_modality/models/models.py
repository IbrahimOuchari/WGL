# -*- coding: utf-8 -*-
from odoo import models, fields, api, _, exceptions
from odoo.exceptions import UserError


VALUES_type = [('a', 'Espèce'), ('b', 'Chèque'), ('c', 'Traite'), ('d', 'Virement')]
VALUES_mode = [('a', 'Comptant'), ('b', 'A terme')]
# class relate_payment(models.Model):
#     _inherit = 'account.payment'
#
#     x = fields.Many2one('payment.modality')
class payment_modality(models.Model):
    _name = 'payment.modality'
    # _rec_name = 'type_modalite'


    partner_id = fields.Many2one('res.partner', related="payment_ids.partner_id")
    payment_ids=fields.One2many('account.payment','nbr_month')
    type_modalite = fields.Integer(string='Nombre des Chèque')
    payment_lines = fields.One2many('payment.modality.lines', 'cheque_id', string='Liste des Cheque')
    state1 = fields.Integer(string='status de paiment', related='payment_lines.state1')
    lst_price = fields.Monetary(string='Montant Total de Paiment', readonly=True,related="payment_ids.amount")
    currency_id = fields.Many2one('res.currency', string='Currency')
    lst_price1 = fields.Integer(store=True,compute='_compute_lst_price',string='Montant Totale Saisie')
    code=fields.Many2one('account.payment')

    payment_state = fields.Selection(selection=[
        ('not_paid', 'Not Paid'),
        ('paid', 'Paid'),
        ('partial', 'Partially Paid')],
        string="Payment Status", store=True, readonly=True, copy=False, tracking=True,
        compute='_compute_amount')


    @api.depends('payment_lines.montant')
    def _compute_lst_price(self):
        price = 0
        for record in self:
            for line in record.payment_lines:
                price += line.montant
            record.lst_price1 = price
    @api.depends('payment_state', 'type_modalite', 'state1')
    def _compute_amount(self):
        for rec in self:
            if int(rec.state1) == 0:
                self.payment_state = 'not_paid'
            elif int(rec.state1) == rec.type_modalite:
                self.payment_state = 'paid'
            else:
                self.payment_state = 'partial'

    @api.constrains('payment_lines')
    def _check_lines(self):
        nb = self.type_modalite
        tot=self.lst_price1
        tot1=self.lst_price
        count = len(self.payment_lines)
        res = {}
        if count != nb:
            raise exceptions.UserError(_('Nombre des chèques saisi different de nombre des chèques declarer'))
        if tot != tot1:
            raise exceptions.UserError(_('Montant totale des chèque doit ètre egale 0. Confirmer le paiement puis modifier et régler les montants oui bien les Traiter sous le menu Suivi de paiement et n oublier pas que le mantant total saisie doit etre egale a la montant de paiment  '))

    # @api.model
    # def _get_default_partner(self):
    #     ctx = self._context
    #     if ctx.get('active_model') == 'account.payment':
    #         return self.env['account.payment'].browse(ctx.get('active_ids')[1]).partner_id.name
class payment_form(models.Model):
    # _name = 'payment.form'
    _inherit = 'account.payment'

    type_pay = fields.Selection(VALUES_type, string='Type de Paiment')
    mode_pay = fields.Selection(VALUES_mode, string='Modalité de Paiment')
    num_cheque = fields.Integer(string='Numéro de Chéque')
    num_bank = fields.Integer(string='Numéro de Banque')
    date_emission = fields.Date(string="Date d'émission")
    nbr_month = fields.Many2one('payment.modality', string='Nombre des Mois')
    mod_id =fields.One2many('payment.modality','code')
class payment_modality_lines(models.Model):
    _name = 'payment.modality.lines'

    num_cheque = fields.Integer(string='Numero de cheque')
    montant = fields.Integer(string='Montant')
    date_che = fields.Date(string='Date de Paiement')
    State = fields.Selection([
        ('payed', 'Payé'),
        ('not payed', 'Non Payé')
    ], readonly=False, string='Status', default='not payed')
    cheque_id = fields.Many2one('payment.modality', string='Cheque id')
    state1 = fields.Integer(string='Progrés de Paiment', compute='_compute_pay')

    @api.depends('State', 'montant')
    def _compute_pay(self):
        nb = 0
        for rec in self:
            if rec.State == 'payed':
                nb = nb + 1
        self.state1 = nb
