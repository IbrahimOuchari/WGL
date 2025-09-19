from odoo import models, fields, api


class PurchaseOrderLineDiscount(models.Model):
    _inherit = 'sale.order.line'

    pu_remise = fields.Float(string='P.U. Après Remise', compute='_compute_amount_pu_remise', digits='Product Price')

    @api.depends('discount', 'price_unit')
    def _compute_amount_pu_remise(self):
        for line in self:
            if line.discount:
                line.pu_remise = line.price_unit * ((100 - line.discount) / 100)
            else:
                line.pu_remise = line.price_unit
