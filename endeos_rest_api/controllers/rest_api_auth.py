import odoo
from odoo import http, fields
from odoo.http import request, db_filter
from odoo.exceptions import AccessError
from ..controllers.api_helpers import prepare_response
import logging
import datetime

_logger = logging.getLogger(__name__)

class EndeosRestApiAuth(http.Controller):    
    @http.route("/api/auth", auth="public", type="json", methods=["POST"])
    def api_authenticate(self, **kw):
        """ Based on controller /web/session/authenticate
            return valid session ID
            :param db: database name
            :param login: Odoo username
            :param password: user password
        """
        post_data = request.params
        db_name = post_data.get("db")
        u = post_data.get("login")
        p = post_data.get("password")

        if not db_filter([db_name]):
            raise AccessError("Database not found.")
        
        pre_uid = request.session.authenticate(db_name, u, p)
        if pre_uid != request.session.uid:
            return {"uid": None}
        
        request.session.db = db_name
        registry = odoo.modules.registry.Registry(db_name)
        with registry.cursor() as cr:
            env = odoo.api.Environment(cr, request.session.uid, request.session.context)
            if not request.db and not request.session.is_explicit:
                http.root.session_store.rotate(request.session, env)
                request.future_response.set_cookie(
                    'session_id', request.session.sid,
                    max_age=http.SESSION_LIFETIME, httponly=True
                )
                _logger.warning(f"set cookie session_id: {request.session.sid}")
            # result =  env['ir.http'].session_info()
            
            response = prepare_response(data=["check cookie session_id"])
            return response
    
    @http.route("/api/logout", auth="user", type="json")
    def api_logout(self, **kw):
        """ logout session
        """
        request.session.logout()
        response = prepare_response(data=["Logout complete"])
        return response