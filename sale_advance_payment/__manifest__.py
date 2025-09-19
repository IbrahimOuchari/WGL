{
    "name": "Paiement Client BC",
    "version": "14",
    "author": "BMG Tech",
    "website": "",
    "category": "Sales",
    "license": "AGPL-3",
    "summary": "Autoriser le paiement client depuis le bon de commande de vente",
    "depends": ["sale"],
    "data": [
        "wizard/sale_advance_payment_wzd_view.xml",
        "views/sale_view.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
}
