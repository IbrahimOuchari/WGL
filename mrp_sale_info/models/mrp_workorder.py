
from odoo import fields, models


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    sale_id = fields.Many2one(
        related="production_id.sale_id", string="BC N°", readonly=True, store=True
    )
    partner_id = fields.Many2one(
        related="sale_id.partner_id", readonly=True, string="Client", store=True
    )
    commitment_date = fields.Datetime(
        related="sale_id.commitment_date",
        string="Date d'Engagement",
        store=True,
        readonly=True,
    )
    client_order_ref = fields.Char(
        related="sale_id.client_order_ref", string="Customer Reference", store=True
    )
