from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.depends('last_purchase_price', 'purchase_ok', 'sale_ok', 'total_cost')
    def _compute_standard_price(self):
        for record in self:
            if record.purchase_ok:
                record.standard_price = record.last_purchase_price
            elif record.sale_ok:
                record.standard_price = record.total_cost
            else:
                record.standard_price = 0


class ProductProduct(models.Model):
    _inherit = 'product.product'

    standard_price = fields.Float(related="product_tmpl_id.last_purchase_price")

class StockMove(models.Model):
    _inherit = 'stock.move'

    price_unit_move = fields.Float(string="Prix Unitaire")