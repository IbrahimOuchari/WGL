
{
    'name': "Créer Tâche sur Bon de Commande",
    'author': 'BMG Tech',
    'category': 'Sales',
    'summary': """Créer une tâche et la liée à un projet depuis le bon de commande vente""",
    'website': '',
    'license': 'AGPL-3',
    'description': """Créer une tâche et la liée à un projet depuis le bon de commande vente""",
    'version': '14',
    'depends': ['base','project','sale_management'],
    'data': ['security/ir.model.access.csv','wizard/create_task.xml','views/project_task_view.xml','views/sale_order_add_button_view.xml'
           ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
