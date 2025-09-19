{
    'name': 'Structure des Coûts',
    'version': '1.0',
    'summary': 'Gestion et analyse de la structure des coûts',
    'description': """
        Ce module permet de gérer efficacement la structure des coûts
        en fournissant des outils d’analyse des coûts fixes, variables,
        et indirects pour une meilleure rentabilité.
    """,
    'author': 'Votre Société',
    'website': 'https://www.votresite.com',
    'category': 'Accounting',
    'license': 'LGPL-3',
    'depends': ['account', 'purchase', 'product', 'purchase_last_price_info', 'nn_custom_product_costing'],
    'data': [
        # 'views/cost_structure_views.xml',
        # 'views/product_template_views_inherit.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
        'demo/cost_structure_demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
