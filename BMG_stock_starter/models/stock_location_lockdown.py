from odoo import _, fields, models, api
from odoo.exceptions import UserError, ValidationError


# Interdir stock dans emplacement interne

class StockLocation(models.Model):
    _inherit = "stock.location"

    block_stock_entrance = fields.Boolean(
        help="si cette case est cochée, mettre du stock sur cet emplacement ne sera pas "
             "autorisé. Habituellement utilisé pour un emplacement virtuel qui a "
             "des enfants."
    )

    # Générer une erreur si l'emplacement que vous essayez de bloquer a déjà des quants
    def write(self, values):
        res = super().write(values)

        if "block_stock_entrance" in values and values["block_stock_entrance"]:
            # Unlink zero quants before checking
            # if there are quants on the location
            self.env["stock.quant"]._unlink_zero_quants()
            if self.mapped("quant_ids"):
                raise UserError(
                    _(
                        "Il est impossible d'interdire cet emplacement\
                     recevoir des produits car il en contient déjà."
                    )
                )
        return res


class StockQuant(models.Model):
    _inherit = "stock.quant"

    # Génère une erreur lors d'une tentative de modification d'un quant dont l'emplacement de stock correspondant est bloqué
    @api.constrains("location_id")
    def check_location_blocked(self):
        for record in self:
            if record.location_id.block_stock_entrance:
                raise ValidationError(
                    _(
                        "L'emplacement %s est bloqué et ne peut "
                        "pas être utilisé pour déplacer le produit %s"
                    )
                    % (record.location_id.display_name, record.product_id.display_name)
                )
