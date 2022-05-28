# -*- coding: utf-8 -*-
import logging
from odoo import fields, models, api

_logger = logging.getLogger(__name__)

class SaleOrderLineInherit(models.Model):
    _inherit = "sale.order.line"
    
    tarif_rpa = fields.Float(string='RPA', default=0, required=True)
    tarif_maritime = fields.Float(string='Maritime', default=0, required=True)
    tarif_terrestre = fields.Float(string='Terrestre', default=0, required=True)
    r_volume = fields.Float(string='Volume Revatua (m³)', default=0)
    r_weight = fields.Float(string='Volume weight (T)', default=0)
    check_adm = fields.Boolean(string='Payé par ADM', related="product_id.check_adm")
    revatua_uom = fields.Many2one(string='Udm', comodel_name='uom.uom')
    
    @api.onchange('product_id')
    def product_id_change(self):
        ##################
        #### OVERRIDE ####
        ##################
        res = super(SaleOrderLineInherit, self).product_id_change()
        # Check if revatua is activate
        revatua_state = self.env.company.revatua_ck
        if revatua_state:
            product = self.product_id
            self.tarif_terrestre = product.tarif_terrestre
            self.tarif_maritime = product.tarif_maritime
            self.tarif_rpa = product.tarif_rpa
        return res
    
    @api.onchange('r_volume','r_weight')
    def _onchange_update_qty(self):
        # Calcul volume si poids + volume alors product_qty = (poids+volume)/2, sinon soit l'un soit l'autre
            if self.r_volume and self.r_weight:
                self.product_uom_qty = (self.r_volume + self.r_weight) / 2
                self.revatua_uom = 29
            elif self.r_weight and not self.r_volume:
                self.product_uom_qty = self.r_weight
                self.revatua_uom = 7
            elif self.r_volume and not self.r_weight:
                self.product_uom_qty = self.r_volume
                self.revatua_uom = 12
            else:
                self.product_uom_qty = 1
    
    @api.onchange('product_packaging_id', 'product_uom', 'product_uom_qty')
    def _onchange_update_product_packaging_qty(self):
        ##################
        #### OVERRIDE ####
        ##################
        #Terrestre 60% du prix & maritime 40% du prix
        res = super(SaleOrderLineInherit, self)._onchange_update_product_packaging_qty()
        # Check if revatua is activate
        revatua_state = self.env.company.revatua_ck
        
        if revatua_state:
            # Calcul des part maritime et part terrestre    
            if self.tarif_terrestre or self.tarif_maritime:   
                self.tarif_terrestre = self.price_subtotal * 0.6
                self.tarif_maritime = self.price_subtotal * 0.4
                if self.tarif_rpa != 0:
                    self.tarif_rpa = self.product_uom_qty * 100
        return res
    
    def _prepare_procurement_values(self, group_id=False):
        values = super(SaleOrderLineInherit, self)._prepare_procurement_values(group_id)
        self.ensure_one()
        _logger.error('Avant : %s' % values)
        values.update({
            'tarif_rpa': self.tarif_rpa,
            'tarif_maritime': self.tarif_maritime,
            'tarif_terrestre': self.tarif_terrestre,
            'r_volume': self.r_volume,
            'r_weight': self.r_weight,
        })
        _logger.error('Après : %s' % values)
        return values
    