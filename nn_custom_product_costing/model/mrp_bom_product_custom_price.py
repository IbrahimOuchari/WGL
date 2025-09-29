from unicodedata import digit
from odoo.exceptions import ValidationError

from odoo import models, fields, api


class MrpBomCustomFields(models.Model):
    _inherit = 'mrp.bom'

    is_calculated = fields.Boolean(
        string="Calculer Coût",default=True,
        help="Activez pour utiliser cette nomenclature dans le calcul des coûts du produit."
    )

    total_cost = fields.Float(
        string="Coût Total",
        compute="_compute_total_cost",
        digits='Product Price',
        help="Somme des prix standards des composants dans les lignes de nomenclature."
    )


    @api.depends('is_calculated', 'total_cost')
    def reset_is_calculated_if_cost_zero(self):
        for bom in self:
            if bom.is_calculated and (not bom.total_cost or bom.total_cost == 0):
                bom.is_calculated = False

    # @api.constrains('is_calculated', 'product_tmpl_id')
    # def _check_unique_is_calculated_per_product(self):
    #     for bom in self:
    #         if bom.is_calculated:
    #             # Look for another BOM for same product with is_calculated = True
    #             other_bom = self.search([
    #                 ('product_tmpl_id', '=', bom.product_tmpl_id.id),
    #                 ('is_calculated', '=', True),
    #                 ('id', '!=', bom.id)
    #             ], limit=1)
    #
    #             if other_bom:
    #                 raise ValidationError(
    #                     f"❌ Une autre nomenclature est déjà marquée comme 'Calculer Coût' pour cet article.\n"
    #                     f"👉 Code : {other_bom.code or 'Sans Référence'}\n"
    #                     f"💰 Coût total : {other_bom.total_cost:.2f} \n\n"
    #                     f"Vous devez d'abord désactiver 'Calculer Coût' sur cette autre nomenclature."
    #                 )

    @api.model
    def create(self, vals):
        """
        Override create to ensure only one BOM per product has is_calculated=True.

        Steps:
        1. Call super().create(vals) to create the new BOM record.
        2. Search for other BOMs of the same product that are marked as is_calculated=True.
           - Exclude the newly created record using res.id.
        3. If any other BOMs are found, set their is_calculated to False.
        4. Ensure the newly created BOM keeps is_calculated=True.
        5. Return the newly created record.
        """
        res = super(MrpBomCustomFields, self).create(vals)

        # Find other BOMs for the same product marked as calculated
        check_is_calculated = self.search([
            ('product_tmpl_id', '=', res.product_tmpl_id.id),
            ('is_calculated', '=', True),
            ('id', '!=', res.id)  # exclude the newly created BOM
        ])

        if check_is_calculated:
            # Unset is_calculated on other BOMs
            check_is_calculated.write({'is_calculated': False})
            # Ensure the newly created record remains is_calculated
            res.is_calculated = True

        return res

    def write(self, vals):
        """
        Override write to ensure only one BOM per product has is_calculated=True when updating records.

        Steps:
        1. Call super().write(vals) to apply the updates.
        2. If the write changes is_calculated to True:
           - Iterate over the records being updated.
           - Search for other BOMs of the same product with is_calculated=True.
           - Exclude the current record using bom.id.
           - Set is_calculated=False on all other BOMs.
        3. Return the result of super().write(vals).
        """
        res = super(MrpBomCustomFields, self).write(vals)

        if vals.get('is_calculated'):
            for bom in self:
                if bom.is_calculated:
                    # Find other BOMs of the same product marked as calculated
                    other_boms = self.search([
                        ('product_tmpl_id', '=', bom.product_tmpl_id.id),
                        ('is_calculated', '=', True),
                        ('id', '!=', bom.id)  # exclude the current record
                    ])
                    if other_boms:
                        # Unset is_calculated on other BOMs
                        other_boms.write({'is_calculated': False})

        return res

    @api.depends('bom_line_ids.standard_price_calculated')
    def _compute_total_cost(self):
        """Compute the total cost of the BOM based on the calculated cost of its components."""
        for bom in self:
            # Sum up the 'standard_price_calculated' field of all BOM lines
            bom.total_cost = sum(line.standard_price_calculated for line in bom.bom_line_ids)

    def action_call_calculate_standard_price_calculated(self):
        for line in self.bom_line_ids:
            # Call the method on each BOM line
            line.calculate_standard_price_calculated()



class MrpBomLineCustomFields(models.Model):
    _inherit = 'mrp.bom.line'

    standard_price_related_product = fields.Float(
        string="Coût",
        related="product_id.standard_price",
        readonly=True,store=True,
        help="Prix standard du composant, lié au champ standard_price dans le produit."
    )
    standard_price_related_template = fields.Float(
        string="Coût",
        related="product_tmpl_id.standard_price",
        readonly=True,store=True,
        help="Prix standard du composant, lié au champ standard_price dans le produit."
    )
    standard_price_calculated = fields.Float(
        string="Coût Calculé",
        compute="_compute_standard_price_calculated",
        digits= (16,3),
        help="Coût calculé en multipliant le prix standard par la quantité du produit.",store=True
    )

    @api.depends('standard_price_related_template', 'standard_price_related_product', 'product_qty')
    def _compute_standard_price_calculated(self):
        for line in self:
            if line.standard_price_related_product:
                line.standard_price_calculated = line.standard_price_related_product * line.product_qty
            else:
                line.standard_price_calculated = line.standard_price_related_template * line.product_qty



    def calculate_standard_price_calculated(self):
        """Compute the calculated cost as standard price multiplied by product quantity."""
        for line in self:
            if line.standard_price_related_product:
                line.standard_price_calculated = line.standard_price_related_product * line.product_qty
            else:
                line.standard_price_calculated = line.standard_price_related_template * line.product_qty


    cost_product = fields.Boolean(compute="price_cost")

    @api.depends('standard_price_calculated')
    def price_cost(self):
        for line in self:
            if line.standard_price_calculated == 0:
                line.cost_product = True
            else:
                line.cost_product = False
