# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from collections import Counter

_logger = logging.getLogger(__name__)


# ============================================================
#   MRP PRODUCTION EXTENSION
# ============================================================
class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    # ------------------------------------------------------------
    #   Count of returned components
    # ------------------------------------------------------------
    returned_components_count = fields.Integer(
        string='Return composants',
        compute='compute_return_components'
    )
    return_operation_count = fields.Integer(
        string='Return operations',
    )
    # ------------------------------------------------------------
    #   Compute: Count return components operations
    # ------------------------------------------------------------
    @api.depends('picking_ids', 'move_raw_ids','return_operation_count')
    def compute_return_components(self):
        Picking = self.env['stock.picking']
        for mrp in self:
            # Count done RT pickings
            rt_operations = Picking.search([
                ('origin', '=', mrp.name),
                ('picking_type_id.sequence_code', '=', 'RC'),
                ('state', 'in', ['assigned', 'confirmed', 'done'])
            ])
            if rt_operations:
                mrp.returned_components_count = len(rt_operations)
                mrp.compute_update_returned()
            else:
                mrp.returned_components_count = 0

    # ------------------------------------------------------------
    #   Action: View return operations
    # ------------------------------------------------------------
    def action_view_total_return_operations(self):
        self.ensure_one()
        return {
            'name': 'Retour des Composants',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            'domain': [('origin', '=', self.name), ('picking_type_id.sequence_code', '=', 'RC')],
            'type': 'ir.actions.act_window',
        }

    # ------------------------------------------------------------
    #   Pickings associated with MO
    # ------------------------------------------------------------
    picking_ids = fields.Many2many(
        'stock.picking',
        compute='_compute_picking_ids',
        string='Picking associated to this manufacturing order',

    )

    # ------------------------------------------------------------
    #   Updates triggered by done pickings
    # ------------------------------------------------------------
    updating_cc_from_picking_ids = fields.Integer(
        string="Latest Done Picking",
        compute='_compute_qty_delivered',
    )

    # ------------------------------------------------------------
    #   Allow bypassing component validation
    # ------------------------------------------------------------
    ignore_component_check = fields.Boolean(
        string="Ignorer la vérification des composants",
        default=False
    )
    # ------------------------------------------------------------
    #   Field Selection for the return components
    # ------------------------------------------------------------
    return_status = fields.Selection([
        ('returned', 'Retourné'),
        ('not_returned', 'Non Retourné'),
        ('return_not_needed', 'Retour Non Nécessaire'),
    ], string="Statut du Retour", default='return_not_needed')

    # ------------------------------------------------------------
    #   NO BACK ORDER FLAG
    # ------------------------------------------------------------

    no_back_order = fields.Boolean(
        string="PAs de reliquat",
        default=False
    )
    has_leftovers = fields.Boolean(
        string="Reste de production",
        compute="compute_has_leftovers", store=True
    )
    show_div_message = fields.Selection([
        ('show', 'show'),
        ('hide', 'hide'),

    ], string="Statut du div", default='hide')

    leftover_lines_info = fields.Text(
        string="Info des restes",
        compute="compute_has_leftovers",
    )

    @api.depends('state', 'move_raw_ids.qty_in_prod')
    def compute_has_leftovers(self):
        for rec in self:
            leftover_lines = self.env['stock.move']  # empty recordset by default

            # ------------------------------
            # CASE 1: DONE + NO BACK ORDER
            # ------------------------------
            # Determine which lines have leftovers based on state
            if rec.state in ('done', 'cancel'):
                if rec.no_back_order:
                    # Only count items not fully consumed
                    leftover_lines = rec.move_raw_ids.filtered(
                        lambda l: l.qty_in_prod > 0 and l.product_uom_qty > l.quantity_done
                    )

                else:
                    # Count all items still in production location
                    leftover_lines = rec.move_raw_ids.filtered(lambda l: l.qty_in_prod > 0)

            # ------------------------------
            # CASE 3: CANCELLED
            # ------------------------------
            elif rec.state == 'cancel' and rec.no_back_order:
                leftover_lines = rec.move_raw_ids.filtered(
                    lambda l: l.qty_in_prod > 0 and l.product_uom_qty > l.quantity_done
                )

            elif rec.state == 'cancel' and not rec.no_back_order:
                leftover_lines = rec.move_raw_ids.filtered(
                    lambda l: l.qty_in_prod > 0
                )

            # ------------------------------
            # CASE 4: OTHER STATES
            # ------------------------------
            else:
                rec.has_leftovers = False
                rec.return_status = 'return_not_needed'
                rec.leftover_lines_info = ""
                rec.show_div_message = 'hide'
                continue  # skip the rest

            # ---------------------------------------------------
            # Build info text only if leftovers were computed
            # ---------------------------------------------------
            rec.has_leftovers = bool(leftover_lines)

            if leftover_lines:
                print("Leftover lines: ", leftover_lines, "Return Status : ", rec.return_status)
                rec.return_status = 'not_returned'



            # If nothing left + nothing previously returned
            if not leftover_lines and not rec.returned_components_count:
                rec.return_status = 'return_not_needed'


            # Build detail text
            info_text = ""
            for line in leftover_lines:
                info_text += f"- {line.product_id.display_name}: {line.qty_in_prod}\n"

            rec.leftover_lines_info = info_text

            # Show warning message if leftovers exist
            rec.show_div_message = 'hide' if leftover_lines else 'show'

    # ------------------------------------------------------------
    #   Quantity returned
    # ------------------------------------------------------------
    qty_returned = fields.Boolean(
        string="Quantity returned",
        compute='compute_update_returned', store=True
    )

    # ------------------------------------------------------------
    #   Quantity Scraped
    # ------------------------------------------------------------
    qty_scraped = fields.Integer(
        string="Update quantity returned",
        compute='_compute_update_scraped'
    )

    # ------------------------------------------------------------
    #   Compute: qty_returned updates
    # ------------------------------------------------------------

    @api.depends('picking_ids', 'picking_ids.state', 'move_raw_ids.qty_in_prod')
    def compute_update_returned(self):
        for rec in self:
            print("=======================_compute_update_returned================================")
            rt_pickings = self.env['stock.picking'].search([
                ('state', '=', 'done'),
                ('picking_type_id.sequence_code', '=', 'RC'),
                ('origin', '=', rec.name),
                ('is_returned_qty_applied', '=', False),
            ], order='id desc', limit=1)

            print("4) RC picking found:", bool(rt_pickings))

            if not rt_pickings:
                print("⚠️ No RC picking found → nothing to apply _compute_update_returned Stops Here ")
                continue
            print("⚠️ RC picking found , _compute_update_returned Stops Here ")

            if rec.no_back_order:
                if any(line.qty_in_prod > 0 for line in
                       rec.move_raw_ids.filtered(lambda l: l.product_uom_qty > l.quantity_done)):
                    for line in rt_pickings.move_line_ids_without_package:
                        for move in rec.move_raw_ids.filtered(lambda l: l.product_uom_qty > l.quantity_done):
                            if move.product_id == line.product_id:
                                print("5) Updating move:", move.product_id.name)

                                prev_qty_in_prod = move.qty_in_prod
                                prev_qty_returned = move.qty_returned

                                move.qty_returned = prev_qty_returned + line.qty_done
                                move.qty_in_prod = max(prev_qty_in_prod - line.qty_done, 0.0)

                                print(f"   qty_in_prod: {prev_qty_in_prod} → {move.qty_in_prod}")
                                print(f"   qty_returned: {prev_qty_returned} → {move.qty_returned}")

                    rt_pickings.is_returned_qty_applied = True
                    quantity_left = rec.move_raw_ids.filtered(
                        lambda l: l.product_uom_qty > l.quantity_done and l.qty_in_prod > 0)
                    if not quantity_left:
                        rec.qty_returned = True
                        rec.return_status = 'returned'
                        if rec.state in ['done', 'cancel']:
                            rec.show_div_message = 'show'
                    else:
                        rec.qty_returned = True
                        rec.return_status = 'not_returned'
                        if rec.state in ['done', 'cancel']:
                            rec.show_div_message = 'hide'


            # ------------------------------------------------------------

            else:
                if any(line.qty_in_prod > 0 for line in rec.move_raw_ids.filtered(lambda l: l.qty_in_prod > 0)):

                    for line in rt_pickings.move_line_ids_without_package:
                        for move in rec.move_raw_ids:
                            if move.product_id == line.product_id:
                                print("5) Updating move:", move.product_id.name)

                                prev_qty_in_prod = move.qty_in_prod
                                prev_qty_returned = move.qty_returned

                                move.qty_returned = prev_qty_returned + line.qty_done
                                move.qty_in_prod = max(prev_qty_in_prod - line.qty_done, 0.0)

                                print(f"   qty_in_prod: {prev_qty_in_prod} → {move.qty_in_prod}")
                                print(f"   qty_returned: {prev_qty_returned} → {move.qty_returned}")
                    rt_pickings.is_returned_qty_applied = True
                    quantity_left = rec.move_raw_ids.filtered(lambda l: l.qty_in_prod > 0)
                    if not quantity_left:
                        rec.qty_returned = True
                        rec.return_status = 'returned'
                        if rec.state in ['done', 'cancel']:
                            rec.show_div_message = 'show'
                    else:
                        rec.qty_returned = True
                        rec.return_status = 'not_returned'
                        if rec.state in ['done', 'cancel']:
                            rec.show_div_message = 'hide'

                # Mark picking applied
                print("6) Marked picking as applied")
                print("--- END COMPUTE UPDATE RETURNED ---\n")
                print("=======================_compute_update_returned================================")

    # ------------------------------------------------------------
    #   Trigger for qty_left updates
    # ------------------------------------------------------------
    qty_left_trigger_update = fields.Integer(
        string="Trigger qty left update",
        compute='_compute_qty_left'
    )

    # ------------------------------------------------------------
    #   Compute: qty_left from latest picking (assigned or done)
    # ------------------------------------------------------------
    @api.depends('picking_ids', 'picking_ids.state')
    def _compute_qty_left(self):
        print("QTY is Called")
        for rec in self:
            if rec.delivery_count > 0:
                rec.qty_left_trigger_update += 1

                done_pickings = rec.picking_ids.filtered(lambda p: p.state == 'done') \
                    .sorted(lambda p: p.scheduled_date, reverse=True)[:1]
                assigned_pickings = rec.picking_ids.filtered(lambda p: p.state == 'assigned')

                print("There's an assigned Picking", assigned_pickings.mapped('origin'))

                # Determine which picking to use
                picking_to_process = assigned_pickings or done_pickings

                if picking_to_process:
                    # Create a dictionary of product quantities from the picking
                    product_qty_dict = {}
                    for line in picking_to_process.move_line_ids_without_package:
                        if line.product_id.id in product_qty_dict:
                            product_qty_dict[line.product_id.id] += line.product_uom_qty
                        else:
                            product_qty_dict[line.product_id.id] = line.product_uom_qty

                    # Update qty_left for all moves
                    for move in rec.move_raw_ids:
                        # If product exists in picking, use that quantity
                        # Otherwise, set to 0 (nothing collected/returned)
                        move.qty_left = product_qty_dict.get(move.product_id.id, 0.0)

                    print(f"Updated qty_left for picking: {picking_to_process.mapped('origin')}")
                else:
                    # No pickings found, reset all quantities
                    rec.move_raw_ids.write({'qty_left': 0.0})
            else:
                rec.qty_left_trigger_update = 0
                # Reset quantities when no deliveries
                rec.move_raw_ids.write({'qty_left': 0.0})

    # ------------------------------------------------------------
    #   Compute qty_delivered from done pickings
    # ------------------------------------------------------------
    @api.depends('picking_ids', 'picking_ids.state', )
    def _compute_qty_delivered(self):
        for rec in self:
            done_pickings = rec.picking_ids.filtered(lambda p: p.state == 'done')

            if done_pickings:
                rec.updating_cc_from_picking_ids += 1

                for move in rec.move_raw_ids:
                    total = sum(
                        line.quantity_done
                        for p in done_pickings
                        for line in p.move_ids_without_package
                        if line.product_id == move.product_id
                    )
                    move.qty_delivered = total

                    if move.qty_consumed_total:
                        move.qty_in_prod = max(
                            move.qty_delivered - move.qty_consumed_total - move.qty_scraped - move.qty_returned, 0.0)
                    else:
                        move.qty_in_prod = max(move.qty_delivered - move.qty_scraped - move.qty_returned, 0.0)

                for picking in done_pickings:
                    print("THIS IS FROM manual collect===================================================")
                    picking.write({'manual_collect': False})
            else:
                rec.updating_cc_from_picking_ids = 0
                rec.move_raw_ids.write({'qty_delivered': 0.0})

    # ------------------------------------------------------------
    #   Compute qty_scraped from scrap_ids
    # ------------------------------------------------------------

    @api.depends('scrap_ids')
    def _compute_update_scraped(self):
        for rec in self:
            if rec.scrap_ids:
                rec.qty_scraped = + len(rec.scrap_ids)
                for scrap in rec.scrap_ids.filtered(lambda s: not s.is_scrap_applied):
                    for line in rec.move_raw_ids:
                        if scrap.product_id == line.product_id:
                            prev_qty_scrap = line.qty_scraped
                            prev_qty_in_prod = line.qty_in_prod
                            line.qty_scraped = prev_qty_scrap + scrap.scrap_qty
                            line.qty_in_prod = prev_qty_in_prod - scrap.scrap_qty

                            scrap.is_scrap_applied = True
            else:
                rec.qty_scraped = 0

    # ------------------------------------------------------------
    #   Validation before closing MO
    # ------------------------------------------------------------
    def button_mark_done(self):
        _logger.info("=== button_mark_done called ===")

        for mrp in self:
            if mrp.ignore_component_check:
                continue

            blocking_msgs = []

            for move in mrp.move_raw_ids:
                product = move.product_id.display_name
                # Needed quantity: always fallback to product UOM if not explicitly set
                needed = float(move.qty_needed or move.product_uom_qty or 0.0)
                current = float(move.qty_in_prod)  # If qty_in_prod is 0, assume full needed quantity

                # Stage 1: No delivered quantity
                if current <= 0.0:
                    blocking_msgs.append(
                        f"❌ {product} : {current:.4f}/{needed:.4f} unités\n"
                        f"   • Aucune collecte effectuée."
                    )
                    continue

                needed_r = round(needed, 4)
                current_r = round(current, 4)

                # Stage 2: Missing quantities
                if needed_r > current_r:
                    missing = max(0.0, needed_r - current_r)
                    blocking_msgs.append(
                        f"❌ {product} : {current_r:.4f}/{needed_r:.4f} unités\n"
                        f"   • Il manque {missing:.4f} unité(s)."
                    )

            if blocking_msgs:
                raise UserError(_("❌ Erreurs de validation :\n\n%s") % "\n\n".join(blocking_msgs))
            res = super(MrpProduction, self).button_mark_done()
            for production in self:
                # Detect if validation is done WITHOUT creating a backorder
                if production.env.context.get('skip_backorder'):
                    production.no_back_order = True
        # This MO is being validated WITHOUT backorder

        return res

    # ------------------------------------------------------------
    #   Post inventory updates
    # ------------------------------------------------------------
    def _post_inventory(self, cancel_backorder=False):
        for mrp in self:
            for line in mrp.move_raw_ids:
                line.qty_in_prod = max(line.qty_delivered - line.qty_needed - line.qty_scraped - line.qty_returned, 0.0)
                prev_qty_consumed_total = line.qty_consumed_total
                line.qty_consumed_total = line.qty_needed + prev_qty_consumed_total

            res = super(MrpProduction, self)._post_inventory(cancel_backorder=cancel_backorder)

            for line in mrp.move_raw_ids:
                _logger.info(
                    f"MRP{mrp.name} and the product name {line.product_id.name} is "
                    f"{line.product_id.display_name} has a qty lef in production of {line.qty_in_prod:.4f} units."
                )
            if mrp.env.context.get('skip_backorder'):
                mrp.no_back_order = True
            return res

        return None

    # ------------------------------------------------------------
    #   Backorder generation handling
    # ------------------------------------------------------------
    def _generate_backorder_productions(self, close_mo=True):
        backorders = super()._generate_backorder_productions(close_mo=close_mo)

        for rec in self:
            _logger.info("=" * 80)
            _logger.info("=== Backorder Generation Triggered ===")
            _logger.info("Original MO: %s (ID: %d)", rec.name, rec.id)

            # Loop through each raw move
            for line in rec.move_raw_ids:

                if line.qty_consumed_total <= 0:
                    original_qty_consumed_total = line.qty_needed
                    original_qty_in_prod = max(
                        line.qty_delivered - line.qty_needed - line.qty_scraped - line.qty_returned, 0.0)

                else:
                    original_qty_consumed_total = line.qty_consumed_total + line.qty_needed
                    original_qty_in_prod = max(
                        line.qty_delivered - line.qty_consumed_total - line.qty_scraped - line.qty_returned, 0.0)

                _logger.info("-" * 60)
                _logger.info(
                    "Product: [%s] %s (ID: %d)",
                    line.product_id.default_code,
                    line.product_id.name,
                    line.product_id.id
                )
                _logger.info(
                    "ORIGINAL VALUES -> qty_in_prod: %.4f | qty_consumed_total: %.4f",
                    original_qty_in_prod,
                    original_qty_consumed_total
                )

                # Assign values to backorders
                for new_order in backorders:
                    for new_line in new_order.move_raw_ids:
                        if line.product_id == new_line.product_id:

                            new_line.qty_consumed_total = original_qty_consumed_total
                            scrapd_return = line.qty_scraped + line.qty_returned
                            if new_line.qty_consumed_total > 0:
                                print("New Line QTy consumed", line.qty_consumed_total)
                                print("Scrap Return", scrapd_return)
                                new_line.qty_in_prod = max(
                                    line.qty_delivered - original_qty_consumed_total - scrapd_return, 0.0)
                                _logger.info(
                                    f"Qty Update | Product: {new_line.product_id.display_name} | Delivered: {line.qty_delivered} | ConsumedTotal: {new_line.qty_consumed_total} | Scrapped: {line.qty_scraped} | Returned: {line.qty_returned} | QtyInProd: {new_line.qty_in_prod}")
                            else:
                                print("Else New Line QTy consumed", line.qty_consumed_total)
                                print("Else qty needed", new_line.qty_needed)
                                print("Scrap Return", scrapd_return)

                                new_line.qty_in_prod = max(line.qty_delivered - line.qty_needed - scrapd_return, 0.0)
                                _logger.info(
                                    f"Qty Update | Product: {new_line.product_id.display_name} | Delivered: {line.qty_delivered} | Needed: {line.qty_needed} | Scrapped: {line.qty_scraped} | Returned: {line.qty_returned} | QtyInProd: {new_line.qty_in_prod}")

                            _logger.info("Backorder MO: %s (ID: %d)", new_order.name, new_order.id)
                            _logger.info(
                                "NEW VALUES -> qty_in_prod: %.4f | qty_consumed_total: %.4f",
                                new_line.qty_in_prod,
                                new_line.qty_consumed_total
                            )

            _logger.info("=" * 80)
            _logger.info("=== End of Backorder Processing for Original MO: %s ===", rec.name)
            _logger.info("=" * 80)

        return backorders

    # ------------------------------------------------------------
    #   Return components logic
    # ------------------------------------------------------------
    def return_components(self):
        self.ensure_one()

        picking_in_progress = self.picking_ids.filtered(lambda p: p.state != 'done')

        if self.state not in ['done', 'cancel']:
            raise UserError(
                _("Vous ne pouvez retourner les composants que lorsque l'Ordre de Fabrication est terminé ou annulé.")
            )

        # ---- Moves to check ----
        if self.state == 'done':
            if self.no_back_order:
                moves_to_check = self.move_raw_ids.filtered(
                    lambda m: m.qty_in_prod > 0 and m.product_id and m.product_uom_qty > m.quantity_done
                )
            else:
                moves_to_check = self.move_raw_ids.filtered(
                    lambda m: m.qty_in_prod > 0 and m.product_id
                )
        else:  # cancel
            moves_to_check = self.move_raw_ids.filtered(
                lambda m: m.qty_in_prod > 0 and m.product_id
            )

        # ===================================================
        # SIMPLE PRINT DEBUG
        # ===================================================
        print("\n===== DEBUG RETURN COMPONENTS =====")
        print("Id:", self.id)
        print("MO:", self.name)
        print("State:", self.state)
        print("no_back_order:", self.no_back_order)
        print("MO returned_components_count:", self.returned_components_count)
        print("Number of moves_to_check:", len(moves_to_check))

        for mv in moves_to_check:
            print(
                " -", mv.product_id.display_name,
                "| qty_in_prod =", mv.qty_in_prod,
                "| qty_uom =", mv.product_uom_qty,
                "| qty_done =", mv.quantity_done
            )

        print("====================================\n")
        # ===================================================

        # ---- Auto return logic ----
        if all(move.qty_in_prod == 0 and move.returned_components_count > 0 for move in moves_to_check):
            self.qty_returned = True
            self.write({'return_status': 'returned', 'show_div_message': 'show'})
            return

        if all(move.qty_in_prod == 0 and move.returned_components_count == 0 for move in moves_to_check):
            self.write({'return_status': 'return_not_needed', 'show_div_message': 'hide'})
            return

        if picking_in_progress:
            raise UserError(
                _("Un transfert est déjà en cours. Veuillez d'abord traiter ce transfert avant de retourner les composants.")
            )
        else:
            return {
                'type': 'ir.actions.act_window',
                'name': _("Retourner les composants"),
                'res_model': 'mrp.return.components.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {'default_production_id': self.id},

            }

    # ------------------------------------------------------------
    #   Collect components Manual
    # ------------------------------------------------------------

    show_manual_collect = fields.Boolean(string="Show Manual Collect", default=True,
                                         compute='_compute_show_manual_collect')

    @api.depends('move_raw_ids', 'move_raw_ids.qty_left', 'delivery_count')
    def _compute_show_manual_collect(self):
        for rec in self:
            # Default value (important to avoid failed assignment)
            # Only compute for these states
            if rec.state in ['confirmed', 'progress', 'to_closer'] and rec.delivery_count > 1:
                # If ANY move has qty_left <= 0 → show the button
                if any(move.qty_left <= 0 for move in rec.move_raw_ids):
                    rec.show_manual_collect = True
                else:
                    rec.show_manual_collect = False

            else:
                rec.show_manual_collect = False

    def action_create_manual_collect(self):
        self.ensure_one()
        picking = self.env['stock.picking']
        picking_in_progress = picking.search([
            ('origin', '=', self.name),
            ('picking_type_id.sequence_code', '=', 'PC'),
            ('manual_collect', '=', True),
            ('state', '!=', 'done')
        ])
        if picking_in_progress:
            raise UserError(_(
                "Un transfert de collecte manuelle est déjà en cours. "
                "Veuillez d'abord traiter ce transfert avant de collecter manuellement les composants. "
            ))

        if any(move.qty_left <= 0 for move in self.move_raw_ids):
            return {
                'type': 'ir.actions.act_window',
                'name': _("Collecte manuelle des composants"),
                'res_model': 'mrp.manual.collect.components.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {'default_production_id': self.id},
            }
        else:
            raise UserError(
                _("Au moins un produit doit avoir toutes ses quantités livrées "
                  "avant de pouvoir effectuer une collecte manuelle des composants.")
            )

# =======================================================================================================================
    ref_product_client_manual = fields.Char(string="Reference Articles étiquette", required=True)

    bom_id = fields.Many2one(
        'mrp.bom', 'Bill of Material',
        readonly=False, states={'draft': [('readonly', False)]},
        domain="""[
        '&',
            '|',
                ('company_id', '=', False),
                ('company_id', '=', company_id),
            '&',
                '|',
                    ('product_id','=',product_id),
                    '&',
                        ('product_tmpl_id.product_variant_ids','=',product_id),
                        ('product_id','=',False),
            ('type', '=', 'normal'),
            ('state', '=', 'done')
        ]""",
        check_company=True,
        help="Bill of Materials allow you to define the list of required components to make a finished product.")

    @api.onchange('product_id', 'picking_type_id', 'company_id')
    def onchange_product_id(self):
        """ Finds UoM of changed product and sets BOM if state is 'done'."""
        _logger.info("onchange_product_id method called")
        if not self.product_id:
            self.bom_id = False
        else:

            picking_type_id = self._context.get('default_picking_type_id')
            picking_type = picking_type_id and self.env['stock.picking.type'].browse(picking_type_id)
            domain = [
                '|',
                    ('company_id', '=', False),
                    ('company_id', '=', self.company_id.id),
                '|',
                    ('product_id', '=', self.product_id.id),
                    '&',
                        ('product_tmpl_id.product_variant_ids', '=', self.product_id.id),
                        ('product_id', '=', False),
                ('type', '=', 'normal'),
                ('state', '=', 'done')
            ]
            _logger.info(f"Domain: {domain}")
            bom = self.env['mrp.bom'].search(domain, limit=1)
            if bom:
                self.bom_id = bom.id
                self.product_qty = bom.product_qty
                self.product_uom_id = bom.product_uom_id.id
            else:
                self.bom_id = False
                self.product_uom_id = self.product_id.uom_id.id

    @api.onchange('product_id', 'picking_type_id', 'company_id')
    def onchange_product_id(self):
        _logger.info("onchange_product_id method called")

        # Always reset BOM when product changes
        self.bom_id = False

