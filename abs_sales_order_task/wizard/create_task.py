
from odoo import api,fields,models,_

class CreateTask(models.TransientModel):
    _name = "sale.create.task"
    
    project_task_id = fields.Many2one('project.project', string='Projet', required=True, help='Ce champ affiche le nom du projet')
    assigned_to_id = fields.Many2one('res.users', string='Assigné à', required=True, help='Affiche le nom du user attribué')
    deadline = fields.Datetime(string='Deadline', required=True, help='Date échéance de la tâche')
   
    # This function is used for create wizard and assign values to specific fields
    def create_task(self):
        store_products = []
        for record in self:
            active_model_id = self.env.context.get('active_id')
            if active_model_id:
                order_obj=self.env['sale.order'].browse(active_model_id)
                order_name=order_obj.name
                customer_name=order_obj.partner_id.id
                confirm_date=order_obj.date_order
                products = order_obj.order_line
                if products:
                    for product_store in products:
                        for products_name in product_store:
                            store_products.append(products_name.product_id.id)
                        project_dictionary = {
                                              'user_id':self.assigned_to_id.id,
                                              'project_id':self.project_task_id.id,
                                              'date_deadline':self.deadline,
                                              'sale_order_id':order_obj.id,
                                              'partner_id':customer_name,
                                              'name':order_name,
                                              'sale_order_date':confirm_date,
                                              'products_task_ids':[(6,0,store_products)]
                                             }
                        if project_dictionary:
                            store_task_id = self.env['project.task'].create(project_dictionary)
                            if store_task_id:
                                order_obj.write({'sale_order_task_field_id': store_task_id.id})
        return True
	            
