# -*- coding: utf-8 -*-
{
    "name": "NN Product Pricing",
    "version": "14.0.1.0.0",
    "summary": "Add discounted price and update margin for products",
    "description": """
        This module adds two fields to product.template:
        - taux_remise (discount rate)
        - prix_apres_remise (price after discount)
        It also overrides the marge_brute computation to use the discounted price.
        Fields are visible only if sale_ok = True and user belongs to group_manager_report_id.
    """,
    "category": "Sales",
    "author": "Your Name",
    "website": "http://yourcompany.com",
    "depends": ["product", "sale", "nn_reporting", "nn_sales_management_extension", "nn_cost_access_rights"],
    "data": [
        "views/product_template.xml",  # For XML field placement
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "license": "LGPL-3",
}
