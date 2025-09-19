
{
    "name": "Raison d'Annulation BC Achat",
    "version": "14",
    "author": "BMG Tech",
    "category": "Purchase",
    "license": "AGPL-3",
    "complexity": "normal",
    "website": "",
    "depends": ["purchase"],
    "data": [
        "wizard/purchase_cancel_reason_view.xml",
        "views/purchase_order.xml",
        "security/ir.model.access.csv",
        "data/purchase_order_cancel_reason.xml",
    ],
    "auto_install": False,
    "installable": True,
}
