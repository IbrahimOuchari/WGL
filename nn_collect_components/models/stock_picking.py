from odoo import fields, models, api



class StockPicking(models.Model):
    _inherit = 'stock.picking'




    is_returned_qty_applied = fields.Boolean(   string="Déjà appliqué",
        help="Indique si cette qty retounrée a déjà été appliquée aux quantités de production.")

    manual_collect = fields.Boolean(string="Collecte manuelle", default=False )

