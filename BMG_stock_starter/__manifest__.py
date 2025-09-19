{
    'name': "BMG_stock_starter",
    'author': 'BMG Tech',
    'category': '',
    'summary': """""",
    'license': 'AGPL-3',
    'website': 'www.bmgtech.tn',
    'description': "Modules BMG Technologies Stock",
    'version': '14.0',

    'depends': ['base', 'stock', "delivery", "sale_stock", "sales_team", 'purchase_stock', 'BMG_sale_starter'],

    'data': [
        'wizard/create_manual_stock_picking.xml',
        'wizard/manual_delivery.xml',
        'security/ir.model.access.csv',
        'views/status_bc_livraison_view.xml',
        'views/stock_non_reserve_view.xml',
        'views/stock_no_negative_view.xml',
        'views/stock_location_lockdown_view.xml',
        'views/livraison_manuelle_view.xml',
        'views/picking_draft_view.xml',
        'views/qty_dispo_vente.xml',
        'views/livraison_manuelle_achat_view.xml',
        'views/stock_picking_view.xml',

    ],

    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
