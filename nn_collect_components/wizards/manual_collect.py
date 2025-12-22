# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class MrpManualCollectComponentsWizard(models.TransientModel):
    _name = 'mrp.manual.collect.components.wizard'
    _description = 'Wizard to manually collect components for production'

    production_id = fields.Many2one('mrp.production', string="OF", required=True)
    line_ids = fields.One2many('mrp.manual.collect.components.line', 'wizard_id', string="Lignes")

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        production_id = self._context.get('active_id')
        if production_id:
            production = self.env['mrp.production'].browse(production_id)
            res['production_id'] = production.id

            lines = []
            # Only include moves that are fully delivered (qty_left <= 0)
            for move in production.move_raw_ids.filtered(lambda m: m.qty_left <= 0):
                lines.append((0, 0, {
                    'product_id': move.product_id.id,
                    'qty_to_collect': move.qty_in_prod,  # qty remaining in production
                }))
            res['line_ids'] = lines
        return res

    def action_confirm(self):
        """Create stock picking PC for selected quantities"""
        self.ensure_one()

        # Get the picking type (code_sequence PC)
        picking_type = self.env['stock.picking.type'].search([('sequence_code', '=', 'PC')], limit=1)
        if not picking_type:
            raise UserError(_("Aucun type d'opération PC trouvé."))

        # Filter lines with qty_to_collect > 0
        lines_to_collect = self.line_ids.filtered(lambda l: l.qty_to_collect > 0)
        if not lines_to_collect:
            raise UserError(_("Aucune quantité à collecter n'a été saisie."))

        # Create picking with group_id from production
        picking_vals = {
            'picking_type_id': picking_type.id,
            'group_id': self.production_id.procurement_group_id.id,
            'origin': self.production_id.name,
            'manual_collect': True,
            'location_id': picking_type.default_location_src_id.id,
            'location_dest_id': picking_type.default_location_dest_id.id,
            'move_lines': [],
        }

        move_vals = []
        for line in lines_to_collect:
            move_vals.append((0, 0, {
                'product_id': line.product_id.id,
                'name': line.product_id.display_name,
                'product_uom_qty': line.qty_to_collect,
                'product_uom': line.product_id.uom_id.id,
                'location_id': picking_type.default_location_src_id.id,
                'location_dest_id': picking_type.default_location_dest_id.id,
                'group_id': self.production_id.procurement_group_id.id,
            }))

        picking_vals['move_lines'] = move_vals
        picking = self.env['stock.picking'].create(picking_vals)

        return {
            'type': 'ir.actions.act_window',
            'name': _('Collecte manuelle des composants'),
            'res_model': 'stock.picking',
            'view_mode': 'form',
            'res_id': picking.id,
            'target': 'current',
        }


class MrpManualCollectComponentsLine(models.TransientModel):
    _name = 'mrp.manual.collect.components.line'
    _description = 'Line for manual collection of components'

    wizard_id = fields.Many2one(
        'mrp.manual.collect.components.wizard',
        string="Wizard",
        required=True,
        ondelete='cascade'
    )
    product_id = fields.Many2one(
        'product.product',
        string="Produit",
        required=True
    )
    qty_to_collect = fields.Float(string="Quantité à collecter", default=0.0)

    @api.constrains('qty_to_collect', 'product_id')
    def _check_qty_to_collect(self):
        for line in self:
            if line.qty_to_collect < 0:
                raise UserError(_("La quantité à collecter ne peut pas être négative."))
