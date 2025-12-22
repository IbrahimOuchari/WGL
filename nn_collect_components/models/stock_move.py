from odoo import fields, models, api

class MoveRawIds(models.Model):
    _inherit = 'stock.move'

    qty_delivered = fields.Float(string="Qty livrée", digits=(16, 4))
    qty_consumed_total = fields.Float(string="Qty consommée totale", digits=(16, 4))
    qty_in_prod = fields.Float(string="Qty en production", digits=(16, 4))
    qty_left = fields.Float(
        string="Qty Left",digits=(16, 4)
    )
    qty_needed = fields.Float(
        string="Qty Needed",
        compute='_compute_qty_needed',
        store=False,digits=(16, 4)
    )
    qty_scraped = fields.Float(
        string="Qty rebut",
        digits=(16, 4)
    )

    qty_returned = fields.Float(
        string="Quantité retournée",
        digits=(16, 4)
    )

    @api.depends('quantity_done')
    def _compute_qty_needed(self):
        for move in self:
            move.qty_needed = move.quantity_done
