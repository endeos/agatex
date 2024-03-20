# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)
    

class CommissionSettleLine(models.Model):
    _inherit = 'commission.settlement.line'
    
commission_ids = fields.Many2many(
    comodel_name="commission",
    string="Commissions",
    copy=True
)