from odoo import fields, models , api


class SaleOrder(models.Model):
    _inherit = 'sale.order.line'



    price_unit = fields.Float('Unit Price', required=True, digits='Product Price', default=0.0, group_operator='avg')

