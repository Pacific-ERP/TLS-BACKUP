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
        res = super(SaleOrderLineInherit, self).product_id_change()
        product = self.product_id
        self.tarif_terrestre = product.tarif_terrestre
        self.tarif_maritime = product.tarif_maritime
        self.tarif_rpa = product.tarif_rpa
        return res
    