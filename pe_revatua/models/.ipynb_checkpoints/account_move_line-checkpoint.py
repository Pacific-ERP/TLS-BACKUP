# -*- coding: utf-8 -*-
import logging
from odoo import fields, models, api

_logger = logging.getLogger(__name__)

class AccountMoveLineInherit(models.Model):
    _inherit = "account.move.line"
    
    tarif_rpa = fields.Float(string='RPA', default=0, required=True, store=True)
    tarif_maritime = fields.Float(string='Maritime', default=0, required=True, store=True)
    tarif_terrestre = fields.Float(string='Terrestre', default=0, required=True, store=True)
    r_volume = fields.Float(string='Volume Revatua (m³)', default=0, store=True)
    r_weight = fields.Float(string='Volume weight (T)', default=0, store=True)
    revatua_uom = fields.Char(string='Udm', store=True)
    check_adm = fields.Boolean(string='Payé par ADM', related="product_id.check_adm")
    
    old_subtotal = fields.Float(string='Base Total HT', default=0, store=True)
    base_qty = fields.Float(string='Base Quantity', default=0, store=True)
    
    def _get_price_total_and_subtotal_model(self, price_unit, quantity, discount, currency, product, partner, taxes, move_type):
        #########################
        #### OVERRIDE METHOD ####
        #########################
        res = super(AccountMoveLineInherit, self)._get_price_total_and_subtotal_model(price_unit, quantity, discount, currency, product, partner, taxes, move_type)
        # --- Check if revatua is activate ---#
        if self.env.company.revatua_ck:
            if self.check_adm:
                if not self.move_id.is_adm_invoice:
                    old_subtotal = res['price_subtotal']
                    self.old_subtotal = old_subtotal
                    new_subtotal = (res['price_subtotal'] - old_subtotal) + self.tarif_terrestre
                    res['price_subtotal'] = new_subtotal
                else:
                    old_subtotal = res['price_subtotal']
                    self.old_subtotal = old_subtotal
                    new_subtotal = (res['price_subtotal'] - old_subtotal) + self.tarif_maritime
                    res['price_subtotal'] = new_subtotal
        else:
            _logger.error('Revatua not activate : account_move_line.py -> _get_price_total_and_subtotal_model')
        return res
    
    def _prepare_line_admg(self, sequence=1):
        self.ensure_one()
        vals = {
            'sequence': sequence,
            'display_type': self.display_type,
            'product_id': self.product_id,
            'r_volume': self.r_volume,
            'r_weight': self.r_weight,
            'quantity': self.quantity,
            'revatua_uom': self.revatua_uom,
            'price_subtotal': self.price_subtotal,
            'tax_id': [(6,0,[137])], #RPA id
            'tarif_terrestre': self.tarif_terrestre,
            'tarif_maritime': self.tarif_maritime,
            'tarif_rpa': self.tarif_rpa,
            'price_total': self.price_total,
        }
        _logger.error('Seq : %s | Ligne: %s' % (sequence,vals))
        return vals