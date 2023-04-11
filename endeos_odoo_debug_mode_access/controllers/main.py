from odoo import http
from odoo.http import request
import werkzeug
from odoo.addons.web.controllers.main import Home


class HomeDebugMode(Home):

    @http.route('/web', type='http', auth="none")
    def web_client(self, s_action=None, **kw):
        debug = kw.get('debug', False) if 'debug' in kw.keys() else False
        user_id = request.context.get('uid', False)
        if debug or debug == '':
            if user_id:
                user = request.env['res.users'].sudo().browse(user_id)
                if not user.has_group('endeos_odoo_debug_mode_access.endeos_debug_mode_access_group'):
                    return werkzeug.utils.redirect('/web/login?error=access')
        return super().web_client(s_action=s_action, **kw)
