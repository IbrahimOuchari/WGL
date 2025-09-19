from odoo import api, fields, models, tools, _

class Company(models.Model):
    _inherit = "res.company"

    compte_bancaire = fields.Char(string="RIB Bancaire")
    iban = fields.Char(string="IBAN")
    bic = fields.Char(string="Code BIC")
    banque = fields.Char(string="Banque")
    agence = fields.Char(string="Agence")
    mat_cnss = fields.Char(string="Immatriculation CNSS")
    tel_technique = fields.Char(string="N° Tel Service Technique")
    tel_commercial = fields.Char(string="N° Tel Service Commercial")
    affiche_tax = fields.Boolean(string="Afficher la colonne Tax dans template", default=True)