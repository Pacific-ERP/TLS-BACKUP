# -*- coding: utf-8 -*-
import logging
from odoo import fields, models, api

_logger = logging.getLogger(__name__)

class AccountMoveLineInherit(models.Model):
    _inherit = "account.move.line"
    
    r_volume = fields.Float(string='Volume Revatua (m³)', default=0, store=True)
    r_weight = fields.Float(string='Volume weight (T)', default=0, store=True)
    check_adm = fields.Boolean(string='Payé par ADM', related="product_id.check_adm")
    
    # Field from Sales line before recompute of value
    base_qty = fields.Float(string='Base Quantity', default=0, store=True)
    base_unit_price = fields.Float(string='Origin Unit Price', default=0, store=True)
    base_subtotal = fields.Float(string='Base Total HT', default=0, store=True)
    base_total = fields.Float(string='Base Total TTC', default=0, store=True)
    
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
    
    @api.onchange('quantity', 'discount', 'price_unit', 'tax_ids')
    def _onchange_price_subtotal(self):
        ### Override ###
        for line in self:
            if not line.move_id.is_invoice(include_receipts=True):
                continue
            # --- Check if revatua is activate ---#
            if self.env.company.revatua_ck:
                # Pour la facture Administration article ADM
                if line.check_adm and line.move_id.is_adm_invoice:
                    if line.base_unit_price:
                        price_adm = line.base_maritime
                        if price_adm < line.product_id.tarif_minimum_maritime:
                            price_adm = line.product_id.tarif_minimum_maritime
                        line.update(line._get_price_total_and_subtotal(price_unit=price_adm) )
                        line.update(line._get_fields_onchange_subtotal())
                        
                # Pour la facture client article ADM
                elif line.check_adm and not line.move_id.is_adm_invoice:
                    if line.base_unit_price:
                        price_custo = line.base_terrestre
                        if price_custo < line.product_id.tarif_minimum_terrestre:
                            price_custo = line.product_id.tarif_minimum_terrestre
                        line.update(line._get_price_total_and_subtotal(price_unit=price_custo) )
                        line.update(line._get_fields_onchange_subtotal())
                else:
                    line.update(line._get_price_total_and_subtotal())
                    line.update(line._get_fields_onchange_subtotal())
                    line.update({'tarif_maritime': (line.quantity * line.base_terrestre), 
                                 'tarif_terrestre': (line.quantity * line.base_maritime),
                                 'tarif_rpa': line.quantity * line.base_rpa,})
            # Autres
            else:
                 _logger.error('Revatua not activate : account_move_line.py -> _onchange_price_subtotal')
                 line.update(line._get_price_total_and_subtotal())
                 line.update(line._get_fields_onchange_subtotal())
    
    @api.onchange('r_volume','r_weight')
    def _onchange_update_qty(self):
        _logger.error('_onchange_update_qty')
        # Calcul volume si poids + volume alors product_qty = (poids+volume)/2, sinon soit l'un soit l'autre
        # --- Check if revatua is activate ---#
        if self.env.company.revatua_ck:
            if self.r_volume and self.r_weight:
                self.quantity = (self.r_volume + self.r_weight) / 2
                self.product_uom_id = self.env['uom.uom'].sudo().search([('name','=','T/m³')]) #'T/m³'
            elif self.r_weight and not self.r_volume:
                self.quantity = self.r_weight
                self.product_uom_id = self.env['uom.uom'].sudo().search([('name','=','T')]) #'T'
            elif self.r_volume and not self.r_weight:
                self.quantity = self.r_volume
                self.product_uom_id = self.env['uom.uom'].sudo().search([('name','=','m3')]) #'m³'
            else:
                self.quantity = 1
                self.product_uom_id = self.env['uom.uom'].sudo().search([('name','=','m3')]) #'m³'
        else:
            _logger.error('Revatua not activate : account_move_line.py -> _onchange_update_qty')
    
    def _prepare_line_admg(self, sequence=1):
        self.ensure_one()
        vals = {
            'sequence': sequence,
            'display_type': self.display_type,
            'product_id': self.product_id,
            'r_volume': self.r_volume,
            'r_weight': self.r_weight,
            'quantity': self.quantity,
            'price_subtotal': self.price_subtotal,
            'tax_id': [(6,0,[137])], #RPA id
            'tarif_terrestre': self.tarif_terrestre,
            'tarif_maritime': self.tarif_maritime,
            'tarif_rpa': self.tarif_rpa,
            'price_total': self.price_total,
        }
        #_logger.error('Seq : %s | Ligne: %s' % (sequence,vals))
        return vals