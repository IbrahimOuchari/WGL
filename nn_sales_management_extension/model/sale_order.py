from pkgutil import read_code

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    forcee_facturation = fields.Boolean(string="Forcée Facturation", default=False)
    forcee_livraison = fields.Boolean(string="Forcée Livraison", default=False)

    @api.onchange('forcee_facturation')
    def _onchange_force_facturation(self):
        if self.forcee_facturation:
            self.invoice_status = "invoiced"



    picking_status = fields.Selection(
        [
            ("done", "Entièrement Livré"),  # order done
            ("in_progress", "En Cours"),  # order in progress
        ],
        string="Livraison",
        copy=False,
        tracking=True,
        index=True,
        compute="_compute_picking_status",
        search="_search_picking_status",
    )

    @api.onchange('livraison_complete', 'livraison_done')
    def _compute_picking_status(self):
        for record in self:
            if record.livraison_complete:
                record.picking_status = "done"
            else:
                record.picking_status = "in_progress"
            print("status")
            if not record.livraison_complete and record.forcee_livraison:
                record.picking_status = 'done'


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'



    margin_product = fields.Monetary(
        string="Marge Brute",
        compute="_compute_margin_product",
        store=True,
        help="Marge calculée pour cette ligne : (Prix unitaire - Coût d'achat) * Quantité"
    )

    @api.depends('price_unit', 'product_id.standard_price', 'product_uom_qty','discount')
    def _compute_margin_product(self):
        for line in self:
            if not line.discount:
              line.margin_product = (line.price_unit - line.product_id.standard_price) * line.product_uom_qty
            else:
              line.margin_product = (line.pu_remise - line.product_id.standard_price) * line.product_uom_qty

    decoration_danger = fields.Boolean(
        string="Decoration DANGER",
        default=False,
        compute="_compute_marge_product",
        store=True
    )

    @api.onchange('margin_product')
    def _compute_marge_product(self):
        for record in self:
            if record.margin_product <= 0 or record.margin_product == 0:
                record.decoration_danger = True

    def compute_marge_product(self):
        for record in self:
            if record.margin_product <= 0 or record.margin_product == 0:
                record.decoration_danger = True