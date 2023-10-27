# -*- coding: utf-8 -*-
{
    'name': "Endeos - Columnas impuestos en listado facturas",

    'summary': """
        Módulo que añade columnas de IVA e IRPF en los listados de facturas.
        """,

    'description': """
        Módulo que añade columnas de IVA e IRPF en los listados de facturas.
    """,
    "license": "Other proprietary",
    'author': "ENDEOS S.L.",
    'website': "https://endeos.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Account',
    'version': '16.0.1.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        'views/views.xml',
    ],
}
