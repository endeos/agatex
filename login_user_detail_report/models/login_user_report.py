# -*- coding: utf-8 -*-
# Email: sales@creyox.com

from odoo import fields, models, api, _


class LoginUserReport(models.Model):
    _name = 'login.user.report'

    start_date = fields.Datetime(required=True, default=fields.Date.today().strftime('%Y-%m-%d 00:00:00'))
    end_date = fields.Datetime(required=True, default=fields.Date.today().strftime('%Y-%m-%d 23:59:59'))
    type = fields.Selection([('all', 'All Users'), ('selected', 'Selected User')], default='all', required=True)
    user_id = fields.Many2many('res.users')

    def gathering_user_details(self):
        user = self.env['res.users'].search([])
        users = []
        login_users = []
        for rec in user:
            users.append(rec.name)
        if self.type == 'all':
            records = self.env['login.detail'].search([('name', 'in', users), ('date_time', '>=', self.start_date),
                                                       ('date_time', '<=', self.end_date)])
            for obj in records:
                data = {
                    'name': obj.name,
                    'date_time': obj.date_time,
                    'ip_address': obj.ip_address,
                    'socket_name': obj.socket_name,
                    # 'sys_name': obj.sys_name,
                }
                login_users.append(data)
            return login_users
        else:
            for rec in self.user_id:
                records = self.env['login.detail'].search([('name', '=', rec.name),
                    ('date_time', '>=', self.start_date), ('date_time', '<=', self.end_date)])
                for obj in records:
                    data = {
                        'name': obj.name,
                        'date_time': obj.date_time,
                        'ip_address': obj.ip_address,
                        'socket_name': obj.socket_name,
                        # 'sys_name': obj.sys_name,
                    }
                    login_users.append(data)
                return login_users

    def generate_report(self):
        return self.env.ref('login_user_detail_report.report_login_user').report_action([], )

