{
    'name': 'Gestion des Comptes Bancaires',
    'version': '14.0.1.0.0',
    'summary': 'Module pour gérer les comptes bancaires et les lier aux factures',
    'description': """
        Ce module permet de :
        - Créer un modèle de compte bancaire avec Agence, RIB, IBAN et Code BIC.
        - Lier un compte bancaire destinataire à une facture client.
        - Afficher les informations du compte dans le PDF de la facture.
    """,
    'author': 'Neonara',
    'website': 'https://neonara.digital',
    'category': 'Accounting',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'views/bank_account_view.xml',
        'views/account_move_view.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
