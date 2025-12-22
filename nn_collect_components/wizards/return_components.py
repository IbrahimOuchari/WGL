# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class MrpReturnComponentsWizard(models.TransientModel):
    _name = 'mrp.return.components.wizard'
    _description = 'Wizard to return components from production'

    production_id = fields.Many2one('mrp.production', string="OF", required=True)
    line_ids = fields.One2many('mrp.return.components.line', 'wizard_id', string="Lignes")

    @api.model
    def default_get(self, fields_list):
        res = super(MrpReturnComponentsWizard, self).default_get(fields_list)

        # Try both active_id and default_production_id for compatibility
        production_id = self._context.get('active_id') or self._context.get('default_production_id')

        if production_id:
            production = self.env['mrp.production'].browse(production_id)
            res['production_id'] = production.id

            lines = []
            product_moves = {}

            if production.state == 'done':
                if production.no_back_order:
                    # Only components with qty_in_prod > 0 AND not fully consumed
                    for move in production.move_raw_ids.filtered(
                            lambda m: m.qty_in_prod > 0 and m.product_id and m.product_uom_qty > m.quantity_done
                    ):
                        product_moves[move.product_id.id] = move
                else:
                    # All components with qty_in_prod > 0
                    for move in production.move_raw_ids.filtered(
                            lambda m: m.qty_in_prod > 0 and m.product_id
                    ):
                        product_moves[move.product_id.id] = move
            else:  # cancel state
                for move in production.move_raw_ids.filtered(
                        lambda m: m.qty_in_prod > 0 and m.product_id
                ):
                    product_moves[move.product_id.id] = move

            # Create lines from the filtered moves
            for move in product_moves.values():
                lines.append((0, 0, {
                    'product_id': move.product_id.id,
                    'qty_in_prod': move.qty_in_prod,
                    'qty_return': move.qty_in_prod,
                }))

            res['line_ids'] = lines

        return res

    def action_confirm(self):
        """Create stock picking RC for selected quantities"""
        self.ensure_one()
        # Get the picking type (code_sequence RC)
        picking_type = self.env['stock.picking.type'].search([('sequence_code', '=', 'RC')], limit=1)
        if not picking_type:
            raise UserError(_("Aucun type d'opération RC trouvé."))

        # Filter lines with qty_return > 0
        lines_to_return = self.line_ids.filtered(lambda l: l.qty_return > 0)
        if not lines_to_return:
            raise UserError(_("Aucune quantité à retourner n'a été saisie."))

        # Create picking
        picking_vals = {
            'picking_type_id': picking_type.id,
            'origin': self.production_id.name,
            'location_id': picking_type.default_location_src_id.id,
            'location_dest_id': picking_type.default_location_dest_id.id,
            'move_lines': [],
        }

        move_vals = []
        for line in lines_to_return:
            # Validate qty_return doesn't exceed qty_in_prod
            if line.qty_return > line.qty_in_prod:
                raise UserError(_(
                    "La quantité à retourner (%.2f) pour %s ne peut pas dépasser la quantité en production (%.2f)."
                ) % (line.qty_return, line.product_id.display_name, line.qty_in_prod))

            move_vals.append((0, 0, {
                'product_id': line.product_id.id,
                'name': line.product_id.display_name,
                'product_uom_qty': line.qty_return,
                'product_uom': line.product_id.uom_id.id,
                'location_id': picking_type.default_location_src_id.id,
                'location_dest_id': picking_type.default_location_dest_id.id,
            }))
            # Reduce qty_in_prod in corresponding move_raw_ids

        picking_vals['move_lines'] = move_vals
        picking = self.env['stock.picking'].create(picking_vals)
        self.production_id.return_operation_count+=1
        # picking.action_confirm()

        return {
            'type': 'ir.actions.act_window',
            'name': _('Retour composants'),
            'res_model': 'stock.picking',
            'view_mode': 'form',
            'res_id': picking.id,
            'target': 'current',
        }


class MrpReturnComponentsLine(models.TransientModel):
    _name = 'mrp.return.components.line'
    _description = 'Line for returning components'

    wizard_id = fields.Many2one(
        'mrp.return.components.wizard',
        string="Wizard",
        required=True,
        ondelete='cascade'
    )
    product_id = fields.Many2one(
        'product.product',
        string="Produit",
        # keep readonly if you only want lines populated from default_get,
        # but don't enforce required at ORM-level to avoid confusing default UI errors.
        readonly=False
    )
    qty_in_prod = fields.Float(string="Quantité en production", readonly=False)
    qty_return = fields.Float(string="Quantité à retourner", default=0.0)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        """If product selected, fill qty_in_prod from the production's raw move and default qty_return."""
        if not self.product_id:
            self.qty_in_prod = 0.0
            self.qty_return = 0.0
            return
        if self.wizard_id and self.wizard_id.production_id:
            raw_move = self.wizard_id.production_id.move_raw_ids.filtered(
                lambda m: m.product_id == self.product_id
            )
            qty = raw_move and raw_move[0].qty_in_prod or 0.0
            self.qty_in_prod = qty
            # if qty_return empty, default to qty_in_prod
            if not self.qty_return:
                self.qty_return = qty

    @api.onchange('product_id')
    def _onchange_product_id(self):
        """If product selected, fill qty_in_prod from the production's raw move and default qty_return."""
        if not self.product_id:
            self.qty_in_prod = 0.0
            self.qty_return = 0.0
            return
        if self.wizard_id and self.wizard_id.production_id:
            raw_move = self.wizard_id.production_id.move_raw_ids.filtered(
                lambda m: m.product_id == self.product_id
            )
            qty = raw_move and raw_move[0].qty_in_prod or 0.0
            self.qty_in_prod = qty
            # if qty_return empty, default to qty_in_prod
            if not self.qty_return:
                self.qty_return = qty

    @api.onchange('qty_return', 'product_id', 'qty_in_prod')
    def _onchange_qty_return_validation(self):
        """Validate qty_return in real-time"""
        # Check if product is selected
        if not self.product_id:
            return {
                'warning': {
                    'title': _("Produit manquant"),
                    'message': _("Veuillez sélectionner un produit pour cette ligne.")
                }
            }

        # Check for negative quantity
        if self.qty_return < 0:
            return {
                'warning': {
                    'title': _("Quantité invalide"),
                    'message': _("La quantité à retourner ne peut pas être négative.")
                }
            }

        # Check if qty_return exceeds qty_in_prod
        if self.qty_return > self.qty_in_prod:
            return {
                'warning': {
                    'title': _("Quantité trop élevée"),
                    'message': _(
                        "La quantité à retourner (%.2f) pour %s ne peut pas dépasser la quantité en production (%.2f)."
                    ) % (self.qty_return, self.product_id.display_name, self.qty_in_prod)
                }
            }