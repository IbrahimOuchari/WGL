from odoo import models, fields

class AccountMove(models.Model):
    _inherit = 'account.move'

    bank_account_id = fields.Many2one('bank.account', string="Compte Bancaire Destinataire")
