from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # NN Reporting Marge des Produits Finuax Page
    bom_cost = fields.Float(
        string="Coût de la nomenclature",
        compute="compute_bom_cost",
        readonly=False,
        groups="nn_reporting.group_manager_report_id",

        help="Coût total de la nomenclature sélectionnée.", store=True,
    )
    exploitation_cost = fields.Float(
        string="Coût d’exploitation",
        compute="_compute_exploitation_cost",
        readonly=False,
        store=True,
        groups="nn_reporting.group_manager_report_id",


        help="Calculé comme: (Bom Cost * (100 + % Charge d’exploitation)) / 100."
    )
    standard_price = fields.Float(
        string='Cost',
        compute='compute_standard_price_update',
        # inverse='_set_standard_price',
        # search='_search_standard_price',
        # digits='Product Price',
        groups="nn_reporting.group_manager_report_id",
        help="Cost based on the last purchase order line for this product, "
             "or manually set if needed.", store=True
    )

    list_price = fields.Float(
        'Sales Price', default=1.0,
        digits='Product Price',
        groups="nn_reporting.group_manager_report_id",
        help="Price at which the product is sold to customers.", store=True)

    marge_brute = fields.Float(
        string="Marge Brute",
        compute="_compute_marge_brute",
        groups="nn_reporting.group_manager_report_id",
        store=True
    )

    exploitation_charge_percent = fields.Float(
        string="% Charge d’exploitation",
        help="Pourcentage manuel de charge d’exploitation.",
        groups="nn_reporting.group_manager_report_id", store=True

    )

    total_cost = fields.Float(
        string="Coût de revient total",
        compute="_compute_total_cost",
        readonly=False,
        groups="nn_reporting.group_manager_report_id",
        store=True,
        help="Calculé comme: Bom Cost + Coût d’exploitation."
    )
