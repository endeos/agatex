from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class CustomPurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def create(self, vals):
        # si 'name' ya viene definido en 'vals' por la llamada API
        if 'name' in vals and vals['name']:
            header_id = vals.get('name', False)
            try:
                vals['name'] = header_id
            except ValueError:
                # usar el valor por defecto
                pass
        else:
            # usar el valor por defecto
            pass
        _logger.warning(f"No se encontró la UoM para {vals}")
        
        return super(CustomPurchaseOrder, self).create(vals)