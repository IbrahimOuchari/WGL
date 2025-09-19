
from odoo import models
from odoo.tools import config


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    #Ne modifie pas le prix quand le BC line est modifié
    def _onchange_eval(self, field_name, onchange, result):
        ctx = self.env.context
        if field_name in {"product_uom_qty", "product_uom"} and (
            not config["test_enable"]
            or (config["test_enable"] and ctx.get("prevent_onchange_quantity", False))
        ):
            cls = type(self)
            for method in self._onchange_methods.get(field_name, ()):
                if method == cls.product_uom_change:
                    self._onchange_methods[field_name].remove(method)
                    break
        return super()._onchange_eval(field_name, onchange, result)

    #fin

