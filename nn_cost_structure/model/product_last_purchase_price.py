from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    standard_price = fields.Float(
        string='Cost',
        compute='compute_standard_price_update',
        # inverse='_set_standard_price',
        # search='_search_standard_price',
        digits='Product Price',
        help="Cost based on the last purchase order line for this product, "
             "or manually set if needed.", store =True
    )
    new_purchase_order = fields.Integer("New Purchase Order", compute='compute_purchase_order', default=0, store=True)


    @api.depends('last_purchase_line_id', 'last_purchase_line_ids', 'seller_ids', 'sale_ok','purchase_ok')
    def compute_purchase_order(self):
        """Increment counter if new PO line is added"""
        for rec in self:
            # keep a count of purchase lines using the new field
            count = len(rec.last_purchase_line_ids)
            if rec.sale_ok:
                rec.new_purchase_order += count
                rec.compute_standard_price_update()
            # initialize if not set
            if not rec.new_purchase_order:
                rec.new_purchase_order = 0

            # detect if count increased compared to stored value
            if count > rec.new_purchase_order:
                rec.new_purchase_order = count
                if rec.standard_price == 0 and rec.new_purchase_order>0:
                    rec.compute_standard_price_update()
            else:
                # keep current value if no new line added
                rec.new_purchase_order = rec.new_purchase_order

    @api.depends(
        'product_variant_ids',
        'last_purchase_line_ids',
        'last_purchase_line_id',
        'last_purchase_price',
        'new_purchase_order','bom_count','total_cost','sale_ok','purchase_ok'
    )
    def compute_standard_price_update(self):
        """Compute standard_price from the latest confirmed purchase order line (state='purchase')"""
        for product in self:

            if product.sale_ok and not product.purchase_ok:
                product.standard_price = product.total_cost
            elif product.purchase_ok:
                # Filter only confirmed purchase order lines
                confirmed_lines = product.last_purchase_line_ids.filtered(
                    lambda l: l.order_id.state == 'purchase'
                )

                # Get the latest line based on date_order
                last_line = confirmed_lines.sorted(
                    key=lambda l: l.order_id.date_order
                )[-1] if confirmed_lines else False

                if last_line:
                    product.last_purchase_line_id = last_line
                    product.standard_price = last_line.price_unit
                    _logger.debug(
                        "Product %s: last purchase line %s, standard_price set to %s",
                        product.id, last_line.id, last_line.price_unit
                    )
                else:
                    _logger.debug("Product %s: no confirmed purchase line found", product.id)

    standard_price_refreshed = fields.Boolean(
        default=False,
        string="Standard Price Refreshed",
        store=True,
        compute='compute_standard_price_refreshed'
    )

    @api.depends('standard_price')
    def compute_standard_price_refreshed(self):
        for rec in self:
            if not rec.standard_price_refreshed:
                result = rec.check_standard_price()
                if not result:  # mismatch found
                    rec.compute_standard_price_update_actual()  # call a separate method
                rec.standard_price_refreshed = True

    def compute_standard_price_update_actual(self):
        """Actually update the standard_price from the latest confirmed PO line"""
        for product in self:
            confirmed_lines = product.last_purchase_line_ids.filtered(
                lambda l: l.order_id.state == 'purchase'
            )
            last_line = confirmed_lines.sorted(key=lambda l: l.order_id.date_order)[-1] if confirmed_lines else False
            if last_line:
                product.standard_price = last_line.price_unit
                _logger.info(
                    "Product %s: standard_price updated to %.2f",
                    product.name, last_line.price_unit
                )

    def check_standard_price(self):
        """Return True if standard_price matches the latest confirmed PO line, False otherwise"""
        for product in self:
            confirmed_lines = product.last_purchase_line_ids.filtered(
                lambda l: l.order_id.state == 'purchase'
            )
            last_line = confirmed_lines.sorted(key=lambda l: l.order_id.date_order)[-1] if confirmed_lines else False
            if last_line and product.standard_price != last_line.price_unit:
                return False
        return True


    def check_standard_price(self):
        """
        Check if the current product's standard_price matches
        the latest confirmed purchase order line (state='purchase').
        If not, update it.
        Sets standard_price_refreshed to True after update.
        Returns:
            True if standard_price is correct, False otherwise
        """
        for product in self:
            # Skip if already refreshed
            if product.standard_price_refreshed:
                continue

            # Get confirmed purchase order lines
            confirmed_lines = product.last_purchase_line_ids.filtered(
                lambda l: l.order_id.state == 'purchase'
            )

            # Get latest confirmed purchase order line
            last_line = confirmed_lines.sorted(
                key=lambda l: l.order_id.date_order
            )[-1] if confirmed_lines else False

            if last_line and product.standard_price != last_line.price_unit:
                # Mismatch found, update standard_price

                return False

            # If no mismatch, mark as refreshed

        return True


    @api.model
    def get_products_with_mismatched_standard_price(self):
        """Return products whose standard_price does not match the latest purchase order line"""
        mismatched_products = self.env['product.template'].search([]).filtered(
            lambda p: p.last_purchase_line_ids.filtered(lambda l: l.order_id.state == 'purchase')
        )

        result = []
        for product in mismatched_products:
            confirmed_lines = product.last_purchase_line_ids.filtered(lambda l: l.order_id.state == 'purchase')
            last_line = confirmed_lines.sorted(key=lambda l: l.order_id.date_order)[-1] if confirmed_lines else False
            if last_line and product.standard_price != last_line.price_unit:
                result.append(product)

        _logger.info("Products with mismatched standard_price: %s", [p.name for p in result])
        return result

class ProductProduct(models.Model):
    _inherit = 'product.product'

    standard_price = fields.Float(related="product_tmpl_id.last_purchase_price")


class StockMove(models.Model):
    _inherit = 'stock.move'

    price_unit_move = fields.Float(string="Prix Unitaire")