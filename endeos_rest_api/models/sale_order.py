from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = "sale.order"

    x_incotrastat_transport_code = fields.Char(string="Código Transporte Intrastat")
    