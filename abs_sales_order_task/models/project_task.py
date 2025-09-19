

from odoo import api,fields,models,_

class ProjectTask(models.Model):
    _inherit="project.task"
    _description = "Project Task"

    sale_order_id = fields.Many2one('sale.order', string='BC Origine', readonly=True, help='This field displays customer name')
    sale_order_date = fields.Date(string='Date Commande',help='Ce champ affiche la date de confirmation de la commande')
    products_task_ids = fields.Many2many('product.product','product_id',string='Produit',help='Ce champ affiche les produits de la commande spécifique')
