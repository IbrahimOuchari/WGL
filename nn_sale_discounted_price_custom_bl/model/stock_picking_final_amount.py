from odoo import models, fields, api
from odoo.tools import formatLang
from functools import partial

class StockPicking(models.Model):
    _inherit = "stock.picking"

    amount_untaxed = fields.Monetary(
        string="Montant HT",  # French label for untaxed amount
        store=True,
        readonly=True,
        compute='_compute_amounts',  # Renamed for clarity
        tracking=5
    )
    amount_tax = fields.Monetary(
        string="Taxes",  # French label for tax amount
        store=True,
        readonly=True,
        compute='_compute_amounts'  # Updated compute method
    )
    amount_total = fields.Monetary(
        string="Total",  # French label for total amount
        store=True,
        readonly=True,
        compute='_compute_amounts',  # Updated compute method
        tracking=4
    )


    @api.depends('move_ids_without_package.total')  # Ensure taxes are considered
    def _compute_amounts(self):
        """
        Compute the total amounts for the stock picking.
        """
        for picking in self:
            amount_untaxed = amount_tax = 0.0
            for move in picking.move_ids_without_package:  # Iterating over stock moves instead
                amount_untaxed += move.price_subtotal
                amount_tax += move.price_tax
            picking.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax,
            })

    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        default=lambda self: self.env.company.currency_id,  # Default to the company's currency
    )

    def action_generate_report(self):
        """
        Print lot etiquettes for each stock move associated with this picking.
        """
        self.ensure_one()

        # Récupérez le rapport depuis l'identifiant
        report = self.env.ref('nn_sale_discounted_price_custom_bl.action_template_stock_picking')

        # Générez le rapport pour l'enregistrement actuel
        return report.report_action(self)


    sale_line_id = fields.Many2one('sale.order.line', string='Sale Order Line', ondelete='set null')

    def action_refresh_price_unit(self):
        # This will store the price unit updates to prevent multiple writes
        price_unit_updates = {}

        # Loop through each stock picking record
        for picking in self:
            # Loop through each move related to the picking
            for move in picking.move_ids_without_package:
                if move.sale_line_id:
                    # Store the move ID and the corresponding sale line price unit
                    price_unit_updates[move.id] = move.sale_line_id.price_unit

        # Perform the update in a single write to improve performance
        if price_unit_updates:
            moves = self.env['stock.move'].browse(price_unit_updates.keys())
            moves.write({'price_unit': [(4, price_unit_updates[move_id]) for move_id in moves.ids]})
