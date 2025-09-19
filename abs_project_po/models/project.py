
from odoo import api, fields, models,_

class Project(models.Model):
    _inherit = 'project.project'

    purchase_order_ids = fields.One2many('purchase.order','project_id',string="Bon de Commande")
