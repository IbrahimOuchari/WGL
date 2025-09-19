
{
    'name': "Instruction Etape CRM",
    'author': 'BMG Tech',
    'category': 'CRM',
    'summary': """Donner des instructions d'une étape particulière dans CRM""",
    'license': 'AGPL-3',
    'website': '',
    'description': """Donner des instructions d'une étape particulière dans CRM""",
    'version': '14',
    'depends': ['base','project','crm'],
    'data': ['views/crm_lead_view.xml','views/crm_stage_view.xml'],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
