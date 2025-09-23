from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    bom_cost = fields.Float(
        string="Coût de la nomenclature",
        compute="compute_bom_cost",
        readonly=False,
        help="Coût total de la nomenclature sélectionnée.",store=True,
    )
    exploitation_charge_percent = fields.Float(
        string="% Charge d’exploitation",
        help="Pourcentage manuel de charge d’exploitation.",
    )
    exploitation_cost = fields.Float(
        string="Coût d’exploitation",
        compute="_compute_exploitation_cost",
        readonly=False,
        help="Calculé comme: (Bom Cost * (100 + % Charge d’exploitation)) / 100."
    )
    total_cost = fields.Float(
        string="Coût de revient total",
        compute="_compute_total_cost",
        readonly=False,
        help="Calculé comme: Bom Cost + Coût d’exploitation."
    )

    @api.depends('bom_ids.total_cost','bom_count', 'bom_ids','bom_ids.is_calculated','bom_cost')
    def compute_bom_cost(self):
        for product in self:
            # Filter to only calculated BOMs (regardless of cost)
            calculated_boms = product.bom_ids.filtered(lambda b: b.is_calculated)

            # Sort them by descending ID (latest first)
            sorted_boms = calculated_boms.sorted(key=lambda b: b.id, reverse=True)

            # Find the first one that has a total_cost > 0
            valid_bom = next((bom for bom in sorted_boms if bom.total_cost and bom.total_cost > 0), None)

            # Set the cost
            product.bom_cost = valid_bom.total_cost if valid_bom else 0



    def action_compute_bom_cost(self):
        """Manually compute the total BOM cost based on the latest calculated BOM."""
        for product in self:
            # Filter to only calculated BOMs (regardless of cost)
            calculated_boms = product.bom_ids.filtered(lambda b: b.is_calculated)

            # Sort them by descending ID (latest first)
            sorted_boms = calculated_boms.sorted(key=lambda b: b.id, reverse=True)

            # Find the first one that has a total_cost > 0
            valid_bom = next((bom for bom in sorted_boms if bom.total_cost and bom.total_cost > 0), None)

            # Set the cost
            product.bom_cost = valid_bom.total_cost if valid_bom else 0.0

    @api.depends('bom_cost', 'exploitation_charge_percent')
    def _compute_exploitation_cost(self):
        """Compute the exploitation cost based on BOM cost and exploitation charge percentage."""
        for product in self:
            product.exploitation_cost = (product.bom_cost * product.exploitation_charge_percent) / 100

    @api.depends('bom_cost', 'exploitation_cost')
    def _compute_total_cost(self):
        """Compute the total cost as BOM cost + exploitation cost."""
        for product in self:
            product.total_cost = product.bom_cost + product.exploitation_cost

    bom_cost_set = fields.Boolean(string="BoM set and BOM_cost false",compute='compute_bom_notset',default=False)
    bom_exist = fields.Boolean(string="BoM set ",compute='compute_bom_notset', default=False)


    @api.depends('bom_ids', 'bom_ids.total_cost', 'bom_cost')
    def compute_bom_notset(self):
        for product in self:
            boms = product.bom_ids

            # Default value
            if not boms:
                product.bom_cost_set = False
                product.bom_exist = False
            else:
                product.bom_exist = True

            if boms:
                # Check if at least one BOM has total_cost > 0
                one_bom_has_cost = any(bom.total_cost and bom.total_cost > 0 for bom in boms)

                if one_bom_has_cost and (not product.bom_cost or product.bom_cost <= 0):
                    product.bom_cost_set = False
                if one_bom_has_cost and (product.bom_cost and product.bom_cost > 0):
                    product.bom_cost_set = True


class ProductProduct(models.Model):
    _inherit = 'product.product'

    bom_cost_set = fields.Boolean(related="product_tmpl_id.bom_cost_set")
