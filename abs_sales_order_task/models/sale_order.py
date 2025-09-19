

from odoo import api,fields,models,_

class SaleOrder(models.Model):
    _inherit="sale.order"

    sale_order_task_field_id = fields.Many2one('project.task',string='Tâche de B.C.', help='Ce champ affiche le nom de la tâche')
