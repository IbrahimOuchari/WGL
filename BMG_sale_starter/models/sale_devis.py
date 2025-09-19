from odoo import fields, models, api, _
from functools import partial
from odoo.tools.misc import formatLang, get_lang
from datetime import datetime, timedelta


class SaleDevis(models.Model):
    _name = "sale.devis"
    _description = "New Page Sales Devis Modules"

    name = fields.Char(string='Sequence Devis', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('Nouveau'))
    partner_id = fields.Many2one(
        'res.partner', string='Client', readonly=False,

        required=True, change_default=True, index=True, tracking=1, )

    state = fields.Selection([
        ('devis', 'Devis'),
        ('confirme', 'Confirmé'),
        ('expired', 'Expiré'),
        ('cancel', 'Annulé'),
    ], string='Status', readonly=True, copy=False, index=True, tracking=True,
        default='devis', store=True)

    @api.model
    def _get_default_team(self):
        return self.env['crm.team']._get_default_team_id()

    # Sequence de devis
    @api.model
    def create(self, vals):
        if 'name' not in vals or vals['name'] == _('Nouveau'):
            vals['name'] = self.env['ir.sequence'].next_by_code('sale.devis') or _('Nouveau')
        return super(SaleDevis, self).create(vals)

    def _default_validity_date(self):
        if self.env['ir.config_parameter'].sudo().get_param('sale.use_quotation_validity_days'):
            days = self.env.company.quotation_validity_days
            if days > 0:
                return fields.Date.to_string(datetime.now() + timedelta(days))
        return False

    @api.depends('validity_date')
    def _compute_is_expired(self):
        today = fields.Date.today()
        for order in self:
            order.is_expired = order.state == 'devis' and order.validity_date and order.validity_date < today

    @api.depends('is_expired', 'state')
    def _compute_expired_state(self):
        for state in self:
            if state.is_expired:
                state.status_devis = '3'
            elif state.state == 'confirme':
                state.status_devis = '2'
            elif state.state == 'cancel':
                state.status_devis = '4'
            else:
                state.status_devis = '1'

    status_devis = fields.Selection([('1', 'Devis'), ('2', 'Commande'), ('3', 'Expiré'), ('4', 'Annulé')],
                                    string="Status Devis",
                                    default="1", readonly=True, compute="_compute_expired_state", store=True)

    is_expired = fields.Boolean(compute='_compute_is_expired', string="Expiré")

    date_devis = fields.Date(string='Date Devis', required=True)
    validity_date = fields.Date(string='Date d\'Expiration', required=True, default=_default_validity_date)
    company_id = fields.Many2one('res.company', 'Société', required=True, index=True,
                                 default=lambda self: self.env.company)

    payment_term_id = fields.Many2one('account.payment.term', string='Condition de paiement', check_company=True,
                                      domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", )

    devis_line = fields.One2many('sale.devis.line', 'devis_id', string='Ligne de Devis')

    def _get_update_prices_lines(self):
        return self.order_line.filtered(lambda line: not line.display_type)

    def update_prices(self):
        self.ensure_one()
        for line in self._get_update_prices_lines():
            line.product_uom_change()
            line.discount = 0  # Force 0 as discount for the cases when _onchange_discount directly returns
            line._onchange_discount()
        self.show_update_pricelist = False
        self.message_post(body=_("Product prices have been recomputed according to pricelist <b>%s<b> ",
                                 self.pricelist_id.display_name))

    show_update_pricelist = fields.Boolean(string='Has Pricelist Changed')

    pricelist_id = fields.Many2one(
        'product.pricelist', string='Liste des Prix', check_company=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", tracking=1)
    currency_id = fields.Many2one('res.currency', compute='_compute_currency', store=True, digits=(12, 6),
                                  readonly=True, compute_sudo=True)
    tag_ids = fields.Many2many('crm.tag', 'tag_id', string='Tags')
    user_id = fields.Many2one(
        'res.users', string='Commercial', index=True, tracking=2, default=lambda self: self.env.user,
        domain=lambda self: "[('groups_id', '=', {}), ('share', '=', False), ('company_ids', '=', company_id)]".format(
            self.env.ref("sales_team.group_sale_salesman").id
        ), )
    team_id = fields.Many2one(
        'crm.team', 'Sales Team',
        change_default=True, default=_get_default_team, check_company=True,  # Unrequired company
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    fiscal_position_id = fields.Many2one(
        'account.fiscal.position', string='Position Fiscale',
        domain="[('company_id', '=', company_id)]", check_company=True)

    @api.depends('pricelist_id')
    def _compute_currency(self):
        for record in self:
            if record.pricelist_id:
                record.currency_id = record.pricelist_id.currency_id
            else:
                record.currency_id = record.company_id.currency_id

    @api.onchange('pricelist_id', 'devis_line')
    def _onchange_pricelist_id(self):
        if self.devis_line and self.pricelist_id and self._origin.pricelist_id != self.pricelist_id:
            self.show_update_pricelist = True
        else:
            self.show_update_pricelist = False

    # Total Devis
    note = fields.Text('Terms and conditions')
    amount_untaxed = fields.Monetary(string='Montant H.T.', store=True, readonly=True, compute='_amount_all',
                                     tracking=5)
    amount_by_group = fields.Binary(string="Tax amount by group", compute='_amount_by_group',
                                    help="type: [(name, amount, base, formated amount, formated base)]")
    amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_amount_all')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all', tracking=4)

    # currency_rate = fields.Float("Currency Rate", compute='_compute_currency_rate', compute_sudo=True, store=True,
    #                         digits=(12, 6), readonly=True,)

    @api.depends('devis_line.price_subtotal')
    def _amount_all(self):
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.devis_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            order.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax,
            })

    def _amount_by_group(self):
        for order in self:
            currency = order.currency_id or order.company_id.currency_id
            fmt = partial(formatLang, self.with_context(lang=order.partner_id.lang).env, currency_obj=currency)
            res = {}
            for line in order.devis_line:
                price_reduce = line.price_unit * (1.0 - line.discount / 100.0)
                taxes = line.tax_id.compute_all(price_reduce, quantity=line.qty, product=line.product_id,
                                                partner=order.partner_id)['taxes']
                for tax in line.tax_id:
                    group = tax.tax_group_id
                    res.setdefault(group, {'amount': 0.0, 'base': 0.0})
                    for t in taxes:
                        if t['id'] == tax.id or t['id'] in tax.children_tax_ids.ids:
                            res[group]['amount'] += t['amount']
                            res[group]['base'] += t['base']
            res = sorted(res.items(), key=lambda l: l[0].sequence)
            order.amount_by_group = [(
                l[0].name, l[1]['amount'], l[1]['base'],
                fmt(l[1]['amount']), fmt(l[1]['base']),
                len(res),
            ) for l in res]

    devis_line_option = fields.One2many('sale.devis.line.option', 'devis_id', string='Article Optionnel')

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if not self.partner_id:
            self.update({
                'fiscal_position_id': False,
            })
            return

        self = self.with_company(self.company_id)

        partner_user = self.partner_id.user_id or self.partner_id.commercial_partner_id.user_id
        values = {
            'pricelist_id': self.partner_id.property_product_pricelist and self.partner_id.property_product_pricelist.id or False,
            'payment_term_id': self.partner_id.property_payment_term_id and self.partner_id.property_payment_term_id.id or False,
        }
        user_id = partner_user.id
        if not self.env.context.get('not_self_saleperson'):
            user_id = user_id or self.env.context.get('default_user_id', self.env.uid)
        if user_id and self.user_id.id != user_id:
            values['user_id'] = user_id

        if self.env['ir.config_parameter'].sudo().get_param(
                'account.use_invoice_terms') and self.env.company.invoice_terms:
            values['note'] = self.with_context(lang=self.partner_id.lang).env.company.invoice_terms
        if not self.env.context.get('not_self_saleperson') or not self.team_id:
            values['team_id'] = self.env['crm.team'].with_context(
                default_team_id=self.partner_id.team_id.id
            )._get_default_team_id(domain=['|', ('company_id', '=', self.company_id.id), ('company_id', '=', False)],
                                   user_id=user_id)
        self.update(values)

    # Création BC depuis le Devis

    def create_order(self):
        sale_order = self.env['sale.order'].create({
            'partner_id': self.partner_id.id,
            'devis_seq': self.name,
            'order_line': [(0, 0, {
                'product_id': line.product_id.id,
                'name': line.name,
                'product_uom_qty': line.qty,
                'price_unit': line.price_unit,
                'discount': line.discount,
            }) for line in self.devis_line],
        })
        self.state = "confirme"
        return {
            'name': 'Sale Order',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sale.order',
            'res_id': sale_order.id,
            'type': 'ir.actions.act_window',
            'target': 'current', }
        return


class SaleDevisLine(models.Model):
    _name = 'sale.devis.line'
    _description = 'Sales Devis Line'

    name = fields.Text(string='Description', index=True, required=True)
    sequence = fields.Integer(string='Sequence', default=10)

    devis_id = fields.Many2one('sale.devis', string='Devis Reference', required=True, ondelete='cascade', index=True,
                               copy=False)
    partner_id = fields.Many2one('res.partner', string='Client')
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")

    product_id = fields.Many2one('product.product', string='Produit')
    description = fields.Text(string='Description')
    qty = fields.Float(string='Quantité', digits='Product Unit of Measure', required=True, )
    product_uom = fields.Many2one('uom.uom', string='Unité de Mesure')
    price_unit = fields.Float(string='P.U.', digits='Product Price')
    tax_id = fields.Many2many('account.tax', string='T.V.A.')
    discount = fields.Float(string='Remise (%)', digits='Discount', default=0)
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id', readonly=True)
    pu_remise = fields.Float(string='P.U. Après Remise', compute='_compute_amount_pu_remise')
    price_subtotal = fields.Monetary(compute='_compute_amount_ht', string='Montant H.T.', readonly=True, store=True)
    currency_id = fields.Many2one(related='devis_id.currency_id', depends=['devis_id.currency_id'], store=True,
                                  string='Devise', readonly=True)
    price_tax = fields.Float(compute='_compute_amount_tax', string='Total Tax', readonly=True, store=True)
    company_id = fields.Many2one(related="devis_id.company_id")

    # Remplir les lignes de devis avec les champs articles
    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.name = self.product_id.name
            self.price_unit = self.product_id.lst_price
            self.product_uom = self.product_id.uom_id.id
            self.tax_id = self.product_id.taxes_id.ids

    # Calcul Total ligne devis
    @api.depends('discount', 'price_unit')
    def _compute_amount_pu_remise(self):
        for line in self:
            if line.discount:
                line.pu_remise = line.price_unit * ((100 - line.discount) / 100)
            else:
                line.pu_remise = 0

    @api.depends('qty', 'price_unit', 'pu_remise')
    def _compute_amount_ht(self):
        for line in self:
            if line.pu_remise == 0:
                line.price_subtotal = line.price_unit * line.qty
            else:
                line.price_subtotal = line.pu_remise * line.qty

    @api.depends('price_subtotal', 'tax_id')
    def _compute_amount_tax(self):
        for line in self:
            taxes_amount = sum(tax.amount / 100 for tax in line.tax_id)
            line.price_tax = line.price_subtotal * taxes_amount


class SaleDevisLineOption(models.Model):
    _name = 'sale.devis.line.option'
    _description = 'Sales Devis Line Option'

    name = fields.Text(string='Description', index=True, required=True)
    sequence = fields.Integer(string='Sequence', default=10)

    devis_id = fields.Many2one('sale.devis', string='Devis Reference', required=True, ondelete='cascade', index=True,
                               copy=False)
    partner_id = fields.Many2one('res.partner', string='Client')
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")

    product_id = fields.Many2one('product.product', string='Produit')
    description = fields.Text(string='Description')
    qty = fields.Float(string='Quantité', digits='Product Unit of Measure', required=True, )
    product_uom = fields.Many2one('uom.uom', string='Unité de Mesure')
    price_unit = fields.Float(string='P.U.', digits='Product Price')
    tax_id = fields.Many2many('account.tax', string='T.V.A.')
    discount = fields.Float(string='Remise (%)', digits='Discount', default=0)
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id', readonly=True)
    pu_remise = fields.Float(string='P.U. Après Remise', compute='_compute_amount_pu_remise')
    price_subtotal = fields.Monetary(compute='_compute_amount_ht', string='Montant H.T.', readonly=True, store=True)
    currency_id = fields.Many2one(related='devis_id.currency_id', depends=['devis_id.currency_id'], store=True,
                                  string='Devise', readonly=True)
    price_tax = fields.Float(compute='_compute_amount_tax', string='Total Tax', readonly=True, store=True)

    # Remplir les lignes de devis avec les champs articles
    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.name = self.product_id.name
            self.price_unit = self.product_id.lst_price
            self.product_uom = self.product_id.uom_id.id
            self.tax_id = self.product_id.taxes_id.ids

    # Calcul Total ligne devis
    @api.depends('discount', 'price_unit')
    def _compute_amount_pu_remise(self):
        for line in self:
            if line.discount:
                line.pu_remise = line.price_unit * ((100 - line.discount) / 100)
            else:
                line.pu_remise = 0

    @api.depends('qty', 'price_unit', 'pu_remise')
    def _compute_amount_ht(self):
        for line in self:
            if line.pu_remise == 0:
                line.price_subtotal = line.price_unit * line.qty
            else:
                line.price_subtotal = line.pu_remise * line.qty

    @api.depends('price_subtotal', 'tax_id')
    def _compute_amount_tax(self):
        self.price_tax = self.price_subtotal * (self.tax_id.amount / 100)
