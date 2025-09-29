from odoo import fields, models, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    discount_rate = fields.Float(related='product_tmpl_id.discount_rate',groups="nn_reporting.group_manager_report_id",
                                 )
    pu_after_discount = fields.Float(related='product_tmpl_id.pu_after_discount', groups="nn_reporting.group_manager_report_id",
                                     )
