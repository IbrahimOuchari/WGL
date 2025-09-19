from odoo import fields, models, api, _


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    # Archivage de BC Achat
    active = fields.Boolean(default=True)

    state = fields.Selection([
        ('brouillon', 'Brouillon'),
        ('to approve', 'A approuver'),
        ('purchase', 'Commande'),
        ('done', 'Fait'),
        ('cancel', 'Annulé'),
    ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='brouillon')

    rfq_seq = fields.Char(string='Référence RFQ', readonly=True)

    def button_draft_achat(self):
        self.write({'state': 'brouillon'})
        return {}

    def button_confirm_achat(self):
        for order in self:
            if order.state not in ['brouillon']:
                continue
            order._add_supplier_to_product()
            # Deal with double validation process
            if order._approval_allowed():
                order.button_approve()
            else:
                order.write({'state': 'to approve'})
            if order.partner_id not in order.message_partner_ids:
                order.message_subscribe([order.partner_id.id])
        return True
