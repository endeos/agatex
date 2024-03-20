# # -*- coding: utf-8 -*-

# from odoo import models, fields, api
# from datetime import datetime
# import logging

# _logger = logging.getLogger(__name__)
    

# class CommissionSettleLine(models.Model):
#     _inherit = 'commission.settlement.line'
    
#     commission_ids = fields.Many2many(
#         comodel_name="commission",
#         string="Commissions",
#         copy=True
#     )
    
# class SaleOrderLineAgent(models.Model):
#     _inherit = "sale.order.line.agent"
    
#     @api.depends(
#         "commission_ids",
#         "object_id.price_subtotal",
#         "object_id.product_id",
#         "object_id.product_uom_qty",
#     )
#     def _compute_amount(self):
#         for line in self:
#             order_line = line.object_id
#             line.amount = line._get_commission_amount(
#                 line.commission_ids,
#                 order_line.price_subtotal,
#                 order_line.product_id,
#                 order_line.product_uom_qty,
#             )
            
# class CommissionLineMixin(models.AbstractModel):
#     _inherit = "commission.line.mixin"

#     commission_ids = fields.Many2many(
#             comodel_name="commission",
#             string="Commissions",
#             compute="_compute_commission_id",
#             copy=True
#         )
#     @api.depends("agent_id")
#     def _compute_commission_id(self):
#         for record in self:
#             record.commission_ids = record.agent_id.commission_id
from odoo import api, fields, models

class SaleOrderLineAgent(models.Model):
    _inherit = "sale.order.line.agent"

    # Nuevo campo para seleccionar una comisión entre todas las disponibles
    all_commission_id = fields.Many2one(
        'sale.commission', 
        string="All Commissions"
    )

    @api.depends(
        "all_commission_id",  # Cambiar a la nueva comisión seleccionada
        "object_id.price_subtotal",
        "object_id.product_id",
        "object_id.product_uom_qty",
    )
    def _compute_amount(self):
        for line in self:
            order_line = line.object_id
            commission = line.all_commission_id or line.commission_id  # Usar la nueva comisión si está disponible
            line.amount = line._get_commission_amount(
                commission,
                order_line.price_subtotal,
                order_line.product_id,
                order_line.product_uom_qty,
            )
            