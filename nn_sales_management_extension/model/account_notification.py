from odoo import models, fields

class AccountNotification(models.Model):
    _inherit = 'account.notification'


    type1 = fields.Selection(related='notification.type1',string="Mode de Paiment")

    date = fields.Date (string="Date")