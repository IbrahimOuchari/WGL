{
    'name': 'Custom Product Costing',
    'version': '1.0',
    'sequence':-3,
    'summary': 'Gestion avancée et analyse des coûts des produits',
    'description': """
        Ce module permet d'améliorer la gestion et l'analyse de la structure des coûts des produits. 
        Principales fonctionnalités :
        - Calcul automatisé du coût de revient basé sur les nomenclatures (BOM).
        - Gestion des coûts fixes, variables et d'exploitation.
        - Intégration de la gestion des étiquettes dans la production.
        - Analyse détaillée des marges dans les devis et commandes.
        """,
    'author': 'Votre Société',
    'website': 'https://www.votresite.com',
    'category': 'Productivity',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'account',
        'purchase',
        'product',
        'purchase_last_price_info',
        'mrp',
        'BMG_sale_starter',
        'sale_management',
    ],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'data/label_management_sequence.xml',
        'report/mrp_production_print_etiquette.xml',
        'report/product_template_xlsx_report_button.xml',
        'views/mrp_bom_standard_price.xml',
        'views/product_product_custom_cost.xml',
        'views/product_template_custom_cost.xml',
        'views/sale_order_analysis_tree.xml',
        'views/sale_order_margin.xml',
        'views/mrp_production_label_management.xml',
        'views/product_template_view.xml',
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
}
