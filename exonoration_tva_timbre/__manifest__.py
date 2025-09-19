# -*- coding: utf-8 -*-
{
    'name': "Exonoration TVA Timbre",

    'summary': """
        Exonoration TVA Timbre """,

    'description': """
        Exonoration TVA Timbre """,

    'author': "IDVEY",
    'website': "http://www.idvey.com",
    'images': ['static/description/exono.png'],
    'category': 'tools',
    'version': '0.1',
    'depends': ['base','account'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/partner_exo.xml',
        'views/invoice_exo.xml',

    ],
    'demo': [
        # 'demo/demo.xml',
    ],
    'application': True,
}
