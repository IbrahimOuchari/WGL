from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)


class AccountMoveInstance(models.Model):
    _inherit = 'account.move'

    amount_paid = fields.Monetary(
        string='Montant Payé',
        compute='_compute_amount_paid',
        store=True,
        help="Montant total déjà payé pour cette facture"
    )
    notification_ids = fields.One2many(
        'account.notification',
        'move_id',
        string="Notifications"
    )

    payment_en_instance = fields.Integer(
        string='Nombre de Paiements Échelonnés',
        store=True,
        compute='_compute_total_unpaid_amount_fixed',
        help="Nombre de paiements échelonnés non effectués"
    )


    credit = fields.Monetary(
        string='Crédit',
        compute='_compute_credit',
        store=True,
        help="Montant Dû - Paiements Échelonnés"
    )

    @api.depends('amount_total', 'amount_residual')
    def _compute_amount_paid(self):
        for move in self:
            move.amount_paid = move.amount_total - move.amount_residual




    def action_recompute_payment(self):
        for record in self:
            # Log if the function is being triggered
            _logger.info(f"Triggered _compute_total_unpaid_amount_fixed for Account Move ID: {record.id}")
            # Fetch unpaid notifications and calculate the total amount
            unpaid_notifications = record.notification_bill.filtered(lambda line: line.paid is False)
            # Log how many lines are unpaid and their amounts
            _logger.info(f"Account Move ID: {record.id} - Found {len(unpaid_notifications)} unpaid notification lines")
            # Log the unpaid amounts
            if unpaid_notifications:
                unpaid_amounts = unpaid_notifications.mapped('amount')
                _logger.info(f"Unpaid amounts for Account Move ID {record.id}: {unpaid_amounts}")
            # Update the payment_en_instance fi
            # eld with the sum of unpaid amounts
            record.payment_en_instance = sum(unpaid_notifications.mapped('amount')) if unpaid_notifications else 0.0
            # Log the final computed value
            _logger.info(f"Account Move ID: {record.id} - Computed payment_en_instance: {record.payment_en_instance}")


    @api.depends('notification_bill.paid', 'notification_bill.amount')
    def _compute_total_unpaid_amount_fixed(self):
        for record in self:
            # Log if the function is being triggered
            _logger.info(f"Triggered _compute_total_unpaid_amount_fixed for Account Move ID: {record.id}")
            # Fetch unpaid notifications and calculate the total amount
            unpaid_notifications = record.notification_bill.filtered(lambda line: line.paid is False)
            # Log how many lines are unpaid and their amounts
            _logger.info(f"Account Move ID: {record.id} - Found {len(unpaid_notifications)} unpaid notification lines")
            # Log the unpaid amounts
            if unpaid_notifications:
                unpaid_amounts = unpaid_notifications.mapped('amount')
                _logger.info(f"Unpaid amounts for Account Move ID {record.id}: {unpaid_amounts}")
            # Update the payment_en_instance fi
            # eld with the sum of unpaid amounts
            record.payment_en_instance = sum(unpaid_notifications.mapped('amount')) if unpaid_notifications else 0.0
            # Log the final computed value
            _logger.info(f"Account Move ID: {record.id} - Computed payment_en_instance: {record.payment_en_instance}")


    @api.depends('amount_residual', 'payment_en_instance')
    def _compute_credit(self):
        for move in self:
            move.credit = move.amount_residual - move.payment_en_instance

class AccountNotification(models.Model):
    _inherit = "account.notification"
    _description = "Notification de comptabilité"

    move_id = fields.Many2one(
        'account.move',  # Modèle cible
        string="Facture/Écriture",
        ondelete="cascade"
    )
