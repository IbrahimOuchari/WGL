{
    'name': "NN Sale Discounted Price & Custom Delivery Slip",
    'author': 'BMG Tech',
    'category': 'Sales',
    'sequence': -1,
    'summary': "Manage discounted prices and customize delivery slips.",
    'license': 'AGPL-3',
    'website': 'www.bmgtech.tn',
    'description': """
        Modules BMG Technologies - Sales Enhancement:

        - Display unit prices before and after discount in sales order lines.
        - Customize delivery slips (Bon de Livraison) to display detailed line totals and global totals (HT, TVA, TTC).
        - Allow users to switch between pre-discount and post-discount pricing displays.
    """,
    'version': '14.0',

    'depends': ['base', 'stock', 'sale', 'BMG_sale_starter', 'BMG_stock_starter', 'sale_stock', 'sales_team',
                'purchase_stock'],

    'data': [
        'report/stock_picking_template.xml',
        'security/ir.model.access.csv',  # Security access rules
        'views/sale_order_line_discount.xml',
        'views/stock_picking_form_amount.xml',
        'views/manual_delivery_views.xml'

    ],

    'installable': True,
    'application': True,
    'auto_install': False,
}
