# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)
    

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    
    color = fields.Char(
        string='Color',
        store=True
    )
    
    lote = fields.Char(
        string='Lote',
        store=True
    )
       