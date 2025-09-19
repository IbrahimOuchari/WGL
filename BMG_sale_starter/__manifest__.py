{
    'name': "BMG_sale_starter",
    'author': 'BMG Tech',
    'category': 'Sale',
    'summary': """Modules BMG Technologies Vente""",
    'license': 'AGPL-3',
    'website': 'www.bmgtech.tn',
    'description': "Modules BMG Technologies Vente",
    'version': '14.0',

    'depends': ['base', 'sale_management', 'sale', 'BMG_contact_starter', ],

    'data': [
        'security/ir.model.access.csv',
        'security/sale_security.xml',
        'report/devis_report.xml',
        'report/devis_template.xml',
        'views/remise.xml',
        'views/details_invoice.xml',
        'views/notification_invoice.xml',
        'views/sale_devis.xml',
        'views/sale_order.xml',
        'views/sale_order_line.xml',
        'views/line_description_view.xml',
        'wizard/fusion_bc.xml',

    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
