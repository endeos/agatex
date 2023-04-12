# -*- coding: utf-8 -*-
# Email: sales@creyox.com
{
    'name': "Login User Detail Report",
    'version': '15.0',
    'summary': """It helps to know user login detail and you can also print the report for the selected user.""",
    'author': "Creyox Technologies",
    'depends': ['base'],
    'license': 'LGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'views/user_report.xml',
        'views/login_user_report_template.xml',
        'views/login_user_report_wizard.xml',
    ],
    'demo': [],
    'images': ['static/description/banner.gif'],
    'installable': True,
    'auto_install': False,
}
