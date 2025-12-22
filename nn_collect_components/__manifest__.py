# -*- coding: utf-8 -*-
{
    "name": "nn_collect_components_mrp",
    "summary": "NeoNara - Collect and reserve components for Production Orders",
    "description": """
NeoNara - Collect Components for MRP
------------------------------------
This module adds a new operation in the Manufacturing (MRP) workflow to:
- Reserve components specifically for a selected Production Order (OF)
- Generate a “collect components” action
- Prepare stock moves and ensure correct quantity handling
- Improve material availability tracking
    """,
    "author": "NeoNara",
    "website": "https://www.neonara.com",
    "category": "Manufacturing",
    "version": "14.0.1.0.0",
    "license": "LGPL-3",

    "depends": [
        "mrp",
        "stock",
        "base",
        "web",
        "nn_reporting"
    ],

    "data": [
        # security
        # security
        "security/groups.xml",
        "security/ir.model.access.csv",

        # views
        "views/mrp_production_form_view.xml",
        "views/mrp_production_bom_id.xml",
        "views/mrp_bom_states.xml",
        "views/mrp_bom_tree_view.xml",
        "views/mrp_destruction_bom_id.xml",
        "views/stock_picking_form_view.xml",
        "wizards/return_components_form.xml",
        "wizards/manual_collect_components_form.xml",
    ],

    "installable": True,
    "application": False,
}
