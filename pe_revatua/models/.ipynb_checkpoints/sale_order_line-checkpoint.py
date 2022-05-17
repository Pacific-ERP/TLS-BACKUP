# -*- coding: utf-8 -*-
import logging
from odoo import fields, models, api

_logger = logging.getLogger(__name__)

class SaleOrderLineInherit(models.Model):
    _inherit = "sale.order.line"
    
    tarif_rpa = fields.Float(string='RPA', default=0, required=True)
    tarif_maritime = fields.Float(string='Maritime', default=0, required=True)
    tarif_terrestre = fields.Float(string='Terrestre', default=0, required=True)
    
    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        ##################
        #### OVERRIDE ####
        ##################
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_shipping_id)
            line.update({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })
            if self.env.context.get('import_file', False) and not self.env.user.user_has_groups('account.group_account_manager'):
                line.tax_id.invalidate_cache(['invoice_repartition_line_ids'], [line.tax_id.id])
    
    @api.onchange('product_id')
    def product_id_change(self):
        ##################
        #### OVERRIDE ####
        ##################
        res = super(SaleOrderLineInherit, self).product_id_change()
        # Check if revatua is activate
        revatua_state = self.env.company.revatua_ck
        if revatua_state:
            company_name = self.env.company.name
            product = self.product_id
            self.tarif_terrestre = product.tarif_terrestre
            self.tarif_maritime = product.tarif_maritime
            self.tarif_rpa = product.tarif_rpa
        return res
    
    @api.onchange('product_packaging_id', 'product_uom', 'product_uom_qty')
    def _onchange_update_product_packaging_qty(self):
        ##################
        #### OVERRIDE ####
        ##################
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
    