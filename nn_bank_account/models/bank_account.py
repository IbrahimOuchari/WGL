from odoo import models, fields, api
from odoo.exceptions import ValidationError

class BankAccount(models.Model):
    _name = 'bank.account'
    _description = 'Compte Bancaire'

    name = fields.Char(string="Agence", required=True)
    rib = fields.Char(string="RIB", size=20)
    iban = fields.Char(string="IBAN")
    bic = fields.Char(string="Code BIC")

    @api.constrains('rib')
    def _check_rib_length(self):
        for record in self:
            if record.rib and len(record.rib) > 20:
                raise ValidationError("Le RIB ne peut pas dépasser 20 caractères.")
