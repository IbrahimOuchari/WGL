
{
    "name": "Groupe Sécurité CRM",
    "summary": "Ajoute un nouveau groupe droit d'accès à CRM",
    "version": "14",
    "category": "Customer Relationship Management",
    "website": "",
    "author": "BMG Tech",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["crm", "sale_crm"],
    # sale_crm dependency is necessary to add groups in some view
    "maintainers": ["victoralmau"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/menu_items.xml",
    ],
}
