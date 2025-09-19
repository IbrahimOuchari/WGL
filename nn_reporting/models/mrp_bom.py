
from odoo import fields, models


class BOMLINE(models.Model):
    _inherit = "mrp.bom.line"

    active_product = fields.Boolean(related="product_id.active")
