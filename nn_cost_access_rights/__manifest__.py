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
    'depends': ['base','account', 'purchase', 'product',
                'purchase_last_price_info', 'nn_custom_product_costing',
                'nn_cost_structure','nn_custom_product_costing','nn_reporting'],



    'data': [
        'security/groups.xml',
        'views/mrp_product_template_search_view.xml',
        'views/view_mrp_bom_filter.xml',
        'views/view_mrp_bom_line_filter.xml',
        'views/product_template_views.xml',
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
}
