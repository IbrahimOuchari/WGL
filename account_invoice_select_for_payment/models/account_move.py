

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    selected_for_payment = fields.Boolean("A Payer")

    def action_toggle_select_for_payment(self):
        selected = self.filtered(lambda rec: rec.selected_for_payment)
        unselected = self - selected
        if selected:
            selected.write({"selected_for_payment": False})
        if unselected:
            unselected.write({"selected_for_payment": True})
