from odoo import http
from odoo.http import request
from datetime import datetime
from ..controllers.api_helpers import prepare_response, create_record, update_record, delete_record, browse_records, search_records, deserialize_request_params_json
import logging

_logger = logging.getLogger(__name__)

class EndeosRestApiResPartner(http.Controller):
    def _partner_fields_read(self):
        """ Return list of fields to be read on a res.partner() record
        """
        return ["id"]
    


    def _validate_input__create_sale_order(self, post_data):
        """ return validation object
            {
                "errors": []
            }
            Checks:
            - mandatory fields not empty
            - partner exist
            - shipping id same as/child of partner
        """
        # required fields
        if not post_data.get("sale_order_header") or post_data.get("sale_order_lines") is None:
            return {"errors": [f"Required fields: sale_order_header, sale_order_line"]}
        
        header = post_data.get("sale_order_header")
        lines = post_data.get("sale_order_lines")

        if not header.get("company_id") or \
           not header.get("partner_id") or \
           not header.get("partner_shipping_id"):
           return {"errors": [f"Required fields in sale_order_header: company_id, partner_id, partner_shipping_id"]}
        
        if lines and any(
            not l.get("product_tmpl_id") or \
            not l.get("product_uom_qty") for l in lines):
            return {"errors": [f"Required fields in sale_order_lines: product_tmpl_id, product_uom_qty"]}
        
        # existing entities
        partner_model = request.env["res.partner"]
        partner = browse_records(partner_model, header.get("partner_id"))
        if not partner:
            return {"errors": [f"Partner with id {header.get('partner_id')} not found"]}

        product_ids = list(map(lambda l: l.get("product_tmpl_id"), lines))
        product_tmpl_model = request.env["product.template"]
        all_products = search_records(product_tmpl_model, domain=[], company=header.get("company_id"))
        if len(all_products.ids) < len(product_ids):
            return {"errors": [f"Check given product ids given in lines, some of them may not exist in Odoo in company with id {header.get('company_id')}"]}
        
        # shipping address belongs to partner
        if partner.id != header.get("partner_shipping_id"):
            if header.get("partner_shipping_id") not in partner.child_ids.ids:
                return {"errors": [f"Given shipping address does not belong to partner {partner.name}"]}                
        
        return {"errors": []}


    def _create_sale_order(self, header, lines):
        sale_order_model = request.env["sale.order"]
        partner_model = request.env["res.partner"]
        partner = browse_records(partner_model, header.get("partner_id"))

        # header info
        data = {
            "partner_id": partner.id,
            "partner_shipping_id": header.get("partner_shipping_id"),
            "client_order_ref": header.get("client_order_ref")
        }

        data["state"] = "sale" if header.get("validate_picking") == True or header.get("validate_picking") == True else "draft"

        date_format = "%Y-%m-%d %H:%M:%S"
        data["date_order"] = datetime.strptime(header.get("date_order"), date_format) if header.get("date_order") else datetime.now()

        data["payment_mode_id"] = header.get("payment_mode_id") or (partner.customer_payment_mode_id and partner.customer_payment_mode_id.id) or False
        data["payment_term_id"] = header.get("payment_term_id") or (partner.property_payment_term_id and partner.property_payment_term_id.id) or False
        data["pricelist_id"] = partner.property_product_pricelist and partner.property_product_pricelist.id or False

        # lines info
        if lines:
            line_data = []
            for line in lines:
                tmp_line = (0, 0, {
                    "product_tmpl_id": line.get("product_tmpl_id"),
                    "product_uom_qty": line.get("product_uom_qty")
                })
                
                if line.get("description"):
                    tmp_line[2]["name"] = line.get("description")
                
                if line.get("price_unit"):
                    tmp_line[2]["price_unit"] = line.get("price_unit")
                
                if line.get("discount"):
                    tmp_line[2]["discount"] = line.get("discount")          

                line_data.append(tmp_line)

            data["order_line"] = line_data

        new_record = create_record(sale_order_model, data, company=header.get("company_id"))
        new_record.message_post(body=f"Creado desde API")
        return new_record




    """ /k/ in route means that an api key is expected """
    @http.route("/api/v1/k/sale/create", auth="public", type="json", methods=["POST"])
    def k_create_sale_order(self, **kw):
        """ return sale order name just created
            :param (mandatory) | json body | sale_order_header:dict
                                                company_id:int
                                                partner_id:int
                                                partner_shipping_id:int
                                                date_order:char format YYYY-mm-dd HH:MM:SS (optional default now)
                                                payment_mode_id:int (optional default customers's mode or 'TRANSFERENCIA')
                                                payment_term_id:int (optional default customers's term or 'CONTADO')
                                                client_order_ref:char (optional)
                                                validate_picking:bool (optional default False)
                                                validate_invoice:bool (optional default False)
                                                agent_id:int (optional)


            :param (mandatory) | json body | sale_order_lines:list(dict)
                                                product_tmpl_id:int
                                                product_uom_qty:int
                                                description (optional)
                                                price_unit:float (optional)
                                                discount:float (optional)
        """
        _logger.info(f"rest_api_agatex_sale | k_create_sale_order | Begin")
        _logger.info(f"rest_api_agatex_sale | k_create_sale_order | Request params: {request.params}")
        _logger.info(f"rest_api_agatex_sale | k_create_sale_order | Request params raw: {request.httprequest.data}")

        post_data, deserialize_errors = deserialize_request_params_json(request)
        if deserialize_errors and not post_data:
            response = prepare_response(errors=deserialize_errors)
            return response

        validation = self._validate_input__k_create_sale_order(post_data)
        if validation.get("errors"):
            response = prepare_response(errors=validation.get("errors"))
            _logger.info(f"rest_api_agatex_sale | k_create_sale_order | END | Errors: {validation.get('errors')}")
            return response
        
        new_order = self._create_sale_order(post_data.get("sale_order_header"), post_data.get("sale_order_lines"))
        # TODO check if it works via API and document
        # TODO pending info about intrastat codes

        response = prepare_response(data=new_order.name)
        _logger.info(f"rest_api_agatex_sale | k_create_sale_order | END | Response: {response}")
        return response

    