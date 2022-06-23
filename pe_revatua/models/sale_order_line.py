# -*- coding: utf-8 -*-
import logging
from odoo import fields, models, api

_logger = logging.getLogger(__name__)

class SaleOrderLineInherit(models.Model):
    _inherit = "sale.order.line"
    
    # Tarif de ventes
    tarif_minimum = fields.Float(string='Prix Minimum', default=0, required=True, store=True)
    
    # -- RPA --#
    base_rpa = fields.Float(string='Base RPA', store=True)
    tarif_rpa = fields.Float(string='RPA', default=0, store=True)
    tarif_minimum_rpa = fields.Float(string='Minimum RPA', store=True)
    
    # -- Maritime --#
    base_maritime = fields.Float(string='Base Maritime', store=True)
    tarif_maritime = fields.Float(string='Maritime', default=0, store=True)
    tarif_minimum_maritime = fields.Float(string='Minimum Maritime', store=True)
    
    # -- Terrestre --#
    base_terrestre = fields.Float(string='Base Terrestre', store=True)
    tarif_terrestre = fields.Float(string='Terrestre', default=0, store=True)
    tarif_minimum_terrestre = fields.Float(string='Minimum Terrestre', store=True)
    
    # Calcul & check
    r_volume = fields.Float(string='Volume Revatua (m³)', store=True)
    r_weight = fields.Float(string='Volume weight (T)', store=True)
    check_adm = fields.Boolean(string='Payé par ADM', store=True)
    
    @api.onchange('product_id')
    def product_id_change(self):
        ##################
        #### OVERRIDE ####
        ##################
        res = super(SaleOrderLineInherit, self).product_id_change()
        # --- Check if revatua is activate ---#
        if self.env.company.revatua_ck:
            self.tarif_minimum = self.product_id.tarif_minimum
            self.check_adm = self.product_id.check_adm
            # Terrestre
            self.base_terrestre = self.product_id.tarif_terrestre
            self.tarif_minimum_terrestre = self.product_id.tarif_minimum_terrestre
            # Maritime
            self.base_maritime = self.product_id.tarif_maritime
            self.tarif_minimum_maritime = self.product_id.tarif_minimum_maritime
            # RPA
            self.base_rpa = self.product_id.tarif_rpa
            self.tarif_minimum_rpa = self.product_id.tarif_minimum_rpa
        else:
            _logger.error('Revatua not activate : sale_order_line.py -> product_id_change')
        return res        
    
    @api.onchange('r_volume','r_weight')
    def _onchange_update_qty(self):
        # Calcul volume si poids + volume alors product_qty = (poids+volume)/2, sinon soit l'un soit l'autre
        # --- Check if revatua is activate ---#
        if self.env.company.revatua_ck:
            if self.r_volume and self.r_weight:
                self.product_uom_qty = (self.r_volume + self.r_weight) / 2
                self.product_uom = self.env['uom.uom'].sudo().search([('name','=','T/m³')]) #'T/m³'
            elif self.r_weight and not self.r_volume:
                self.product_uom_qty = self.r_weight
                self.product_uom = self.env['uom.uom'].sudo().search([('name','=','T')]) #'T'
            elif self.r_volume and not self.r_weight:
                self.product_uom_qty = self.r_volume
                self.product_uom = self.env['uom.uom'].sudo().search([('name','=','m3')]) #'m³'
            else:
                self.product_uom_qty = 1
                self.product_uom = self.env['uom.uom'].sudo().search([('name','=','m3')]) #'m³'
        else:
            _logger.error('Revatua not activate : sale_order_line.py -> _onchange_update_qty')
    
    @api.onchange('product_packaging_id', 'product_uom', 'product_uom_qty')
    def _onchange_update_product_packaging_qty(self):
        ##################
        #### OVERRIDE ####
        ##################
        #Terrestre 60% du prix & maritime 40% du prix
        res = super(SaleOrderLineInherit, self)._onchange_update_product_packaging_qty()
        # --- Check if revatua is activate ---#
        if self.env.company.revatua_ck:
            # Calcul des part maritime et part terrestre
            if self.base_terrestre:
                if self.tarif_minimum_terrestre and (self.product_uom_qty * self.base_terrestre) < self.tarif_minimum_terrestre:
                    self.tarif_terrestre = self.tarif_minimum_terrestre
                else:
                    self.tarif_terrestre = self.product_uom_qty * self.base_terrestre
            if self.base_maritime:
                if self.tarif_minimum_maritime and (self.product_uom_qty * self.base_maritime) < self.tarif_minimum_maritime:
                    self.tarif_maritime = self.tarif_minimum_maritime
                else:
                    self.tarif_maritime = self.product_uom_qty * self.base_maritime
            if self.base_rpa:
                if self.tarif_minimum_rpa and (self.product_uom_qty * self.base_rpa) < self.tarif_minimum_rpa:
                    self.tarif_rpa = self.tarif_minimum_rpa
                else:
                    self.tarif_rpa = self.product_uom_qty * self.base_rpa
        else:
            _logger.error('Revatua not activate : sale_order_line.py -> _onchange_update_product_packaging_qty')
        return res
# === Stock Move === #
    def _prepare_procurement_values(self, group_id=False):
        ##################
        #### OVERRIDE ####
        ##################
        values = super(SaleOrderLineInherit, self)._prepare_procurement_values(group_id)
        # --- Check if revatua is activate ---#
        if self.env.company.revatua_ck:
            self.ensure_one()
            values.update({
                'tarif_rpa': self.tarif_rpa,
                'tarif_maritime': self.tarif_maritime,
                'tarif_terrestre': self.tarif_terrestre,
                'check_adm': self.check_adm,
                'r_volume': self.r_volume,
                'r_weight': self.r_weight,
            })
        else:
            _logger.error('Revatua not activate : sale_order_line.py -> _prepare_procurement_values')
        return values
    
# === Invoice === #

    # Ligne d'articles de la(les) facture(s)
    def _prepare_invoice_line(self, **optional_values):
        ##################
        #### OVERRIDE ####
        ##################
        values = super(SaleOrderLineInherit, self)._prepare_invoice_line(**optional_values)
        # --- Check if revatua is activate ---#
        if self.env.company.revatua_ck:
            values.update({
                'tarif_rpa': self.tarif_rpa,
                'tarif_maritime': self.tarif_maritime,
                'tarif_terrestre': self.tarif_terrestre,
                'check_adm': self.check_adm,
                'r_volume': self.r_volume,
                'r_weight': self.r_weight,
                'base_qty': self.product_uom_qty,
                'base_unit_price':self.price_unit,
                'base_subtotal':self.price_subtotal,
                'base_rpa':self.tarif_rpa,
                'base_maritime':self.tarif_maritime,
                'base_terrestre':self.tarif_terrestre,
                'base_total':self.price_total,
            })
        else:
            _logger.error('Revatua not activate : sale_order_line.py -> _prepare_invoice_line')
        return values
    
    # Ligne d'articles pour les factures ADM
    def _prepare_invoice_line_adm_part(self, **optional_values):
        values = super(SaleOrderLineInherit, self)._prepare_invoice_line(**optional_values)
        # --- Check if revatua is activate ---#
        # L'administration paie la part maritime et RPA uniquement
        if self.env.company.revatua_ck:
            values.update({
                'tarif_rpa': self.tarif_rpa,
                'tarif_maritime': self.tarif_maritime,
                'tarif_terrestre': 0,
                'check_adm': self.check_adm,
                'r_volume': self.r_volume,
                'r_weight': self.r_weight,
                'base_qty': self.product_uom_qty,
                'base_unit_price':self.price_unit,
                'base_subtotal':self.price_subtotal,
                'base_rpa':self.tarif_rpa,
                'base_maritime':self.tarif_maritime,
                'base_terrestre':self.tarif_terrestre,
                'base_total':self.price_total,
            })
            for tax in self.tax_id:
                if tax.name == 'RPA':
                    values.update({'tax_ids' : [(6,0,[tax.id])]})
        else:
            _logger.error('Revatua not activate : sale_order_line.py -> _prepare_invoice_line_adm_part')
        return values
    
    # Ligne d'articles pour les factures Client
    def _prepare_invoice_line_non_adm(self, **optional_values):
        values = super(SaleOrderLineInherit, self)._prepare_invoice_line(**optional_values)
        # --- Check if revatua is activate ---#
        if self.env.company.revatua_ck:
            # Le client ne paie pas la part Maritime et RPA si l'article est ADM
            values.update({
                'tarif_rpa': 0,
                'tarif_maritime': 0,
                'tarif_terrestre': self.tarif_terrestre,
                'check_adm': self.check_adm,
                'r_volume': self.r_volume,
                'r_weight': self.r_weight,
                'base_qty': self.product_uom_qty,
                'base_unit_price':self.price_unit,
                'base_subtotal':self.price_subtotal,
                'base_rpa':self.tarif_rpa,
                'base_maritime':self.tarif_maritime,
                'base_terrestre':self.tarif_terrestre,
                'base_total':self.price_total,
            })
            tax_list=[]
            for tax in self.tax_id:
                if not tax.name == 'RPA':
                    tax_list.append(tax.id)
            values.update({'tax_ids' : [(6,0,tax_list)]})
        else:
            _logger.error('Revatua not activate : sale_order_line.py -> _prepare_invoice_line_non_adm')
        return values  

class SaleOrderOptionInherit(models.Model):
    _inherit = "sale.order.option"
    
    # Tarif de ventes
    tarif_minimum = fields.Float(string='Prix Minimum', default=0, required=True, store=True)
    
    # -- RPA --#
    base_rpa = fields.Float(string='Base RPA', store=True)
    tarif_rpa = fields.Float(string='RPA', default=0, store=True)
    tarif_minimum_rpa = fields.Float(string='Minimum RPA', store=True)
    
    # -- Maritime --#
    base_maritime = fields.Float(string='Base Maritime', store=True)
    tarif_maritime = fields.Float(string='Maritime', default=0, store=True)
    tarif_minimum_maritime = fields.Float(string='Minimum Maritime', store=True)
    
    # -- Terrestre --#
    base_terrestre = fields.Float(string='Base Terrestre', store=True)
    tarif_terrestre = fields.Float(string='Terrestre', default=0, store=True)
    tarif_minimum_terrestre = fields.Float(string='Minimum Terrestre', store=True)
    
    # Calcul & check
    r_volume = fields.Float(string='Volume Revatua (m³)', store=True)
    r_weight = fields.Float(string='Volume weight (T)', store=True)
    check_adm = fields.Boolean(string='Payé par ADM', store=True)
