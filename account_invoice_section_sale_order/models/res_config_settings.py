
from odoo import fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    invoice_section_name_scheme = fields.Char(
        related="company_id.invoice_section_name_scheme",
        readonly=False,
    )

    invoice_section_grouping = fields.Selection(
        related="company_id.invoice_section_grouping",
        readonly=False,
        required=True,
    )
