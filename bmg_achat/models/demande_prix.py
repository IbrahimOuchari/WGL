from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError


class PurchaseRfq(models.Model):
    _name = "purchase.rfq"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = "New Page Demande de Prix Modules"

    name = fields.Char(string='Sequence Rfq', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('Nouveau'))

    # Sequence de demande de prix
    @api.model
    def create(self, vals):
        if 'name' not in vals or vals['name'] == _('Nouveau'):
            vals['name'] = self.env['ir.sequence'].next_by_code('purchase.rfq') or _('Nouveau')
        return super(PurchaseRfq, self).create(vals)

    priority = fields.Selection(
        [('0', 'Normal'), ('1', 'Urgent')], 'Priority', default='0', index=True)
    date_rfq = fields.Date('Date', required=True, index=True, copy=False,
                           default=fields.Datetime.now)

    partner_id = fields.Many2one('res.partner', string='Fournissuer', required=True, change_default=True, tracking=True,
                                 domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

    state = fields.Selection([
        ('rfq', 'Demande de prix'),
        ('sent', 'Envoyé'),
        ('confirme', 'Confirmé'),
        ('expired', 'Expiré'),
        ('cancel', 'Annulé'),
    ], string='Status', readonly=True, index=True, copy=False, default='rfq', tracking=True)

    READONLY_STATES = {
        'confirme': [('readonly', True)],
        'expired': [('readonly', True)],
        'cancel': [('readonly', True)],
    }
    notes = fields.Text('Conditions')

    currency_id = fields.Many2one('res.currency', 'Devise', required=True, states=READONLY_STATES,
                                  default=lambda self: self.env.company.currency_id.id)
    rfq_line = fields.One2many('purchase.rfq.line', 'rfq_id', string='Rfq Lines',
                               states={'cancel': [('readonly', True)], 'confirme': [('readonly', True)]}, copy=True)
    date_planned = fields.Date(string='Date Prévue de Réception', index=True, copy=False,
                               compute='_compute_date_planned',
                               store=True, readonly=False)

    payment_term_id = fields.Many2one('account.payment.term', 'Condition de Paiement',
                                      domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    product_id = fields.Many2one('product.product', related='rfq_line.product_id', string='Produit', readonly=False)
    user_id = fields.Many2one(
        'res.users', string='Responsable Achat', index=True, tracking=True,
        default=lambda self: self.env.user, check_company=True)
    company_id = fields.Many2one('res.company', 'Société', required=True, index=True,
                                 default=lambda self: self.env.company.id)

    @api.depends('rfq_line.date_planned')
    def _compute_date_planned(self):
        """ date_planned = the earliest date_planned across all order lines. """
        for order in self:
            dates_list = order.rfq_line.filtered(lambda x: not x.display_type and x.date_planned).mapped(
                'date_planned')
            if dates_list:
                order.date_planned = fields.Datetime.to_string(min(dates_list))
            else:
                order.date_planned = False

    @api.onchange('date_planned')
    def onchange_date_planned(self):
        if self.date_planned:
            self.rfq_line.filtered(lambda line: not line.display_type).date_planned = self.date_planned

    def write(self, vals):
        vals, partner_vals = self._write_partner_values(vals)
        res = super().write(vals)
        if partner_vals:
            self.partner_id.sudo().write(partner_vals)  # Because the purchase user doesn't have write on `res.partner`
        return res

    def unlink(self):
        for order in self:
            if not order.state == 'cancel':
                raise UserError(_('In order to delete a purchase order, you must cancel it first.'))
        return super(PurchaseOrder, self).unlink()

    def copy(self, default=None):
        ctx = dict(self.env.context)
        ctx.pop('default_product_id', None)
        self = self.with_context(ctx)
        new_po = super(PurchaseRfq, self).copy(default=default)
        return new_po

    @api.onchange('partner_id')
    def onchange_partner_id_warning(self):
        if not self.partner_id or not self.env.user.has_group('purchase.group_warning_purchase'):
            return
        warning = {}
        title = False
        message = False

        partner = self.partner_id

        # If partner has no warning, check its company
        if partner.purchase_warn == 'no-message' and partner.parent_id:
            partner = partner.parent_id

        if partner.purchase_warn and partner.purchase_warn != 'no-message':
            # Block if partner only has warning but parent company is blocked
            if partner.purchase_warn != 'block' and partner.parent_id and partner.parent_id.purchase_warn == 'block':
                partner = partner.parent_id
            title = _("Warning for %s", partner.name)
            message = partner.purchase_warn_msg
            warning = {
                'title': title,
                'message': message
            }
            if partner.purchase_warn == 'block':
                self.update({'partner_id': False})
            return {'warning': warning}
        return {}

    def _write_partner_values(self, vals):
        partner_values = {}
        if 'receipt_reminder_email' in vals:
            partner_values['receipt_reminder_email'] = vals.pop('receipt_reminder_email')
        if 'reminder_date_before_receipt' in vals:
            partner_values['reminder_date_before_receipt'] = vals.pop('reminder_date_before_receipt')
        return vals, partner_values

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'


    def create_order(self):
        purchase_order = self.env['purchase.order'].create({
            'partner_id': self.partner_id.id,
            'rfq_seq': self.name,
            'order_line': [(0, 0, {
                'product_id': line.product_id.id,
                'name': line.name,
                'product_qty': line.product_qty,
            }) for line in self.rfq_line],
        })
        self.state = "confirme"
        return {
            'name': 'Purchase Order',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'purchase.order',
            'res_id': purchase_order.id,
            'type': 'ir.actions.act_window',
            'target': 'current', }
        return


class PurchaseRfqLine(models.Model):
    _name = "purchase.rfq.line"
    _description = "Purchase RFQ Line"
    _rfq = 'rfq_id, sequence, id'

    name = fields.Text(string='Désignation', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    product_qty = fields.Float(string='Quantité', digits='Product Unit of Measure', required=True)
    product_uom_qty = fields.Float(string='Total Quantity', compute='_compute_product_uom_qty', store=True)
    date_planned = fields.Date(string='Date de Réception', index=True)
    product_uom = fields.Many2one('uom.uom', string='UdM',
                                  domain="[('category_id', '=', product_uom_category_id)]")
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
    product_id = fields.Many2one('product.product', string='Article', domain=[('purchase_ok', '=', True)],
                                 change_default=True)
    product_type = fields.Selection(related='product_id.type', readonly=True)

    rfq_id = fields.Many2one('purchase.rfq', string='RFQ Reference', index=True, required=True, ondelete='cascade')
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company.id)

    state = fields.Selection(related='rfq_id.state', store=True, readonly=False)

    partner_id = fields.Many2one('res.partner', related='rfq_id.partner_id', string='Fournisseur', readonly=True,
                                 store=True)
    date_rfq = fields.Date(related='rfq_id.date_rfq', string='Date demande', readonly=True)
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False)
