{
    "name": "Endeos - Grupos y permisos personalizados",

    "summary": """
        Personalizaciones en grupos y permisos de usuario.""",

    "description": """
        Personalizaciones en grupos y permisos de usuario.
    """,
    "license": "Other proprietary",
    "author": "ENDEOS S.L.",
    "website": "https://endeos.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    "category": "Management",
    "version": "15.0.1.2.3",

    # any module necessary for this one to work correctly
    "depends": ["base", "sale", "stock"],

    # always loaded
    "data": [
        "security/custom_groups.xml",
        "views/product_template_form_view.xml",
        "views/menus.xml",
        "data/data.xml",
    ]
}