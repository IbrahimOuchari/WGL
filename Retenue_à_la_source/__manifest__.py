# -*- coding: utf-8 -*-
{
    'name': "Retenue à la Source",
    'summary': """
         Retenue à la Source""",
    'description': """
         Retenue à la Source
    """,
    'author': "BMG Tech",
    'category': 'Accounting',
    'version': '14',
    'depends': ['base', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'data/account_withholding_sequence.xml',
        'views/ics_withholding_tax_views.xml',
        'views/withholding_tax_view.xml',
        'views/journal_custom_form.xml',
        'views/account_move_view.xml',
        'reports/report_invoice.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
