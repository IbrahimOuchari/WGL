
from odoo import models, fields, api


class StockPickingType(models.Model):
    _name = 'stock.picking.type'  # This line is optional when inheriting
    _description = 'Stock Picking Type'  # Optional description

    # Add mail thread and activity mixin
    _inherit = ['stock.picking.type', 'mail.thread', 'mail.activity.mixin']

    # You can add additional fields or methods here if needed
    message_follower_ids = fields.Many2many(
        'res.users', 'mail_followers_rel', 'res_id', 'user_id', string='Followers'
    )
    message_ids = fields.One2many('mail.message', 'res_id', string='Messages')
