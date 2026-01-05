from odoo import fields, models, api


class MoveRawIds(models.Model):
    _inherit = 'stock.move'

    qty_delivered = fields.Float(
        string="Qté livrée",
        digits=(16, 4)
    )

    qty_consumed_total = fields.Float(
        string="Qté consommée totale",
        digits=(16, 4)
    )

    qty_in_prod = fields.Float(
        string="Qté en production",
        digits=(16, 4)
    )

    qty_left = fields.Float(
        string="Qté restante",
        digits=(16, 4)
    )

    qty_needed = fields.Float(
        string="Qté nécessaire",
        compute="_compute_qty_needed",
        store=False,
        digits=(16, 4)
    )

    qty_scraped = fields.Float(
        string="Qté rebutée",
        digits=(16, 4)
    )

    qty_returned = fields.Float(
        string="Qté retournée",
        digits=(16, 4)
    )

    @api.depends('quantity_done')
    def _compute_qty_needed(self):
        for move in self:
            move.qty_needed = move.quantity_done
