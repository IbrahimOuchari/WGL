
from odoo import api, fields, models, _

class CrmLead(models.Model):
    _inherit = "crm.lead"
 
    stage_instructions = fields.Text(string="Consignes d'étape",readonly=True,help="This field shows the instuctions, when click on the status button.")

    #This function will get satge_id and its instruction.
    def write(self,vals):
        for record in self:
            if vals.get('stage_id', False):
                temp = vals['stage_id']
                # Browse temp(Which is stage_id) for stage_instructions(Where the instructions are stored).
                temp = self.env['crm.stage'].browse(temp).stage_instructions
                vals['stage_instructions'] = temp
            return super(CrmLead, self).write(vals)
