# -*- coding: utf-8 -*-
{
    "name": "Endeos - API REST",

    "summary": """
        Módulo para acceder a Odoo vía REST API.
        """,

    "description": """
        Módulo para acceder a Odoo vía REST API.
    """,
    "license": "Other proprietary",
    "author": "ENDEOS S.L.",
    "website": "https://endeos.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    "category": "Services/Project",
    "version": "16.0.1.0.6",

    # any module necessary for this one to work correctly
    "depends": ["sale", "purchase", "stock"],

    # always loaded
    "data": [],
}
