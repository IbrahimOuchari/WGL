
from odoo import fields, models


class AccountPayment(models.Model):

    _inherit = "account.payment"

    sale_id = fields.Many2one(
        "sale.order", "Sale", readonly=True, states={"draft": [("readonly", False)]}
    )
