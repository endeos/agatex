from odoo import http
from odoo.http import request
from ..controllers.api_helpers import prepare_response
import logging
import ast

_logger = logging.getLogger(__name__)

XML_RPC_METHODS = ["search", "search_count", "fields_get", "read", "search_read", "create", "write", "unlink"]

class EndeosRestApiXmlRpc(http.Controller):
    """ The purpose of this controller is to map the XML RPC default functionality with REST endpoint
        documentation: https://www.odoo.com/documentation/15.0/es/developer/reference/external_api.html
    """
    
    @http.route("/api/v1/rpc_call", auth="user", type="json", methods=["POST"])
    def user_rpc_call(self, **kw):
        return self.map_xml_rpc_api_call()
    
    @http.route("/api/v1/public_rpc_call", auth="public", type="json", methods=["POST"])
    def public_rpc_call(self, **kw):
        env = request.env
        post_data = request.params
        api_key = post_data.get("api_key")
        ResUsersApiKeys = env["res.users.apikeys"]

        valid_request = self.validate_request_token(ResUsersApiKeys, api_key)
        if valid_request:
            return self.map_xml_rpc_api_call()
        
        response = prepare_response(errors=["Invalid request token"])
        return response
    
    def validate_request_token(self, ResUsersApiKeys, api_key):        
        user_id = ResUsersApiKeys._check_credentials(scope="rpc", key=api_key)

        if not user_id:
            return False
        
        request.update_env(user=user_id)
        return True
    
    def map_xml_rpc_api_call(self):
        env = request.env
        post_data = request.params

        # Method mapped in XML RPC API
        # Possible values in XML_RPC_METHODS constant
        rpc_method = post_data.get("rpc_method")
        if rpc_method not in XML_RPC_METHODS:
            response = prepare_response(errors=[f"Invalid rpc_method: '{rpc_method}'"])
            return response
        
        model_name = post_data.get("model")
        if not model_name:
            response = prepare_response(errors=["Missing model param"])
        
        if rpc_method == "search":
            response = self.handle_rpc_search(env, model_name, post_data)
        if rpc_method == "search_count":
            response = self.handle_rpc_search(env, model_name, post_data, only_count=True)
        if rpc_method == "fields_get":
            response = self.handle_rpc_fields_get(env, model_name)
        if rpc_method == "read":
            response = self.handle_rpc_read(env, model_name, post_data)
        if rpc_method == "search_read":
            response = self.handle_rpc_search(env, model_name, post_data, read_fields=True)
        if rpc_method == "create":
            response = self.handle_rpc_create(env, model_name, post_data)
        if rpc_method == "write":
            response = self.handle_rpc_write(env, model_name, post_data)
        if rpc_method == "unlink":
            response = self.handle_rpc_unlink(env, model_name, post_data)
        
        return response
        


    def handle_rpc_search(self, env, model_name, post_data, only_count=False, read_fields=False):
        """ Return list of record ids or total records number matching some domain
        """
        model = env[model_name]

        lang = post_data.get("lang")
        if lang:
            model = model.with_context(lang=lang)

        domain = ast.literal_eval(post_data.get("domain", "[]"))
        limit = post_data.get("limit")
        offset = post_data.get("offset", 0)

        recordset = model.search(domain, limit=limit, offset=offset)

        if only_count:
            response = prepare_response(data=len(recordset))
            return response
        
        if read_fields:
            fields = post_data.get("fields", ["id", "name"])
            result = recordset.read(fields)

            response = prepare_response(data=result)
            return response

        response = prepare_response(data=recordset.ids)
        return response

    def handle_rpc_fields_get(self, env, model_name):
        """ Returns a list of fields of interest of a given model
        """
        model = env[model_name]
        fields = model.fields_get(attributes=["string", "help", "type"])
        response = prepare_response(data=fields)
        return response
        
    
    def handle_rpc_read(self, env, model_name, post_data):
        """ Returns data of records especified by their ids
        """
        rec_ids = post_data.get("rec_ids", [])
        fields = post_data.get("fields", ["id", "name"])

        model = env[model_name]

        lang = post_data.get("lang")
        if lang:
            model = model.with_context(lang=lang)

        recordset = model.browse(rec_ids).exists()
        result = recordset.read(fields)

        response = prepare_response(data=result)
        return response

    def handle_rpc_create(self, env, model_name, post_data):
        """ Creates a record and returns its id
        """
        model = env[model_name]
        record_data = post_data.get("record_data")

        if not record_data:
            response = prepare_response(errors=[f"Missing data in 'record_data' for new record on '{model}' model"])
            return response
        
        new_record = model.create(record_data)
        response = prepare_response(data={"new_record_id": new_record.id})
        return response

    def handle_rpc_write(self, env, model_name, post_data):
        """ Creates a record and returns its id
        """
        model = env[model_name]
        rec_ids = post_data.get("rec_ids")
        record_data = post_data.get("record_data")

        if not rec_ids:
            response = prepare_response(errors=[f"Missing record ids in 'rec_ids'"])
            return response
        
        if not record_data:
            response = prepare_response(errors=[f"Missing data in 'record_data' for update records on '{model}' model"])
            return response
        
        recordset = model.browse(rec_ids).exists()
        recordset.write(record_data)
        response = prepare_response(data={"updated": True})
        return response

    def handle_rpc_unlink(self, env, model_name, post_data):
        """ Deletes records from the database
        """
        model = env[model_name]
        rec_ids = post_data.get("rec_ids")

        if not rec_ids:
            response = prepare_response(errors=[f"Missing record ids in'rec_ids'"])
            return response

        recordset = model.browse(rec_ids).exists()
        recordset.unlink()

        response = prepare_response(data={"deleted": True})
        return response
        
