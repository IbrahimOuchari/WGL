# -*- coding: utf-8 -*-
##############################################################################
#
#    Jupical Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Jupical Technologies(<http://www.jupical.com>).
#    Author: Jupical Technologies Pvt. Ltd.(<http://www.jupical.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'

    access_partner = fields.Boolean(
        string="Allow Default Access to Partner")
    access_salesperson = fields.Boolean(
        string="Default Access For Sales Person")
    access_salesmanager = fields.Boolean(
        string="Default Access For Sales Manager")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        config = self.env['ir.config_parameter'].sudo()
        res.update(
            access_partner=config.get_param(
                'jt_crm_security.access_partner'),
            access_salesperson=config.get_param(
                'jt_crm_security.access_salesperson'),
            access_salesmanager=config.get_param(
                'jt_crm_security.access_salesmanager'),
        )
        return res

    def give_access_partner(self):
        base_user = self.env.ref('base.group_user', raise_if_not_found=False)
        if self.access_partner:
            base_user.write({'implied_ids': [(4, self.env.ref('jt_crm_security.crm_group_user_all').id)]})
        else:
            base_user.write({'implied_ids': [(3, self.env.ref('jt_crm_security.crm_group_user_all').id)]})

    def give_access_salesperson(self):
        sales_person_group = self.env.ref(
            "sales_team.group_sale_salesman", raise_if_not_found=False)

        if self.access_salesperson:
            sales_person_group.write({'implied_ids': [(4, self.env.ref('jt_crm_security.crm_group_user_all').id)]})
        else:
            sales_person_group.write({'implied_ids': [(3, self.env.ref('jt_crm_security.crm_group_user_all').id)]})

    def give_access_salesmanager(self):
        sales_manager_group = self.env.ref(
            "sales_team.group_sale_manager", raise_if_not_found=False)

        if self.access_salesmanager:
            sales_manager_group.write(
                {'implied_ids': [(4, self.env.ref('jt_crm_security.crm_group_manager').id)]})
        else:
            sales_manager_group.write(
                {'implied_ids': [(3, self.env.ref('jt_crm_security.crm_group_manager').id)]})

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()

        param.set_param('jt_crm_security.access_partner',
                        self.access_partner)
        param.set_param('jt_crm_security.access_salesperson',
                        self.access_salesperson)
        param.set_param('jt_crm_security.access_salesmanager',
                        self.access_salesmanager)

        self.give_access_partner()
        self.give_access_salesperson()
        self.give_access_salesmanager()
