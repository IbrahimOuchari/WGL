
{
    'name'        : 'Bon de commande Achat sur projet',
    'author'      : 'BMG Tech',
    'category'    : 'Purchases',
    'summary'     : 'Afficher le bon de commande achat dans le projet',
    'website'     : '',
    'description' : """ Afficher le bon de commande achat dans le projet """,
    'version'     : '14',
    'depends'     : ['base','purchase','project'],
    'data'        : [
                    'views/purchase_order_view.xml',
                    'views/project_view.xml',
                    ],
    'images': ['static/description/banner.png'],
    'license'     : 'AGPL-3',    
    'installable' : True,
    'auto_install': False,
    'application' : True,
}
