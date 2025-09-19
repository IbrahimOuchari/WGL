from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    marge_brute = fields.Float(
        string="Marge Brute",
        compute="_compute_marge_brute",
        store=True
    )

    @api.depends('list_price', 'standard_price')
    def _compute_marge_brute(self):
        for product in self:
            product.marge_brute = product.list_price - product.standard_price

    decoration_danger = fields.Boolean(
        string="Decoration DANGER",
        default=False,
        compute="_compute_marge_product",
        store=True
    )

    def compute_marge_product(self):
        for record in self:
            if record.marge_brute <= 0 or record.marge_brute == 0:
                record.decoration_danger = True

    @api.onchange('marge_brute')
    def _compute_marge_product(self):
        for record in self:
            if record.marge_brute <= 0 or record.marge_brute == 0:
                record.decoration_danger = True


class ProductProduct(models.Model):
    _inherit = "product.product"

    marge_brute = fields.Float(
        string="Marge Brute",
        related="product_tmpl_id.marge_brute",
        store=True
    )
