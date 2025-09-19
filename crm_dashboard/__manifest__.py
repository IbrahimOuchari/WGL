{
    'name': "Tableau de bord CRM",
    'description': """Tableau de bord CRM, vue détaillée du tableau de bord pour CRM, CRM, tableau de bord""",
    'summary': """Tableau de bord CRM""",
    'category': 'Sales',
    'version': '14',
    'author': 'BMG Tech',
    'company': '',
    'maintainer': '',
    'website': "",
    'depends': ['base', 'sale_management', 'crm'],
    'data': [
        'views/dashboard_view.xml',
        'views/assets.xml',
    ],
    'qweb': [
        'static/src/xml/dashboard_view.xml',
        'static/src/xml/sub_dashboard.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
