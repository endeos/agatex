from odoo import http, fields
from odoo.http import request, db_monodb
from ..controllers.api_helpers import prepare_response
import logging
import datetime

_logger = logging.getLogger(__name__)

class EndeosRestApiAuth(http.Controller):    
    @http.route("/api/auth", auth="public", type="json", methods=["POST"])
    def api_authenticate(self, **kw):
        """ return valid session ID
            :param db: database name
            :param login: Odoo username
            :param password: user password
        """
        post_data = request.params

        db_name = post_data.get("db", db_monodb())
        request.session.authenticate(db_name, post_data.get("login"), post_data.get("password"))
        result = request.env["ir.http"].session_info()

        request.session.rotate = False
        expiration = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        result["session"] = {
            "session_id": request.session.sid,
            "expires_at": fields.Datetime.to_string(expiration),
        }

        response = prepare_response(data={"session_id": result.get('session')})
        return response
    
    @http.route("/api/logout", auth="user", type="json", methods=["GET"])
    def api_logout(self, **kw):
        """ logout session
        """
        request.session.logout(keep_db=True)
        response = prepare_response(data=["Logout complete"])
        return response