# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Extend Tax Report',
    'version': '14.0.1.0.0',
    'category': 'Sales',
    'summary': "Tax Report with detailed lines",
    'description': """Tax Report with detailed lines""",
    'sequence': '10',
    'author': 'Knowledge Bonds Team',
    'license': 'LGPL-3',
    'company': 'Knowledge Bonds',
    'maintainer': 'Knowledge Bonds Team',
    'support': 'info@knowledge-bonds.com',
    'website': 'https://www.knowledge-bonds.com',
    'depends': ['accounting_pdf_reports'],
    'demo': [],
    'data': [
        'reports/tax_report.xml',
    ],
    'installable': True,
    'price': 0,
    'currency': 'USD',
    'application': False,
    'auto_install': False,
    'qweb': [],
}