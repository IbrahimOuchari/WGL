from odoo import _, models
from odoo.exceptions import UserError


class StockMove(models.Model):
    _inherit = "stock.move"

    def action_back_to_draft(self):
        # if self.filtered(lambda m: m.state != "cancel"):
        #     raise UserError(_("Vous pouvez définir en brouillons uniquement les mouvements annulés"))
        self.write({"state": "draft"})

class StockPicking(models.Model):
    _inherit = "stock.picking"

    def action_back_to_draft(self):
        moves = self.mapped("move_lines")
        moves.action_back_to_draft()
