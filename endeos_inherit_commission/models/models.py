
from odoo import api, fields, models

class SaleOrderLineAgent(models.Model):
    _inherit = "sale.order.line.agent"

    # Nuevo campo para seleccionar una comisión entre todas las disponibles
    all_commission_id = fields.Many2one(
        'commission', 
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

class SaleOrderLineAgent(models.Model):
    _inherit = "commission.line.mixin"
    
    @api.onchange('all_commission_id')
    def _onchange_all_commission_id(self):
        for record in self:
            record.commission_id = record.all_commission_id
    