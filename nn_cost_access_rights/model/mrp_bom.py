from odoo import models, fields


class MrpBomCustomFields(models.Model):
    _inherit = 'mrp.bom'

    # NN Reporting Costs and Margins for products by BOM
    total_cost = fields.Float(
        string="Coût Total",
        compute="_compute_total_cost",
        digits='Product Price',
        help="Somme des prix standards des composants dans les lignes de nomenclature.",
        store=True,
    )
    cost_product = fields.Float(related="product_tmpl_id.total_cost", digits='Product Price', store=True, )
    price_unit = fields.Float(related="product_tmpl_id.list_price", digits='Product Price', store=True, )
    marge_product = fields.Float(related="product_tmpl_id.marge_brute", digits='Product Price', store=True, )


class MrpBomLineCustomFields(models.Model):
    _inherit = 'mrp.bom.line'

    # NN Reporting Bom Lines

    standard_price_related_product = fields.Float(
        string="Coût",
        related="product_id.standard_price",
        readonly=True,
        store=True,
        digits='Product Price',

        help="Prix standard du composant, lié au champ standard_price dans le produit."
    )
    standard_price_related_template = fields.Float(
        string="Coût",
        related="product_tmpl_id.standard_price",
        readonly=True,
        store=True, digits='Product Price',

        help="Prix standard du composant, lié au champ standard_price dans le produit."
    )
    standard_price_calculated = fields.Float(
        string="Coût Calculé",
        compute="_compute_standard_price_calculated",
        store=True, digits='Product Price',

        help="Coût calculé en multipliant le prix standard par la quantité du produit."
    )
    cost_product = fields.Boolean(
        string="Coût produit nul",
        compute="price_cost", store=True,
        digits='Product Price',

    )
