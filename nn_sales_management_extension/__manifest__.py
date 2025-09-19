{
    'name': 'Extension Gestion des Ventes',
    'version': '1.0',
    'category': 'Ventes',
    'author': 'Votre Entreprise',
    'depends': ['sale_management', 'stock', 'account','report_xlsx', 'purchase','BMG_sale_starter','nn_sale_discounted_price_custom_bl',
                'nn_custom_product_costing'],
    'data': [
        'security/groups.xml',
        'views/stock_picking_type_views.xml',
        'views/sale_order_line_tree_view.xml',
        'views/product_tree_view.xml',
        'views/sale_order_form_view.xml',
        'views/account_notification_tree_view.xml',
        'views/account_move_tree_view.xml',
        'views/stock_evluation_tree_view.xml',
        'views/stock_evluation_tree_view.xml',
        'reports/sale_order_line_report_xlsx.xml',

    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'sequence': 10,
    'description': """
        Ce module étend la gestion des ventes avec des champs personnalisés, 
        des rapports et des processus pour un meilleur contrôle des ventes, des stocks et de la comptabilité.
        - Champs personnalisés pour les commandes de vente, les produits et les paiements
        - Prévision de la trésorerie et rapports mensuels
        - Statut de facturation et livraison imposé pour certains rôles
        - Alertes personnalisées pour la Marge Brute
    """,
}
