
from odoo import api, fields, models, _

class CrmStage(models.Model):
    _inherit = "crm.stage"

    stage_instructions = fields.Text(string="Stage Instructions",help="This field shows the instuctions, when you click on the status button.")
