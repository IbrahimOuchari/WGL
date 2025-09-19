
{
    'name': "To Do",
    'summary': """
        Créer une liste de tâches à l'aide d'activités""",
    'description': """
        Créer une liste de tâches à l'aide d'activités""",
    'author': 'BMG Tech',
    'category': 'Tools',
    'version': '14',
    'depends': ['base', 'mail'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/recurring.xml',
        'data/general.xml',
        'views/views.xml',
    ],
    'license': 'LGPL-3',
    'images': ['static/description/icon.png'],
    'installable': True,
    'auto_install': False,
    'application': True,
    'web_icon': ['static/description/icone.png'],
}
