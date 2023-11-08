# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = "account.move"

    #Al enviar una factura, selecciona por defecto la plantilla de correo "[AGX]Factura: Enviando"
    def action_invoice_sent(self):      
        res = super().action_invoice_sent()
        res['context']['default_template_id'] = self.env['mail.template'].search([('id', '=','23')],limit=1).id
        return res