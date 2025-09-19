from odoo import models, fields

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    date_order = fields.Date(
        string="Date de la commande",
        related="order_id.date_order",
        store=True
    )
