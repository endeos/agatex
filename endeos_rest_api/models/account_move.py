from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = "account.move"

    x_sale_incoterm_location = fields.Char(string="Ubicación del Incoterm", help="Valor recogido de la venta si se ha creado a través de la API")
    x_sale_incotrastat_transport_code = fields.Char(string="Código Transporte Incotrastat", help="Valor recogido de la venta si se ha creado a través de la API")
    
class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    x_sale_line_merc_code = fields.Char(
        string="Código de mercancia", 
        help="Valor recogido del producto asociado si se ha creado a través de la API")