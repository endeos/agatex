# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)
    

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    iva_21 = fields.Float(string="IVA 21%")
    iva_10 = fields.Float(string="IVA 10%")
    iva_4 = fields.Float(string="IVA 4%")

    irpf_19 = fields.Float(string="IRPF 19%")
    irpf_15 = fields.Float(string="IRPF 15%")
    irpf_7 = fields.Float(string="IRPF 7%")

    base_iva_21 = fields.Float(string="Base imponible IVA 21")

            
    def _get_taxes_dict_by_ivoice_id(self, move_id):
        """
        Auxiliar method that returns the calculations of the tax columns in an object
        """
        move = self.env['account.move'].search([('id', '=', move_id)])
        
        iva_21 = 0.0
        iva_10 = 0.0
        iva_4 = 0.0

        irpf_19 = 0.0
        irpf_15 = 0.0
        irpf_7 = 0.0

        base_iva_21 = 0.0
        base_iva_10 = 0.0
        base_iva_4 = 0.0

        base_irpf_19 = 0.0
        base_irpf_15 = 0.0
        base_irpf_7 = 0.0


        for line in move.invoice_line_ids:

            """ line_price = line.price_unit * line.quantity
            discount = (line_price * line.discount / 100.0)
            line_total = line_price - discount """

            line_price = line.balance * -1
            line_total = line_price

            for tax in line.tax_ids:

                is_IVA_21 = tax.amount == 21.0 and tax.name.find("IVA") >= 0
                is_IVA_10 = tax.amount == 10.0 and tax.name.find("IVA") >= 0
                is_IVA_4 = tax.amount == 4.0 and tax.name.find("IVA") >= 0

                is_IRPF_19 = tax.amount == -19.0 and tax.name.find("IRPF") >= 0
                is_IRPF_15 = tax.amount == -15.0 and tax.name.find("IRPF") >= 0
                is_IRPF_7 = tax.amount == -7.0 and tax.name.find("IRPF") >= 0

                tax_amount = line_total * (tax.amount / 100.0)

                if is_IVA_21:
                    iva_21 += tax_amount
                    base_iva_21 += line_total
                if is_IVA_10:
                    iva_10 += tax_amount
                    base_iva_10 += line_total
                if is_IVA_4:
                    iva_4 += tax_amount
                    base_iva_4 += line_total

                if is_IRPF_19:
                    irpf_19 += tax_amount
                    base_irpf_19 += line_total
                if is_IRPF_15:
                    irpf_15 += tax_amount
                    base_irpf_15 += line_total
                if is_IRPF_7:
                    irpf_7 += tax_amount
                    base_irpf_7 += line_total
        
        total_iva_21 = base_iva_21 * (21.0 / 100.0)
        total_iva_10 = base_iva_10 * (10.0 / 100.0)
        total_iva_4 = base_iva_4 * (4.0 / 100.0)

        total_irpf_19 = base_irpf_19 * (-19.0 / 100.0)
        total_irpf_15 = base_irpf_15 * (-15.0 / 100.0)
        total_irpf_7 = base_irpf_7 * (-7.0 / 100.0)
        
        """taxes_dict = {
            "iva_21": iva_21,
            "iva_10": iva_10,
            "iva_4": iva_4,
            "irpf_19": irpf_19,
            "irpf_15": irpf_15,
            "irpf_7": irpf_7
        }"""

        taxes_dict = {
            "iva_21": round(total_iva_21, 2),
            "iva_10": round(total_iva_10, 2),
            "iva_4": round(total_iva_4, 2),
            "irpf_19": round(total_irpf_19, 2),
            "irpf_15": round(total_irpf_15, 2),
            "irpf_7": round(total_irpf_7, 2),
            "base_iva_21": round(base_iva_21, 2)
        }

        
        return taxes_dict
    

    def _update_tax_columns(self):
        for move in self:
            taxes_dict = move._get_taxes_dict_by_ivoice_id(move.id)
            # control mecanism to avoid infinite loop in write method
            taxes_dict["skip_update_tax_columns"] = True
            move.write(taxes_dict)
    
    
    def button_recalculate_tax_columns(self):
        """
        Recalculates tax columns of all invoices within current year
        """
        limit_date = datetime.now().date().replace(year=datetime.now().year - 1, month=1, day=1)  

        invoices = self.env['account.move'].search([('invoice_date', '>=', limit_date.strftime("%m/%d/%Y"))])

        for move in invoices:
            taxes_dict = move._get_taxes_dict_by_ivoice_id(move.id)
            move.write(taxes_dict)
    

    
    def write(self, values):
        """
        Recalculate tax columns before saving
        """
        for move in self:
            if values.get("skip_update_tax_columns"):
                # tax columns calculated, no need to recalculate
                del values["skip_update_tax_columns"]
                record = super().write(values)
            else:
                # tax columns need to be calculated                
                record = super().write(values)
                move._update_tax_columns()

            return record
            