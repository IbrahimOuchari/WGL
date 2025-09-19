{
    'name': "Tableau de bord Vente",

    'summary': """
            Tableau de bord Vente""",

    'description': """ Tableau de bord Vente """,

    'author': 'BMG Tech',
    'website': "",
    'license': 'AGPL-3',
    'category': 'Sales',
    'version': '14',
    'images': ['static/description/icon.png'],
    'installable': True,
    'auto_install': False,
    "depends": ['sale_management'],
    "data": [
        'views/sale_dashboard_assets.xml',
        'views/sale_order.xml',
    ],
    'qweb': [
        'static/src/xml/sale_dashboard.xml',
    ],
}
