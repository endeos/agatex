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
    
class SaleOrderLineAgent(models.Model):
    _inherit = "sale.order.line.agent"

    @api.depends(
        "commission_id",
        "commission_ids",
        "object_id.price_subtotal",
        "object_id.product_id",
        "object_id.product_uom_qty",
    )
    def _compute_amount(self):
        for line in self:
            order_line = line.object_id
            line.amount = line._get_commission_amount(
                line.commission_id,
                order_line.price_subtotal,
                order_line.product_id,
                order_line.product_uom_qty,
            )