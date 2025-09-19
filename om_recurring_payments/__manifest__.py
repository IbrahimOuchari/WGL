
{
    'name': 'Recurring Payment',
    'author': 'BMG Tech',
    'category': 'Accounting',
    'version': '1.0.0',
    'description': """Odoo 14 Recurring Payment, Recurring Payment In Odoo, Odoo 14 Accounting""",
    'summary': 'Use recurring payments to handle periodically repeated payments',
    'sequence': 11,
    'website': '',
    'depends': ['account'],
    'license': 'LGPL-3',
    'data': [
        'data/sequence.xml',
        'data/recurring_cron.xml',
        'security/ir.model.access.csv',
        'views/recurring_template_view.xml',
        'views/recurring_payment_view.xml'
    ],
    'images': ['static/description/banner.png'],
}
