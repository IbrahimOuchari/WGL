from odoo import models, fields, _, api
from odoo.exceptions import ValidationError


class MrpBomCustomState(models.Model):
    _inherit = 'mrp.bom'
    _order = 'create_date desc'
    # Adding a custom state field with French labels
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('confirm', 'Confirmé'),
        ('waiting_for_validation', 'En Attente de Validation'),  # New state added

        ('rejected', 'Rejeté'),
        ('done', 'Validé'),
    ], string='État', default='draft', required=True)

    bom_cancel = fields.Boolean(
        string="Raison d'invalidation",
        help="Indiquer la raison de l'invalidation"
    )

    invalidation_reason = fields.Text(string="Raison d'invalidation",
                                      help="Indiquer la raison de l'invalidation")
    date_validation = fields.Datetime(string="Date de Validation")


    def confirm_bom(self):
        for record in self:
            record.state = 'confirm'
            record.message_post(
                body=_("✅ Nomenclature confirmée par %s") % self.env.user.name
            )

    def action_demand_validation_request(self):
        for record in self:
            record.state = 'waiting_for_validation'
            record.date_validation = fields.Datetime.now()

            group = self.env.ref(
                'nn_mrp_bom_custom_states.nomenclature_validation_group',
                raise_if_not_found=False
            )
            template = self.env.ref(
                'nn_mrp_bom_custom_states.nomenclature_validation_template',
                raise_if_not_found=False
            )

            if not group or not group.users:
                record.message_post(
                    body="⚠️ Aucun utilisateur trouvé dans le groupe de validation de nomenclature."
                )
                continue
            if not template:
                record.message_post(
                    body="⚠️ Le template d'email pour la validation de nomenclature est introuvable."
                )
                continue

            # Collect all recipient emails
            recipients = group.users.filtered(lambda u: u.email)
            if recipients:
                email_list = [f"{u.name} ({u.email})" for u in recipients]

                # Send emails in one go using bcc
                template.sudo().with_context(
                    email_to=", ".join(u.email for u in recipients),  # all emails in one field
                    mail_post_autofollow=False,
                    mail_notify_force_send=True
                ).send_mail(record.id, force_send=True)

                # Post a single summary message in chatter
                record.message_post(
                    body="📧 Emails envoyés à :\n- " + "\n- ".join(email_list) +
                         f"\n\nNomenclature mise en attente de validation par {self.env.user.name}"
                )

    def accept_bom(self):
        for record in self:
            record.state = 'done'
            record.bom_cancel = False
            record.message_post(
                body=_("✅ Nomenclature acceptée par %s") % self.env.user.name
            )

    def reject_bom(self):
        for record in self:
            record.state = 'rejected'
        # No state change here, just opening a wizard

    def set_state_draft(self):
        for record in self:
            record.state = 'draft'

    @api.onchange('routing_id')
    def create_one2many_record(self):
        if self.routing_id:
            # ✅ Clear existing one2many lines first
            self.operation_ids = [(5, 0, 0)]

            # ✅ Then add new lines from the selected routing
            self.operation_ids = [(0, 0, {
                'routing_id': line.routing_id.id,
                'name': line.name,
                'workcenter_id': line.workcenter_id.id,
                'time_cycle': line.time_cycle,
                'time_cycle_manual': line.time_cycle_manual,
            }) for line in self.routing_id.gamme_id]
