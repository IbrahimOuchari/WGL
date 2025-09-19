from odoo import models, fields, api




class SaleDevisLIneInherit(models.Model):
    _inherit = 'sale.devis.line'

    margin_product = fields.Monetary(
        string="Marge Produit",
        compute="_compute_margin_product",

        help="Marge calculée pour cette ligne : (Prix unitaire - Coût d'achat) * Quantité"
    )

    @api.onchange('price_unit', 'product_id.standard_price', 'qty','discount')
    def _compute_margin_product(self):
        for line in self:
            if not line.discount:
              line.margin_product = (line.price_unit - line.product_id.standard_price) * line.qty
            else:
              line.margin_product = (line.pu_remise - line.product_id.standard_price) * line.qty





class SaleDevisInherit(models.Model):
    _inherit = 'sale.devis'

    margin_production = fields.Monetary(
        string="Marge Totale",
        compute="_compute_margin_production",

        help="Somme totale des marges des lignes de commande."
    )

    @api.depends('devis_line.margin_product')
    def _compute_margin_production(self):
        for order in self:
            order.margin_production = sum(order.devis_line.mapped('margin_product'))
