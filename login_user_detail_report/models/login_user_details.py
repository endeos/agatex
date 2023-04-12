# -*- coding: utf-8 -*-
# Email: sales@creyox.com

import logging, socket, platform
from itertools import chain
from odoo.http import request
from odoo import models, fields, api
import getpass


_logger = logging.getLogger(__name__)
USER_PRIVATE_FIELDS = ['password']
concat = chain.from_iterable


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def _check_credentials(self, password, user_agent_env):
        result = super(ResUsers, self)._check_credentials(password, user_agent_env)
        ip_address = request.httprequest.environ['REMOTE_ADDR']
        vals = {'name': self.name,
                'ip_address': ip_address,
                'socket_name': socket.gethostname(),
                # 'sys_name': platform.uname().system
                }
        self.env['login.detail'].sudo().create(vals)
        return result


class LoginDetail(models.Model):
    _name = 'login.detail'

    name = fields.Char(string="User Name")
    date_time = fields.Datetime(string="Login Date", default=lambda self: fields.datetime.now())
    ip_address = fields.Char(string="IP Address")
    socket_name = fields.Char(string="Host Name")
    # sys_name = fields.Char(string="OS")
