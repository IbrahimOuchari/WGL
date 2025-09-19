from odoo import models, fields


class MrpBomCustomFields(models.Model):
    _inherit = 'mrp.bom'

    price_unit = fields.Float(related="product_tmpl_id.list_price", digits='Product Price')
    cost_product = fields.Float(related="product_tmpl_id.total_cost", digits='Product Price')
    marge_product = fields.Float(related="product_tmpl_id.marge_brute", digits='Product Price')