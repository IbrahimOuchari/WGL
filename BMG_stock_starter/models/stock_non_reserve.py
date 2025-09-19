from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round

from odoo.addons.stock.models.product import OPERATORS

class StockMoveLine(models.Model):
    _inherit = "stock.move.line"
    _name = "stock.move.line"

    not_reserved = fields.Float(
        string="Non réservé",
        compute="_compute_available_qty",
        store=True,
        readonly=True,
    )

    @api.depends("product_id", "product_uom_qty", "lot_id")
    def _compute_available_qty(self):
        for record in self:
            if record.product_id and record.move_id.state != "done":
                id_lot = record.lot_id.id if record.lot_id else None
                actual_qty = record.product_id.with_context(
                    {"location": record.location_id.id, "lot_id": id_lot}
                ).qty_available
                outgoing_qty = record.product_id.with_context(
                    {"location": record.location_id.id, "lot_id": id_lot}
                ).outgoing_qty
                record.not_reserved = actual_qty - outgoing_qty


class StockMove(models.Model):
    _inherit = "stock.move"
    _name = "stock.move"

    not_reserved = fields.Float(
        string="Non réservé",
        compute="_compute_available_qty",
        store=True,
        readonly=True,
    )

    @api.depends("product_id", "product_uom_qty")
    def _compute_available_qty(self):
        for record in self:
            if record.product_id and record.state != "done":
                actual_qty = record.product_id.with_context(
                    {"location": record.location_id.id}
                ).qty_available
                outgoing_qty = record.product_id.with_context(
                    {"location": record.location_id.id}
                ).outgoing_qty
                record.not_reserved = actual_qty - outgoing_qty

class ProductProduct(models.Model):
    _inherit = "product.product"

    qty_available_not_res = fields.Float(
        string="Qty Available Not Reserved",
        digits="Product Unit of Measure",
        compute="_compute_qty_available_not_reserved",
        search="_search_quantity_unreserved",
        help="Quantity of this product that is "
        "not currently reserved for a stock move",
    )

    def _prepare_domain_available_not_reserved(self):
        domain_quant = [("product_id", "in", self.ids)]
        domain_quant_locations = self._get_domain_locations()[0]
        domain_quant.extend(domain_quant_locations)
        return domain_quant

    def _compute_product_available_not_res_dict(self):

        res = {}

        domain_quant = self._prepare_domain_available_not_reserved()
        quants = (
            self.env["stock.quant"]
            .with_context(lang=False)
            .read_group(
                domain_quant,
                ["product_id", "location_id", "quantity", "reserved_quantity"],
                ["product_id", "location_id"],
                lazy=False,
            )
        )
        product_sums = {}
        for quant in quants:
            # create a dictionary with the total value per products
            product_sums.setdefault(quant["product_id"][0], 0.0)
            product_sums[quant["product_id"][0]] += (
                quant["quantity"] - quant["reserved_quantity"]
            )
        for product in self.with_context(prefetch_fields=False, lang=""):
            available_not_res = float_round(
                product_sums.get(product.id, 0.0),
                precision_rounding=product.uom_id.rounding,
            )
            res[product.id] = {"qty_available_not_res": available_not_res}
        return res

    @api.depends("stock_move_ids.product_qty", "stock_move_ids.state")
    def _compute_qty_available_not_reserved(self):
        res = self._compute_product_available_not_res_dict()
        for prod in self:
            qty = res[prod.id]["qty_available_not_res"]
            prod.qty_available_not_res = qty
        return res

    def _search_quantity_unreserved(self, operator, value):
        if operator not in OPERATORS:
            raise UserError(_("Invalid domain operator %s") % operator)
        if not isinstance(value, (float, int)):
            raise UserError(_("Invalid domain right operand %s") % value)

        ids = []
        for product in self.search([]):
            if OPERATORS[operator](product.qty_available_not_res, value):
                ids.append(product.id)
        return [("id", "in", ids)]

class ProductTemplate(models.Model):
    _inherit = "product.template"

    qty_available_not_res = fields.Float(
        string="Quantity On Hand Unreserved",
        digits="Product Unit of Measure",
        compute="_compute_product_available_not_res",
        search="_search_quantity_unreserved",
        help="Quantity of this product that is "
        "not currently reserved for a stock move",
    )

    @api.depends("product_variant_ids.qty_available_not_res")
    def _compute_product_available_not_res(self):
        for tmpl in self:
            if isinstance(tmpl.id, models.NewId):
                continue
            tmpl.qty_available_not_res = sum(
                tmpl.mapped("product_variant_ids.qty_available_not_res")
            )

    def action_open_quants_unreserved(self):
        products_ids = self.mapped("product_variant_ids").ids
        quants = self.env["stock.quant"].search([("product_id", "in", products_ids)])
        quant_ids = quants.filtered(
            lambda x: x.product_id.qty_available_not_res > 0
        ).ids
        xmlid = "stock_available_unreserved.product_open_quants_unreserved"
        action = self.env["ir.actions.act_window"]._for_xml_id(xmlid)
        action["domain"] = [("id", "in", quant_ids)]
        action["context"] = {
            "search_default_locationgroup": 1,
            "search_default_internal_loc": 1,
        }
        return action

    def _search_quantity_unreserved(self, operator, value):
        return [("product_variant_ids.qty_available_not_res", operator, value)]

class StockQuant(models.Model):
    _inherit = "stock.quant"

    contains_unreserved = fields.Boolean(
        string="Contains unreserved products",
        compute="_compute_contains_unreserved",
        store=True,
    )

    @api.depends("quantity", "reserved_quantity")
    def _compute_contains_unreserved(self):
        for record in self:
            # Avoid error when adding a new line on manually Update Quantity
            if isinstance(record.id, models.NewId):
                record.contains_unreserved = False
                continue
            record.contains_unreserved = (
                True if record.available_quantity > 0 else False
            )

