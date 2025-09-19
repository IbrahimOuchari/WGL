from odoo import fields, models, api, _
from odoo.tools import float_compare
from odoo.tools import config


class SaleOrder(models.Model):
    _inherit = "sale.order"

    state = fields.Selection([
        ('brouillon', 'Brouillon'),
        ('sale', 'Sales Order'),
        ('fait', 'Fait'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='brouillon')
    devis_seq = fields.Char(string='Référence Devis', readonly=True)

    def action_draft_bc(self):
        orders = self.filtered(lambda s: s.state in ['cancel', 'sent', 'sale', 'fait'])
        return orders.write({
            'state': 'brouillon',
            'signature': False,
            'signed_by': False,
            'signed_on': False,
        })

    date_order = fields.Date(string='Order Date', required=True, readonly=True, index=True,
                             states={'brouillon': [('readonly', False)], 'sale': [('readonly', False)], 'sent': [('readonly', False)]}, copy=False,
                             default=fields.Datetime.now)
    partner_id = fields.Many2one(
        'res.partner', string='Client', readonly=True,
        states={'brouillon': [('readonly', False)]},
        required=True, change_default=True, tracking=True,
        domain="['|',('customer_rank','>', 0),('is_customer','=',True)]", )

    pricelist_id = fields.Many2one(
        'product.pricelist', string='Pricelist', check_company=True,  # Unrequired company
        required=True, readonly=True, states={'brouillon': [('readonly', False)], 'sent': [('readonly', False)]},
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", tracking=1,
        help="If you change the pricelist, only newly added lines will be affected.")

    order_line = fields.One2many('sale.order.line', 'order_id', string='Order Lines',
                                 states={'cancel': [('readonly', True)], 'fait': [('readonly', True)]}, copy=True,
                                 auto_join=True)

    # Choix de fusion BC pour la facturation

    def _create_invoices(self, grouped=False, final=False, date=None):
        if self._context.get('flag_merge_invoices'):
            grouped = self._context.get('flag_merge_invoices')
        return super(SaleOrder, self)._create_invoices(grouped=grouped, final=final, date=date)
