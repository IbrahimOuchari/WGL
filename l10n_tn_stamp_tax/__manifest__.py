# Copyright Netformica - Mohamed Machta
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': "Timbre Fiscal Tunisie",
    'version': '14',
    'author': 'BMG Tech',
    'category': 'Localisation',
    "license": "LGPL-3",
    'depends': ['base', 'account'],
    'application': False,
    'data': [
        'views/invoice.xml',
        'views/account_tax_view.xml',
    ],
    'images': [
        'static/description/icon.png',
    ],
}
