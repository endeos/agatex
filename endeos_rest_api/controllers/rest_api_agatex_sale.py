from odoo import http, Command
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
            :param (mandatory) | json body | CompanyId:int
            :param (mandatory) | json body | ExternalId:str
            :param (optional) | json body | SourceDocumentNo:str
            :param (mandatory) | json body | ExternalCustomerId:str
            :param (mandatory) | json body | ExternalCustomerNIF:str
            :param (optional) | json body | ExternalCustomerName:str
            :param (mandatory) | json body | FacturaFecha:str in format YYYY-MM-ddThh:mm:ss
            :param (mandatory) | json body | Incoterm:str
            :param (mandatory) | json body | IncotermUbicacion:str
            :param (mandatory) | json body | IncotrastatTransportCode:str
            :param (mandatory) | json body | Albaranes:str
            :param (mandatory) | json body | lineas:list
                                                IsSeparator:bool (mandatory)
                                                IsTextNote:bool (mandatory)
                                                ProductId:str
                                                ProductoCantidad:float (mandatory)
                                                ProductoCantidadEntregada:float (optional)
                                                ProductDescription:str (mandatory)
                                                ProductoUoM:str
                                                ProductoPrecio:float
                                                Descuento:float
                                                Agente:str
                                                AlbaranExternoId:str
                                                AlbaranExternoLinea:str
                                                PedidoExternoId:str
                                                PedidoExternoLinea:str     
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
        
        header = {
            "CompanyId": post_data.get("CompanyId"),
            "ExternalId": post_data.get("ExternalId"),
            "ExternalCustomerId": post_data.get("ExternalCustomerId"),
            "ExternalCustomerNIF": post_data.get("ExternalCustomerNIF"),
            "ExternalCustomerName": post_data.get("ExternalCustomerName"),
            "FacturaFecha": post_data.get("FacturaFecha"),
            "Incoterm": post_data.get("Incoterm"),
            "IncotermUbicacion": post_data.get("IncotermUbicacion"),
            "IncotrastatTransportCode": post_data.get("IncotrastatTransportCode"),
            "Albaranes": post_data.get("Albaranes"),
            "SourceDocumentNo": post_data.get("SourceDocumentNo"),
        }
        lines = post_data.get("lineas")
        new_order = self._create_sale_order(header, lines)

        new_order.action_confirm()
        
        intrastat_country = None
        # existing partner
        partner_model = request.env["res.partner"]
        vat = post_data.get("ExternalCustomerNIF")
        name = post_data.get("ExternalCustomerName")
        company_id = post_data.get("CompanyId")
        domain = ["|", ("vat", "=", vat), ("name", "=", name)]
        partner = search_records(partner_model, domain, limit=1, company=company_id)
        intrastat_code = post_data.get("IncotrastatTransportCode")
        
        if not partner:
            return {"errors": [f"Partner not found with vat {vat} or name {name} in company with id {company_id}"]}
        if partner.country_id.code != "ES":
            intrastat_country = partner.country_id.id
        # buscar metodo transporte
        transport_model = request.env["account.intrastat.code"]
        domain_intrastat = ["&", ("code", "=", intrastat_code), ("type", "=", "transport")]
        intrastat = search_records(transport_model, domain_intrastat, limit=1)
        invoices = new_order._create_invoices(final=True)
        
        product_tmpl_model = request.env["product.template"]
        product_tmpl_aux = False
        for line in lines:
            product_tmpl = False
            if line.get("ProductoId"):
                domain = [("default_code", "=", line.get("ProductoId"))]
                product_tmpl = search_records(product_tmpl_model, domain, limit=1, company=company_id)
                if product_tmpl:
                    product_tmpl_aux = product_tmpl
        if intrastat_country:
            invoices.write({
                "x_sale_incoterm_location": new_order.incoterm_location,
                "x_sale_incotrastat_transport_code": new_order.x_incotrastat_transport_code,
                "intrastat_country_id": intrastat_country,
                "intrastat_transport_mode_id": intrastat.id,
            })
        else:
            invoices.write({
                "x_sale_incoterm_location": new_order.incoterm_location,
                "x_sale_incotrastat_transport_code": new_order.x_incotrastat_transport_code
            })
        
        for line in invoices.invoice_line_ids:
            if product_tmpl_aux:
                line.write({
                    'x_sale_line_merc_code': product_tmpl_aux.intrastat_code_id.code
                })
        invoices.write({
            "x_sale_incoterm_location": new_order.incoterm_location,
            "x_sale_incotrastat_transport_code": new_order.x_incotrastat_transport_code
        })

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
        if not post_data.get("CompanyId") \
        or not post_data.get("ExternalCustomerId") \
        or not post_data.get("ExternalCustomerNIF") \
        or not post_data.get("ExternalCustomerName") \
        or not post_data.get("FacturaFecha") \
        or post_data.get("lineas") is None:
            return {"errors": [f"Missing some required field: CompanyId, ExternalCustomerId, ExternalCustomerNIF, ExternalCustomerName, FacturaFecha, lineas"]}
        
        lines = post_data.get("lineas")
        
        if lines and any(
            not l.get("ProductoDescripcion") or \
            (not l.get("IsSeparator") and not l.get("IsTextNote") and not l.get("ProductoId")) for l in lines):
            return {"errors": [f"Required fields in sale lines: IsSeparator/IsTextNote/ProductoId, ProductoDescripcion"]}
        
        # existing partner
        partner_model = request.env["res.partner"]
        vat = post_data.get("ExternalCustomerNIF")
        name = post_data.get("ExternalCustomerName")
        company_id = post_data.get("CompanyId")
        domain = ["|", ("vat", "=", vat), ("name", "=", name)]
        partner = search_records(partner_model, domain, limit=1, company=company_id)

        if not partner:
            return {"errors": [f"Partner not found with vat {vat} or name {name} in company with id {company_id}"]}

        # existing incoterm
        incoterm_model = request.env["account.incoterms"]
        code = post_data.get("Incoterm")
        domain = []
        incoterm = search_records(incoterm_model, domain).filtered(lambda i: i.code == code)
        
        if code != "":
            if not incoterm:
                return {"errors": [f"Incoterm not found with code {code}"]}

        # existing products
        product_lines = list(filter(lambda l: l.get("ProductoId"), lines))
        product_model = request.env["product.template"]
        product_refs = list(set(map(lambda l: l["ProductoId"], product_lines)))

        product_errors = []
        for r in product_refs:
            domain = [("default_code", "=", r)]
            product = search_records(product_model, domain, limit=1, company=company_id)
            if not product: product_errors.append(f"Product with ref {r} not found")
        if product_errors:
            return {"errors": product_errors}              
        
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
        incoterm_model = request.env["account.incoterms"]
        product_tmpl_model = request.env["product.template"]

        vat = header.get("ExternalCustomerNIF")
        name = header.get("ExternalCustomerName")
        client_ref = header.get("ExternalId")
        company_id = header.get("CompanyId")
        domain = ["|", ("vat", "=", vat), ("name", "=", name)]
        partner = search_records(partner_model, domain, limit=1, company=company_id)

        code = header.get("Incoterm")
        domain = []
        incoterm = search_records(incoterm_model, domain).filtered(lambda i: i.code == code)

        # header info
        data = {
            "partner_id": partner.id,
            "client_order_ref": client_ref,
            # "partner_shipping_id": header.get("partner_shipping_id"),
            # "client_order_ref": header.get("client_order_ref")
            "state": "draft",
            "incoterm": incoterm.id,
            "incoterm_location": header.get("IncotermUbicacion"),
            "origin": header.get('Albaranes'),
            "x_incotrastat_transport_code": header.get("IncotrastatTransportCode"),
            "origin": header.get('SourceDocumentNo'),
        }

        date_format = "%Y-%m-%d %H:%M:%S"
        data["date_order"] = datetime.strptime(header.get("FacturaFecha"), date_format) if header.get("FacturaFecha") else datetime.now()

        data["payment_mode_id"] = (partner.customer_payment_mode_id and partner.customer_payment_mode_id.id) or False
        data["payment_term_id"] = (partner.property_payment_term_id and partner.property_payment_term_id.id) or False
        data["pricelist_id"] = partner.property_product_pricelist and partner.property_product_pricelist.id or False


        # lines info
        if lines:
            line_data = []
            for line in lines:

                product_tmpl = False
                if line.get("ProductoId"):
                    domain = [("default_code", "=", line.get("ProductoId"))]
                    product_tmpl = search_records(product_tmpl_model, domain, limit=1, company=company_id)
                
                tmp_line = {
                    "name": line.get("ProductoDescripcion")
                }
                if product_tmpl:
                    tmp_line["product_template_id"] = product_tmpl.id
                    tmp_line["product_id"] = product_tmpl.product_variant_id.id
                    tmp_line["product_uom_qty"] = line.get("ProductoCantidad")
                
                if line.get("ProductoCantidadEntregada"):
                    tmp_line["qty_delivered"] = line.get("ProductoCantidadEntregada")

                if line.get("IsSeparator"):
                    if tmp_line.get("product_id"): del tmp_line["product_id"]
                    tmp_line["display_type"] = "line_section"
                
                if line.get("IsTextNote"):
                    if tmp_line.get("product_id"): del tmp_line["product_id"]
                    tmp_line["display_type"] = "line_note"
                
                if line.get("ProductoPrecio"):
                    tmp_line["price_unit"] = line.get("ProductoPrecio")
                
                if line.get("Descuento"):
                    tmp_line["discount"] = line.get("Descuento")
                
                agente = False
                if line.get("Agente"):
                    domain = [("vat", "=", line.get("Agente"))]
                    agent_model = request.env["res.partner"]
                    agente = search_records(agent_model, domain, limit=1, company=company_id)
                    if agente:
                        sale_order_line_agent = request.env['sale.order.line.agent'].search([('display_name', '=', agente.display_name)], limit=1)
                        if sale_order_line_agent:
                            tmp_line["agent_ids"] = [(4, sale_order_line_agent.id)]

                line_data.append(Command.create(tmp_line))

            data["order_line"] = line_data 

        new_record = create_record(sale_order_model, data, company=company_id)
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
        
#Recibe json de la API, agrupa datos, llama a validar, y llama a crear orden de comrpa
    @http.route("/api/v1/k/purchase/create", auth="public", type="json", methods=["POST"])
    def k_create_purchase_order(self, **kw):
        """ return sale order name just created
            :param (mandatory) | json body | CompanyId:int esta
            :param (mandatory) | json body | Id:str esta
            :param (mandatory) | json body | ExternalId:str esta
            :param (optional) | json body | SourceDocumentNo:str esta
            :param (mandatory) | json body | ExternalVendorrId:str esta
            :param (mandatory) | json body | ExternalVendorNIF:str esta
            :param (optional) | json body | ExternalVendorName:str esta
            :param (mandatory) | json body | AlbaranFecha:str in format YYYY-MM-ddThh:mm:ss esta
            :param (mandatory) | json body | AlbaranFechaRecepcion:str in format YYYY-MM-ddThh:mm:ss esta
            :param (mandatory) | json body | Albaranes:str esta
                                                IsSeparator:bool (mandatory) esta
                                                IsTextNote:bool (mandatory) esta
                                                ProductId:str esta
                                                ProductDescription:str (mandatory) esta
                                                ProductVariante:str ESTA
                                                Lote:str ESTA
                                                ProductoCantidad:float (mandatory) esta
                                                ProductoCantidadEntregada:float (optional) esta, pero no pilla el valor
                                                ProductoUoM:str esta
                                                ProductoPrecio:float esta
                                                Descuento:float esta
                                                AlbaranExternoId:str No ESTA
                                                AlbaranExternoLinea:str No ESTA
                                                PedidoExternoId:str NO ESTA
                                                PedidoExternoLinea:str NO ESTA
        """
        _logger.info(f"rest_api_agatex_purchase | /api/v1/k/purchase/create | Begin")
        _logger.info(f"rest_api_agatex_purchase | /api/v1/k/purchase/create | Request params: {request.params}")
        _logger.info(f"rest_api_agatex_purchase | /api/v1/k/purchase/create | Request params raw: {request.httprequest.data}")

        token_valid = validate_request_token(request)
        if not token_valid:
            response = prepare_response(errors=[f"Invalid request token"])
            return response
            
        post_data, deserialize_errors = deserialize_request_params_json(request)
        if deserialize_errors and not post_data:
            response = prepare_response(errors=deserialize_errors)
            return response

        validation = self._validate_input__create_purchase_order(post_data)
        if validation.get("errors"):
            response = prepare_response(errors=validation.get("errors"))
            _logger.info(f"rest_api_agatex_purchase | /api/v1/k/purchase/create | END | Errors: {validation.get('errors')}")
            return response
        
        header = {
            "CompanyId": post_data.get("CompanyId"),
            "Id": post_data.get("Id"),
            "ExternalId": post_data.get("ExternalId"),
            "ExternalVendorId": post_data.get("ExternalVendorId"),
            "ExternalVendorNIF": post_data.get("ExternalVendorNIF"),
            "ExternalVendorName": post_data.get("ExternalVendorName"),
            "AlbaranFecha": post_data.get("AlbaranFecha"),
            "AlbaranFechaRecepcion": post_data.get("AlbaranFechaRecepcion"),
            "Albaranes": post_data.get("Albaranes"),
            "SourceDocumentNo": post_data.get("SourceDocumentNo"),
        }
        lines = post_data.get("lineas")
        new_order = self._create_purchase_order(header, lines)

        #new_order.action_confirm()
        #invoices = new_order._create_invoices(final=True)

        response = prepare_response(data=new_order.name)
        _logger.info(f"rest_api_agatex_sale | /api/v1/k/sale/create | END | Response: {response}")
        return response
    
    # funcion que valida la entrada de los datos minimos necesarios para generar la orden de compra
    def _validate_input__create_purchase_order(self, post_data):
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
        if not post_data.get("CompanyId") \
            or not post_data.get("ExternalVendorId") \
            or not post_data.get("ExternalVendorNIF") \
            or not post_data.get("ExternalVendorName") \
            or post_data.get("lineas") is None:
            return {"errors": [f"Missing some required field: CompanyId, ExternalVendorId, ExternalVendorNIF, ExternalVendorName, lineas"]}
        
        lines = post_data.get("lineas")
        
        if lines and any(
            not l.get("ProductoDescripcion") or \
            (not l.get("IsSeparator") and not l.get("IsTextNote") and not l.get("ProductoId")) for l in lines):
            return {"errors": [f"Required fields in sale lines: IsSeparator/IsTextNote/ProductoId, ProductoDescripcion"]}
        
        # existing partner
        partner_model = request.env["res.partner"]
        vat = post_data.get("ExternalVendorNIF")
        name = post_data.get("ExternalVendorName")
        company_id = post_data.get("CompanyId")
        domain = ["|", ("vat", "=", vat), ("name", "=", name)]
        partner = search_records(partner_model, domain, limit=1, company=company_id)

        if not partner:
            return {"errors": [f"Partner not found with vat {vat} or name {name} in company with id {company_id}"]}

        # existing incoterm
        # incoterm_model = request.env["account.incoterms"]
        # code = post_data.get("Incoterm")
        # domain = []
        # incoterm = search_records(incoterm_model, domain).filtered(lambda i: i.code == code)
        
        # if not incoterm:
        #    return {"errors": [f"Incoterm not found with code {code}"]}

        # existing products
        product_lines = list(filter(lambda l: l.get("ProductoId"), lines))
        product_model = request.env["product.template"]
        product_refs = list(set(map(lambda l: l["ProductoId"], product_lines)))

        product_errors = []
        for r in product_refs:
            domain = [("default_code", "=", r)]
            product = search_records(product_model, domain, limit=1, company=company_id)
            if not product: product_errors.append(f"Product with ref {r} not found")
        if product_errors:
            return {"errors": product_errors}              
        
        return {"errors": []}

    #Como dice el nombr, funcion para buscar la unidad de medida
    def find_uom_id(self, uom_name, product_id):
        uom_model = request.env['uom.uom']
        domain = [('name', '=', uom_name)]
        uom = uom_model.sudo().search(domain, limit=1)
        if not uom:
            product_model = request.env['product.product']
            product = product_model.sudo().browse(product_id)
            uom = product.uom_id
        return uom.id if uom else None
    
    # funcion que recive datos, y se encarga de crear la orden de compra
    def _create_purchase_order(self, header, lines):
        purchase_order_model = request.env["purchase.order"]
        partner_model = request.env["res.partner"]
        product_tmpl_model = request.env["product.template"]
    
        vat = header.get("ExternalVendorNIF")
        name = header.get("ExternalVendorName")
        company_id = header.get("CompanyId")
        domain = ["|", ("vat", "=", vat), ("name", "=", name)]
        partner = search_records(partner_model, domain, limit=1, company=company_id)
            
        # header info
        data = {
            "partner_id": partner.id,
            # "partner_shipping_id": header.get("partner_shipping_id"),
            # "client_order_ref": header.get("client_order_ref")
            "state": "purchase",
            "origin": header.get('SourceDocumentNo'),
            "x_n_albaran": header.get('ExternalId')
        }
        _logger.info(f"| END | data: {data}")
        date_format = "%Y-%m-%d %H:%M:%S"
        data["date_order"] = datetime.now()
        data["date_approve"] = datetime.strptime(header.get("AlbaranFecha"), date_format) if header.get("AlbaranFecha") else datetime.now()
        data["date_planned"] = datetime.strptime(header.get("AlbaranFechaRecepcion"), date_format) if header.get("AlbaranFechaRecepcion") else datetime.now()
        # Recoger el valor de ID y usarlo como ref del pedido si viene en la API, sino usar secuencia de Odoo
        if header.get("Id") and header.get("Id") != "":
            data["name"] = header.get("Id") 
        #data["payment_mode_id"] = (partner.customer_payment_mode_id and partner.customer_payment_mode_id.id) or False
        #data["payment_term_id"] = (partner.property_payment_term_id and partner.property_payment_term_id.id) or False
        #data["pricelist_id"] = partner.property_product_pricelist and partner.property_product_pricelist.id or False
    
    
        # lines info
        if lines:
            line_data = []
            for line in lines:
                id_prod = None
                product_tmpl = False
                if line.get("ProductoId"):
                    domain = [("default_code", "=", line.get("ProductoId"))]
                    product_tmpl = search_records(product_tmpl_model, domain, limit=1, company=company_id)
                    id_prod = product_tmpl.product_variant_id.id
                tmp_line = {
                    "name": line.get("ProductoDescripcion")
                }
                if product_tmpl:
                    #tmp_line["product_template_id"] = product_tmpl.id
                    tmp_line["product_id"] = product_tmpl.product_variant_id.id
                    
                #if line.get("ProductoCantidadEntregada"):
                    #tmp_line["qty_delivered"] = line.get("ProductoCantidadEntregada") or False
    
                if line.get("IsSeparator"):
                    if tmp_line.get("product_id"): del tmp_line["product_id"]
                    tmp_line["display_type"] = "line_section"
                    
                if line.get("IsTextNote"):
                    if tmp_line.get("product_id"): del tmp_line["product_id"]
                    tmp_line["display_type"] = "line_note"
                    
                if line.get("ProductoPrecio"):
                    tmp_line["price_unit"] = line.get("ProductoPrecio") or 1.0
                    
                if line.get("Descuento"):
                    tmp_line["discount"] = line.get("Descuento") or False
                    
                if line.get("Lote"):
                    tmp_line["x_lote"] = line.get("Lote") or False
                    
                if line.get("ProductoVariante"):
                    tmp_line["x_color"] = line.get("ProductoVariante") or False
                
                if line.get("ProductoCantidadEntregada"):
                    tmp_line["qty_received"] = line.get("ProductoCantidadEntregada")   
                
                tmp_line["product_qty"] = line.get("ProductoCantidad") or 0.0
                
                #Conseguir uom, comparando con el dato recibido, sino usar el del producto recibido
                uom_name = line.get("ProductoUoM")  
                uom_id = self.find_uom_id(uom_name, id_prod)
                if uom_id:
                    tmp_line["product_uom"] = uom_id
                else:
                    # Manejar el caso en que no se encuentra la UoM
                    _logger.warning(f"No se encontró la UoM para {uom_name}")
    
                line_data.append(Command.create(tmp_line))
                data["order_line"] = line_data 
            
            new_record = create_record(purchase_order_model, data, company=company_id)
            new_record.message_post(body=f"Creado desde API")
            return new_record