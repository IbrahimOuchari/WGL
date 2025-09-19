# -*- coding: utf-8 -*-
{
    'name': "payment_modality",

    'summary': """
  Generation des Cheques pour le paiment a terme """,

    'description': """
        Sous le menu paiment ( client et fournisseur ), selon le nombre des mois selectionné pour le paiment on va cree l'enregistrement des cheque necessaires
    """,

    'author': 'BMG Tech',
    'category': 'payment',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
}
