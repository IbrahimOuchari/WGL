
{
    "name": "Mode de Paiement",
    "version": "14",
    "development_status": "Production/Stable",
    "license": "AGPL-3",
    "author": "BMG Tech",
    "website": "",
    "category": "Banking addons",
    "depends": ["account"],
    "data": [
        "security/account_payment_mode.xml",
        "security/ir.model.access.csv",
        "views/account_payment_method.xml",
        "views/account_payment_mode.xml",
        "views/account_journal.xml",
    ],
    "demo": ["demo/payment_demo.xml"],
    "installable": True,
}
