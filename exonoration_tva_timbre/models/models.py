# -*- coding: utf-8 -*-
from datetime import datetime,date
from odoo import models, fields, api, _

class partner_extended(models.Model):
    _inherit = 'res.partner'

    exo_tva = fields.Boolean(string='Exonéré de TVA')
    exo_timbre = fields.Boolean(string='Exonéré du Timbre')
    date_limite_tva = fields.Date(string='Date limite "TVA"')
    date_limite_timbre = fields.Date(string='Date limite "Timbre"')
    num_attest = fields.Char(String='N° Attest')
    vts =fields.Char(String='VTS  SUSP TVA')

class invoice_extended(models.Model):
    _inherit = 'account.move'
    bc = fields.Char(String='N° BC')
    exo_tva = fields.Boolean(string='Exonéré de TVA', related='partner_id.exo_tva')
    exo_timbre = fields.Boolean(string='Exonéré du Timbre', related='partner_id.exo_timbre')
    date_limite_tva = fields.Date(string='date limite "TVA"', related='partner_id.date_limite_tva')
    date_limite_timbre = fields.Date(string='Date limite "Timbre"', related='partner_id.date_limite_timbre')
