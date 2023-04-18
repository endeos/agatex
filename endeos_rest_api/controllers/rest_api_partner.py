from odoo import http
from odoo.http import request
from ..controllers.api_helpers import prepare_response, create_record, update_record, delete_record, browse_records, search_records
import logging

_logger = logging.getLogger(__name__)

class EndeosRestApiResPartner(http.Controller):
    def _partner_fields_read(self):
        """ Return list of fields to be read on a res.partner() record
        """
        return ["id","ref","vat","name","email","mobile","phone","street","street2","city","zip","state_id","country_id","comment","company_id","company_type","type","child_ids","parent_id"]
    
    @http.route("/api/v1/contacts", auth="user", type="json", methods=["GET", "POST"])
    def get_contact_list(self, **kw):
        """ Return list of res.partner() dicts
            :param (optional) | json body | rec_ids: list of record ids to get
        """
        domain = []

        post_data = request.params
        if post_data.get("rec_ids"):
            rec_ids = post_data.get("rec_ids", [])
            domain.append(("id", "in", rec_ids))

        partner_model = request.env["res.partner"]
        contacts = search_records(partner_model, domain)
        
        contact_list = []
        for contact in contacts:
            tmp_contact = contact.read(self._partner_fields_read())[0]
            
            contact_list.append(tmp_contact)

        response = prepare_response(data=contact_list)
        return response

    @http.route("/api/v1/contact", auth="user", type="json", methods=["POST"])
    def create_contact(self, **kw):
        """ Return id of new contact created
            :param | json body | contact_data: dict of contact values
        """
        partner_model = request.env["res.partner"]
        post_data = request.params

        contact_data = post_data.get("contact_data", {})
        if not contact_data:
            response = prepare_response(errors=["Contact data not found"])
            return response
        
        new_partner = create_record(partner_model, contact_data)
        
        response = prepare_response(data={"new_contact_id": new_partner.id})
        return response

    @http.route("/api/v1/contact/<int:rec_id>", auth="user", type="json", methods=["GET", "PATCH"])
    def handle_contact(self, rec_id, **kw):
        if request.httprequest.method == "GET":
            """ Return dict of res.partner()
                :param | url | rec_id: record id
            """
            partner_model = request.env["res.partner"]
            partner_id = browse_records(partner_model, rec_id)

            if not partner_id:
                response = prepare_response(errors=[f"Contact with id {rec_id} not found"])
                return response

            tmp_contact = partner_id.read(self._partner_fields_read())

            response = prepare_response(data=tmp_contact[0])
            return response
        
        if request.httprequest.method == "PATCH":
            """ Return boolean after try to update contact
                :param | url | rec_id: id of contact to be updated
                :param | json body | contact_data: dict of contact values to override in record
            """
            partner_model = request.env["res.partner"]
            post_data = request.params
            contact_data = post_data.get("contact_data", {})

            if not contact_data:
                response = prepare_response(errors=["Missing new contact data"])
                return response

            updated = update_record(partner_model, rec_id, contact_data)

            if not updated:
                response = prepare_response(errors=[f"Error updating contact with id {rec_id}"])
                return response
            
            response = prepare_response(data={"updated": updated})
            return response
    
    @http.route("/api/v1/contact/<int:rec_id>", auth="user", type="json", methods=["DELETE"])
    def delete_contact(self, rec_id, **kw):
        """ Return boolean after try to delete contact
            :param | url | rec_id: id of contact to be deleted
        """
        partner_model = request.env["res.partner"]
        deleted = delete_record(partner_model, rec_id)
        
        if not deleted:
            response = prepare_response(errors=[f"Error deleting contact with id {rec_id}"])
            return response
        
        response = prepare_response(data={"deleted": deleted})
        return response