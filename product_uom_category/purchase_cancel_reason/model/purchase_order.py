
from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    cancel_reason_id = fields.Many2one(
        comodel_name="purchase.order.cancel.reason",
        string="Raison d'Annulation",
        readonly=True,
        ondelete="restrict",
    )


class PurchaseOrderCancelReason(models.Model):
    _name = "purchase.order.cancel.reason"
    _description = "Purchase Order Cancel Reason"

    name = fields.Char(string="Raison", required=True, translate=True)
