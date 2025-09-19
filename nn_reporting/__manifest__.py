{
    'name': "NeoNara ",
    'author': 'NeoNara',
    'category': '',
    'summary': """""",
    'license': 'AGPL-3',
    'website': 'www.neonara.digital',
    'description': "Module NeonNara ",
    'version': '17.0',

    'depends': ['base', 'mrp', 'nn_custom_product_costing', 'BMG_sale_starter', 'access_apps',
                'nn_sales_management_extension', ],

    'data': [
        'security/groups.xml',
        'views/bom_line_cost.xml',
        'views/cost_price_bom_product.xml',
        'views/product_sale.xml',
        'views/menu.xml',
    ],

    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
