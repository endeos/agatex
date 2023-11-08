# -*- coding: utf-8 -*-
{
    'name': "Endeos - Account customizations",

    'summary': """
        Personalización de la aplicación de Contabilidad""",

    'description': """
        Personalización de la aplicación de Contabilidad
    """,

    # Categories https://github.com/odoo/odoo/blob/master/odoo/addons/base/data/ir_module_category_data.xml
    'category': 'Accounting',
    'version': '1.1.0',
    'author': "ENDEOS S.L.",
    'website': "https://www.endeos.com",
    'license': 'Other proprietary',

    'depends': ['base', 'account'],

    'data': [
        'views/templates.xml',
    ],
}