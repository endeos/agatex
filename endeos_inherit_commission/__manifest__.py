# -*- coding: utf-8 -*-
{
    'name': "Endeos - inherit commissions",

    'summary': """
        Módulo que permite seleccionar comisiones para el agente
        """,

    'description': """
        Permitir seleccionar comisiones para el agente
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
    'depends': ['base', 'commission.settlement.line'],

    # always loaded
    'data': [
        'views/views.xml',
    ],
}
