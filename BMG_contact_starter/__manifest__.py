{
    'name': "BMG_contact_starter",
    'author': 'BMG Tech',
    'category': 'Contact',
    'summary': """Modules BMG Technologies Contact""",
    'license': 'AGPL-3',
    'website': 'www.bmgtech.tn',
    'description': "Modules BMG Technologies Contact",
    'version': '14.0',

    'depends': ['base', 'account', 'sale_management', 'purchase', 'contacts'],

    'data': [
        'security/ir.model.access.csv',
        'views/identification_contact.xml',
        'views/identification_contact.xml',
        'views/montant_du.xml',
        'views/limit_credit_client_view.xml',
        'wizard/warning_wizard.xml',
        'views/ville_tunisie.xml',

    ],

    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
