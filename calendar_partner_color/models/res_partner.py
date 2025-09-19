
from random import randint

from odoo import fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    def _get_default_color(self):
        return randint(0, 29)

    color = fields.Integer(default=_get_default_color)
