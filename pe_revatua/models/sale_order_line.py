# -*- coding: utf-8 -*-
import logging
from odoo import fields, models, api

_logger = logging.getLogger(__name__)

class SaleOrderLineInherit(models.Model):
    _inherit = "sale.order.line"
    
    tarif_rpa = fields.Float(string='RPA', default=0, required=True)
    tarif_maritime = fields.Float(string='Maritime', default=0, required=True)
    tarif_terrestre = fields.Float(string='Terrestre', default=0, required=True)
            
    @api.onchange('product_id')
    def product_id_change(self):
        #### OVERRIDE ####
        res = super(SaleOrderLineInherit, self).product_id_change()
        # Check if revatua is activate
        revatua_state = self.env.company.revatua_ck
        if revatua_state:
            company_name = self.env.company.name
            _logger = logging.error('Revatua : %s | Société : %s' % (revatua_state,company_name))
            product = self.product_id
            self.tarif_terrestre = product.tarif_terrestre
            self.tarif_maritime = product.tarif_maritime
            self.tarif_rpa = product.tarif_rpa
        return res
    
    @api.onchange('product_packaging_id', 'product_uom', 'product_uom_qty')
    def _onchange_update_product_packaging_qty(self):
        #### OVERRIDE ####
        #Terrestre 60% du prix & maritime 40% du prix
        res = super(SaleOrderLineInherit, self)._onchange_update_product_packaging_qty()
        # Check if revatua is activate
        revatua_state = self.env.company.revatua_ck
        if revatua_state and self.tarif_terrestre != 0 or self.tarif_maritime != 0:
            self.tarif_terrestre = self.price_subtotal * 0.6
            self.tarif_maritime = self.price_subtotal * 0.4
            if self.tarif_rpa != 0:
                self.tarif_rpa = self.product_uom_qty * 100
        return res
    