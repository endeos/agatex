from odoo import http
from odoo.http import request
from datetime import datetime
from ..controllers.api_helpers import prepare_response, create_record, update_record, delete_record, browse_records, search_records, deserialize_request_params_json, validate_request_token
import logging

_logger = logging.getLogger(__name__)

class EndeosRestApiResPartner(http.Controller):

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
                                                product_template_id:int
                                                product_uom_qty:int
                                                description (optional)
                                                price_unit:float (optional)
                                                discount:float (optional)
        """
        _logger.info(f"rest_api_agatex_sale | /api/v1/k/sale/create | Begin")
        _logger.info(f"rest_api_agatex_sale | /api/v1/k/sale/create | Request params: {request.params}")
        _logger.info(f"rest_api_agatex_sale | /api/v1/k/sale/create | Request params raw: {request.httprequest.data}")

        token_valid = validate_request_token(request)
        if not token_valid:
            response = prepare_response(errors=[f"Invalid request token"])
            return response
            
        post_data, deserialize_errors = deserialize_request_params_json(request)
        if deserialize_errors and not post_data:
            response = prepare_response(errors=deserialize_errors)
            return response

        validation = self._validate_input__create_sale_order(post_data)
        if validation.get("errors"):
            response = prepare_response(errors=validation.get("errors"))
            _logger.info(f"rest_api_agatex_sale | /api/v1/k/sale/create | END | Errors: {validation.get('errors')}")
            return response
        
        new_order = self._create_sale_order(post_data.get("sale_order_header"), post_data.get("sale_order_lines"))
        # TODO pending info about intrastat codes
        # TODO add logic to process picking validation
        # TODO add logic to validate invoice

        response = prepare_response(data=new_order.name)
        _logger.info(f"rest_api_agatex_sale | /api/v1/k/sale/create | END | Response: {response}")
        return response
    

    @http.route("/api/v1/k/sale/invoice/create", auth="public", type="json", methods=["POST"])
    def k_create_sale_invoice(self, **kw):
        """ return sale invoice name just created
            :param (mandatory) | json body | CompanyId:int
            :param (mandatory) | json body | ExternalCustomerId:str
            :param (mandatory) | json body | ExternalCustomerNIF:str
            :param (optional) | json body | ExternalCustomerName:str
            :param (mandatory) | json body | FacturaFecha:str in format YYYY-MM-ddThh:mm:ss
            :param (mandatory) | json body | lineas:list
                                                IsSeparator:bool (mandatory)
                                                ExternalOrderId:str
                                                ProductId:str
                                                ProductDescription:str (mandatory)
                                                ProductUnitOfMeasure:str
                                                ProductQuantity:float (mandatory)
                                                ProductUnitPrice:float (mandatory)
                                                DiscountPercent:float
                                                ExternalAgentCode1:str
                                                ExternalAgentCommisionPercent1:float
                                                ExternalAgentCode2:str
                                                ExternalAgentCommisionPercent2:float
        """
        _logger.info(f"rest_api_agatex_sale | /api/v1/k/sale/invoice/create | Begin")
        _logger.info(f"rest_api_agatex_sale | /api/v1/k/sale/invoice/create | Request params: {request.params}")
        _logger.info(f"rest_api_agatex_sale | /api/v1/k/sale/invoice/create | Request params raw: {request.httprequest.data}")

        token_valid = validate_request_token(request)
        if not token_valid:
            response = prepare_response(errors=[f"Invalid request token"])
            return response

        post_data, deserialize_errors = deserialize_request_params_json(request)
        if deserialize_errors and not post_data:
            response = prepare_response(errors=deserialize_errors)
            return response

        validation = self._validate_input__create_sale_invoice(post_data)
        if validation.get("errors"):
            response = prepare_response(errors=validation.get("errors"))
            _logger.info(f"rest_api_agatex_sale | /api/v1/k/sale/invoice/create | END | Errors: {validation.get('errors')}")
            return response

        new_invoice = self._create_sale_invoice(post_data)
        response = prepare_response(data=new_invoice.name)
        _logger.info(f"rest_api_agatex_sale | /api/v1/k/sale/invoice/create | END | Response: {response}")
        return response


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
            not l.get("product_template_id") or \
            not l.get("product_uom_qty") for l in lines):
            return {"errors": [f"Required fields in sale_order_lines: product_template_id, product_uom_qty"]}
        
        # existing entities
        partner_model = request.env["res.partner"]
        partner = browse_records(partner_model, header.get("partner_id"))
        if not partner:
            return {"errors": [f"Partner with id {header.get('partner_id')} not found"]}

        product_ids = list(map(lambda l: l.get("product_template_id"), lines))
        product_tmpl_model = request.env["product.template"]
        all_products = search_records(product_tmpl_model, domain=[], company=header.get("company_id"))
        if len(all_products.ids) < len(product_ids):
            return {"errors": [f"Check given product ids given in lines, some of them may not exist in Odoo in company with id {header.get('company_id')}"]}
        
        # shipping address belongs to partner
        if partner.id != header.get("partner_shipping_id"):
            if header.get("partner_shipping_id") not in partner.child_ids.ids:
                return {"errors": [f"Given shipping address does not belong to partner {partner.name}"]}                
        
        return {"errors": []}
    
    def _validate_input__create_sale_invoice(self, post_data):
        """ return validation object
            {
                "errors": []
            }
            Checks:
            - mandatory fields not empty
            - partner exist
            - products in line exist
        """

        # required fields
        if post_data.get("CompanyId") is None \
            or post_data.get("ExternalCustomerId") is None \
            or post_data.get("ExternalCustomerNIF") is None \
            or post_data.get("FacturaFecha") is None \
            or post_data.get("lineas") is None:
            
            return {"errors": [f"Missing some required field: CompanyId, ExternalCustomerId, ExternalCustomerNIF, FacturaFecha, lineas"]}

        
        # required fields in lines
        lines = post_data.get("lineas")
        company_id = post_data.get("CompanyId")
        if any(l.get("IsSeparator") is None \
                or l.get("ProductId") is None \
                or l.get("ProductDescription") is None \
                or l.get("ProductQuantity") is None \
                or l.get("ProductUnitPrice") is None for l in lines):
            return {"errors": [f"Missing some required field in invoice lines: IsSeparator, ProductId, ProductDescription, ProductQuantity, ProductUnitPrice"]}
        
        # check products exist
        product_model = request.env["product.template"]
        product_names = [line.get("ProductId") for line in list(filter(lambda l: l.get("ProductId") and not l.get("IsSeparator"), lines))]

        product_names = list(set(product_names)) # remove duplicates
        product_errors = []
        for n in product_names:
            domain = [("name", "=", n)]
            product = search_records(product_model, domain, limit=1, company=company_id)
            if not product: product_errors.append(f"Product {n} not found")
        if product_errors:
            return {"errors": product_errors}

        
        # check partner exist
        partner_model = request.env["res.partner"]
        vat = post_data.get("ExternalCustomerNIF")
        name = post_data.get("ExternalCustomerName")
        domain = ["|", ("vat", "=", vat), ("name", "=", name)]
        partner = search_records(partner_model, domain, limit=1, company=company_id)
        if not partner:
            return {"errors": [f"Partner not found with vat {vat} or name {name} in company with id {company_id}"]}
        
        
        return {"errors": []}


    def _create_sale_order(self, header, lines):
        sale_order_model = request.env["sale.order"]
        partner_model = request.env["res.partner"]
        product_tmpl_model = request.env["product.template"]
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
                product_tmpl = browse_records(product_tmpl_model, line.get("product_template_id"))

                tmp_line = (0, 0, {
                    "product_template_id": product_tmpl.id,
                    "product_id": product_tmpl.product_variant_id.id,
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

    def _create_sale_invoice(self, post_data):
        invoice_model = request.env["account.move"]
        partner_model = request.env["res.partner"]
        product_tmpl_model = request.env["product.template"]
        
        vat = post_data.get("ExternalCustomerNIF")
        name = post_data.get("ExternalCustomerName")
        company_id = post_data.get("CompanyId")
        domain = ["|", ("vat", "=", vat), ("name", "=", name)]
        partner = search_records(partner_model, domain, limit=1, company=company_id)

        # header info
        data = {
            "partner_id": partner.id,
            "move_type": "out_invoice",
            "ref": post_data.get("ExternalCustomerId", False)
        }

        date_format = "%Y-%m-%dT%H:%M:%S"
        data["invoice_date"] = datetime.strptime(post_data.get("FacturaFecha"), date_format)

        # lines info
        line_data = []
        for line in post_data.get("lineas"):
            if line.get("IsSeparator", False):
                tmp_line = (0, 0, {
                    "display_type": "line_section",
                    "name": line.get("ProductDescription")
                })
                line_data.append((tmp_line))
                continue

            domain = [("name", "=", line.get("ProductId"))]
            product_tmpl = search_records(product_tmpl_model, domain, limit=1, company=post_data.get("CompanyId"))

            tmp_line = (0, 0, {
                "product_id": product_tmpl.product_variant_id.id,
                "quantity": line.get("ProductQuantity"),
                "name": line.get("ProductDescription"),
                "price_unit": line.get("ProductUnitPrice"),
                "discount": line.get("DiscountPercent")
            })     

            line_data.append(tmp_line)

        data["invoice_line_ids"] = line_data

        new_record = create_record(invoice_model, data, company=company_id)
        new_record.message_post(body=f"Creado desde API")
        
        try:
            new_record.action_post()
        except:
            _logger.error(f"_create_sale_invoice | move {new_record.id} could not been posted")
        
        return new_record
        