# -*- coding: utf-8 -*-
{
    'name': "L10n_timbre",

    'summary': """
        Timbre fiscal""",

    'description': """
        L10n_timbre
    """,

    'author': "IDVEY",
    'website': "http://www.idvey.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        'data/timbre_data.xml',
        'views/views.xml',
        'views/report_invoice.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'installable': True,

}
