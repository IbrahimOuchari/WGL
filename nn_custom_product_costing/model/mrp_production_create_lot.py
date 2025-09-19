from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

import logging

# Configure logging
_logger = logging.getLogger(__name__)


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    date_prevue_fin_prod = fields.Date(string="Date Prévue Fin Prod", required=True)
    quantity_per_batch = fields.Float(string='Quantité par Lot', digits=(16, 0))  # Ensure this field exists

    quality_control_checked = fields.Boolean(
        string="Contrôle Qualité Vérifié",
        default=False,  # Default value set to False
        store=True  # Store the field value to persist it in the database
    )
    # Rename "Durée Attendue" to "Durée Théorique" and control editability
    duration_expected = fields.Float(
        string='Durée Théorique',
        readonly=True,  # Field is read-only by default
        states={'draft': [('readonly', True)]}  # Editable only in 'draft' state
    )

    label_management_ids = fields.One2many(
        'label.management',
        'manufacturing_order_id',
        string="Label Management",
        readonly=True
    )

    quantity_per_batch = fields.Float(string="Colisage", required=True, digits=(16, 0))

    @api.constrains('quantity_per_batch')
    def _check_quantity_per_batch(self):
        """ Ensure that the quantity per batch is not zero """
        for record in self:
            if record.quantity_per_batch == 0.0:
                raise ValidationError(
                    "La quantité par colisage ne peut pas être égale à zéro. Veuillez entrer une valeur valide.")

    is_readonly_lot = fields.Boolean(string="Readonly Lot", default=True)

    def unblock_lot(self):
        # Toggle the readonly status
        for record in self:
            record.is_readonly_lot = not record.is_readonly_lot

            # # You can also change the state of related label_management_ids here if needed
            # for label in record.label_management_ids:
            #     label.is_readonly_lot = not label.is_readonly_lot

    def block_lot(self):
        # Toggle the readonly status
        for record in self:
            record.is_readonly_lot = not record.is_readonly_lot
            # # You can also change the state of related label_management_ids here if needed
            # for label in record.label_management_ids:
            #     label.is_readonly_lot = not label.is_readonly_lot

    def print_label_management_report(self):
        """Fetch related label management records and print the report."""
        label_records = self.env['label.management'].search([
            ('manufacturing_order_id', '=', self.id)
        ])
        if label_records:
            return self.env.ref('nn_z2s.action_label_management_report').report_action(label_records)
        else:
            raise ValueError("No Label Management records found for this Manufacturing Order.")

    def action_create_lots(self):
        """
        Create lots for the manufacturing order based on the `qty_producing` value.
        """
        for order in self:
            qty_producing = order.qty_producing
            quantity_per_batch = order.quantity_per_batch
            # state = order.state
            # if state != 'draft':
            #     raise UserError("L'Ordre de Fabrication (OF) doit être au moins à l'état brouillon.")

            if qty_producing <= 0:
                raise UserError("La quantité à produire doit être supérieure à zéro.")

            if quantity_per_batch <= 0:
                raise UserError("La quantité colisage doit être supérieure à zéro.")
            if quantity_per_batch > qty_producing:
                raise UserError("La quantité clisage ne peut pas être supérieure à la quantité à produire.")

            self.env['label.management'].action_create_lots(order, qty_producing)

    return_count = fields.Integer(string="Retour des Composants", compute="_compute_return_count")

    @api.depends('name')
    def _compute_return_count(self):
        for production in self:
            production.return_count = self.env['stock.picking'].search_count([
                ('origin', '=', production.name),
                ('picking_type_id.sequence_code', '=', 'RT'),
                ('state', '!=', 'done')  # Exclude 'done' return operations
            ])

    @api.depends('name')
    def _compute_control_quality_done(self):
        for production in self:
            # Count the number of related control quality records that are in 'done' or 'in_progress' state
            control_count = self.env['control.quality'].search_count([
                ('of_id', '=', production.name),
                ('state', 'in', ['done', 'in_progress'])  # Include both 'done' and 'in_progress' states
            ])

            # Update the control_quality_done field
            production.control_quality_done = control_count

            # Update the quality_control_checked based on the count
            production.quality_control_checked = control_count > 0  # Set to True if count is greater than 0

    def action_return_components(self):
        for production in self:
            return {
                'name': 'Return Components Wizard',
                'type': 'ir.actions.act_window',
                'res_model': 'return.components.wizard',
                'view_mode': 'form',
                'view_id': self.env.ref('nn_Z2S.view_return_components_wizard_form').id,
                'target': 'new',
                'context': {'default_mrp_production_id': production.id}
            }

    def action_view_return_operations(self):
        self.ensure_one()
        return {
            'name': 'Retour des Composants',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            'domain': [('origin', '=', self.name), ('picking_type_id.sequence_code', '=', 'RT'),
                       ('state', '!=', 'done')],
            'type': 'ir.actions.act_window',
        }

    @api.onchange('return_count')
    def _onchange_return_count(self):
        """Trigger the return components wizard with updated return_count when it changes."""
        if self.return_count:
            # Trigger the wizard with the updated return_count
            return {
                'name': 'Return Components Wizard',
                'type': 'ir.actions.act_window',
                'res_model': 'return.components.wizard',
                'view_mode': 'form',
                'view_id': self.env.ref('nn_Z2S.view_return_components_wizard_form').id,
                'target': 'new',
                'context': {
                    'default_mrp_production_id': self.id,  # Pass the current production id
                    'default_return_count': self.return_count  # Pass the updated return count
                }
            }

#
