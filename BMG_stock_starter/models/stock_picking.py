from odoo import models, fields, api

class StockPickingEdit(models.Model):
    _inherit = 'stock.picking'

    transporteur = fields.Char(string="Transporteur")
    serie_voiture = fields.Char(String="Série Transporteur")

