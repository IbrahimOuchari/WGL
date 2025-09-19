from odoo import models, fields, api

class StockMove(models.Model):
    _inherit = 'stock.move'

    # Assume you already have this field defined
    sale_line_id = fields.Many2one('sale.order.line', string='Sale Order Line', ondelete='set null')

    # Create a related field for pu_remise from sale.order.line
    pu_remise = fields.Float(string='P.U Après Remise', related='sale_line_id.pu_remise', store=True)
    price_subtotal = fields.Monetary( related='sale_line_id.price_subtotal', string='Subtotal', readonly=True, store=True)
    price_tax = fields.Float( related='sale_line_id.price_tax', string='Total Tax', readonly=True, store=True)
    qty_invoiced = fields.Float(related='sale_line_id.qty_invoiced', string='Invoiced', readonly=True, store=True)
    price_unit_move = fields.Float(related='sale_line_id.price_unit', string='P.U', readonly=True, store=True)
    total = fields.Float(string='Total', compute='_compute_total', store=True)
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        default=lambda self: self.env.company.currency_id,  # Default to the company's currency
    )
    @api.depends('quantity_done', 'pu_remise')
    def _compute_total(self):
        for move in self:
            move.total = move.quantity_done * move.pu_remise




