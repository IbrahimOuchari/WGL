from odoo import models, fields

class ProductProduct(models.Model):
    _inherit = 'product.product'

    # Related fields in product.product linking to product.template fields
    bom_cost = fields.Float(
        string="Coût de la nomenclature (Produit)",
        related="product_tmpl_id.bom_cost",

        readonly=False
    )
    exploitation_charge_percent = fields.Float(
        string="% Charge d’exploitation (Produit)",
        related="product_tmpl_id.exploitation_charge_percent",

        readonly=False
    )
    exploitation_cost = fields.Float(
        string="Coût d’exploitation (Produit)",
        related="product_tmpl_id.exploitation_cost",

        readonly=False
    )
    total_cost = fields.Float(
        string="Coût de revient total (Produit)",
        related="product_tmpl_id.total_cost",
        readonly=False
    )
