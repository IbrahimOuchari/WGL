# © 2017 Ecosoft (ecosoft.co.th).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    order_sequence = fields.Boolean(string="Séquence de Commande", readonly=True, index=True)
    quote_id = fields.Many2one(
        comodel_name="sale.order",
        string="Devis",
        readonly=True,
        ondelete="restrict",
        copy=False,
        help="Pour la commande client, ce champ fait référence à son devis",
    )
    order_id = fields.Many2one(
        comodel_name="sale.order",
        string="Commande",
        readonly=True,
        ondelete="restrict",
        copy=False,
        help="Pour le devis, ce champ fait référence à sa commande client",
    )
    quotation_state = fields.Selection(
        string="Status Devis",
        readonly=True,
        related="state",
        help="Only relative quotation states",
    )

    @api.model
    def create(self, vals):
        order_sequence = vals.get("order_sequence") or self.env.context.get(
            "order_sequence"
        )
        if not order_sequence and vals.get("name", "/") == "/":
            vals["name"] = self.env["ir.sequence"].next_by_code("sale.quotation") or "/"
        return super().create(vals)

    def _prepare_order_from_quotation(self):
        return {
            "name": self.env["ir.sequence"].next_by_code("sale.order") or "/",
            "order_sequence": True,
            "quote_id": self.id,
            "client_order_ref": self.client_order_ref,
        }

    def action_convert_to_order(self):
        self.ensure_one()
        if self.order_sequence:
            raise UserError(_("Only quotation can convert to order"))
        order = self.copy(self._prepare_order_from_quotation())
        self.order_id = order.id  # Reference from this quotation to order
        if self.state == "draft":
            self.action_done()
        return self.open_duplicated_sale_order()

    @api.model
    def open_duplicated_sale_order(self):
        return {
            "name": _("Sales Order"),
            "view_mode": "form",
            "view_id": False,
            "res_model": "sale.order",
            "context": {"default_order_sequence": True, "order_sequence": True},
            "type": "ir.actions.act_window",
            "nodestroy": True,
            "target": "current",
            "domain": "[('order_sequence', '=', True)]",
            "res_id": self.order_id and self.order_id.id or False,
        }
