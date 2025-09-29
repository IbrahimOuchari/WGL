from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    discount_rate = fields.Float(string='Taux Remise(%)', digits=(16, 3), groups="nn_reporting.group_manager_report_id",
                                 )
    pu_after_discount = fields.Float(string='Prix après remise', digits=(16, 3), compute='compute_pu_after_discount',
                                     store=True, groups="nn_reporting.group_manager_report_id",
                                     )

    @api.depends('discount_rate', 'list_price', 'sale_ok')
    def compute_pu_after_discount(self):
        for rec in self:
            if rec.sale_ok:
                rec.pu_after_discount = rec.list_price - (rec.list_price * rec.discount_rate / 100)

    marge_brute = fields.Float(
        string="Marge Brute",
        compute="compute_marge_brute",
        store=True,
        groups="nn_reporting.group_manager_report_id",

    )

    @api.depends('list_price','discount_rate','pu_after_discount', 'standard_price')
    def compute_marge_brute(self):
        for product in self:
            product.marge_brute = product.pu_after_discount - product.standard_price
