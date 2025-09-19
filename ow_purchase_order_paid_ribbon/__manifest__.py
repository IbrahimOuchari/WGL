
{
    'name': 'Ruban Payé Bon de commande Achat',
    'summary': 'Ajoute le ruban payé dans le BC achat',
    'version': '14',
    'category': 'Purchases',
    'summary': """
Ajoute le ruban payé dans le BC achat
""",
    'author': 'BMG Tech',
    'website': '',
    'license': 'LGPL-3',
    'depends': [
	'purchase',
    ],
    'data': [
        'views/purchase_order_form.xml',
    ],
    'images': ['images/icon.png'],
    'installable': True,
    'application': False,
}
