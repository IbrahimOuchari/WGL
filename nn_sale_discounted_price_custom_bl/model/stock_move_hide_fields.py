from odoo import fields,models, api

class StockMoveHid(models.Model):
    _inherit ="stock.picking"


    sequence_code = fields.Char(related='picking_type_id.sequence_code', readonly=True)
