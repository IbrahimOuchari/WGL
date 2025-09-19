from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_compare
import logging

_logger = logging.getLogger(__name__)

class ManualDeliveryLine(models.TransientModel):
    _name = "manual.delivery.line"
    _description = "Manual Delivery Line"

    manual_delivery_id = fields.Many2one(
        "manual.delivery",
        string="Wizard",
        ondelete="cascade",
        required=True,
        readonly=True,
    )
    order_line_id = fields.Many2one(
        "sale.order.line",
        string="Lignes de Vente",
        required=True,
        readonly=True,
        ondelete="cascade",
    )
    product_id = fields.Many2one(related="order_line_id.product_id", readonly=True)
    name = fields.Text(related="order_line_id.name", readonly=True)
    qty_ordered = fields.Float(
        string="Commandée",
        related="order_line_id.product_uom_qty",
        help="Quantité commandée dans le bon de commande associé",
        readonly=True,
    )
    qty_procured = fields.Float(related="order_line_id.qty_procured", readonly=True)
    quantity = fields.Float()
    pu_remise = fields.Float(related="order_line_id.pu_remise", string='Prix Unitaire Remisé', readonly=True)

    @api.constrains("quantity")
    def _check_quantity(self):
        """ Prevent delivering more than the ordered quantity """
        for line in self:
            if float_compare(line.quantity, line.qty_ordered - line.qty_procured, precision_rounding=line.product_id.uom_id.rounding) > 0.0:
                raise UserError(
                    _(
                        "Vous ne pouvez pas livrer plus que la quantité restante. "
                        "Si vous devez le faire, veuillez d'abord modifier le bon de commande."
                    )
                )

    def check_pu_remise(self):
        for line in self:
            if line.order_line_id:
                _logger.info("PU Remise for %s: %s", line.order_line_id.name, line.pu_remise)
