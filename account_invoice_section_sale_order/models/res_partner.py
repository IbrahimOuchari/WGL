
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    invoice_section_name_scheme = fields.Char(
        help="This is the name of the sections on invoices when generated from "
        "sales orders. Keep empty to use default. You can use a python "
        "expression with the 'object' (representing sale order) and 'time'"
        " variables."
    )
