# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)
    

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order'
    
    x_n_albaran = fields.Char(
        string='Nº Albaran',
        store=True
    )
    
    
class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    
    x_color = fields.Char(
        string='Color',
        store=True
    )
    
    x_lote = fields.Char(
        string='Lote',
        store=True
    )
       