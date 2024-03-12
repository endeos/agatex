from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class CustomAccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def create(self, vals):
        _logger.info(f"creando invoice a partir de sale order | values {vals}")
        # Verificar si partner_id está en vals y obtener el país del socio
        partner_id = vals.get('partner_id')
        if partner_id:
            partner = self.env['res.partner'].browse(partner_id)
            if partner.country_id and partner.country_id.code != 'ES':
                vals['intrastat_country_id'] = partner.country_id.id

        # Luego llamamos al método original para crear la factura
        return super(CustomAccountMove, self).create(vals)