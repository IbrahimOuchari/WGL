from odoo import fields ,api , models



class StockScrap(models.Model):
    _inherit = 'stock.scrap'

    is_scrap_applied = fields.Boolean(
        string="Déjà appliqué",
        help="Indique si cette mise au rebut a déjà été appliquée aux quantités de production."
    )


