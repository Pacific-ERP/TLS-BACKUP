# -*- coding: utf-8 -*-
import logging
import math
from odoo import fields, models, api
from odoo.addons.account.models.account_move import AccountMoveLine as AMoveLine

_logger = logging.getLogger(__name__)

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    
    r_volume = fields.Float(string='Volume Revatua (m³)', default=0, store=True, digits=(12, 3))
    r_weight = fields.Float(string='Volume weight (T)', default=0, store=True, digits=(12, 3))
    check_adm = fields.Boolean(string='Payé par ADM', related="product_id.check_adm")
    
    # Field from Sale lines before recompute of value (JIC)
    base_qty = fields.Float(string='Base Quantity', default=0, store=True)
    base_unit_price = fields.Float(string='Origin Unit Price', default=0, store=True)
    base_subtotal = fields.Float(string='Base Total HT', default=0, store=True)
    base_total = fields.Float(string='Base Total TTC', default=0, store=True)
    
    # -- RPA --#
    base_rpa = fields.Float(string='Base RPA', store=True)
    tarif_rpa = fields.Float(string='RPA', default=0, store=True)
    tarif_rpa_ttc = fields.Float(string='RPA TTC', default=0, store=True)
    tarif_minimum_rpa = fields.Float(string='Minimum RPA', store=True)
    
    # -- Maritime --#
    base_maritime = fields.Float(string='Base Maritime', store=True)
    tarif_maritime = fields.Float(string='Maritime', default=0, store=True)
    tarif_minimum_maritime = fields.Float(string='Minimum Maritime', store=True)
    
    # -- Terrestre --#
    base_terrestre = fields.Float(string='Base Terrestre', store=True)
    tarif_terrestre = fields.Float(string='Terrestre', default=0, store=True)
    tarif_minimum_terrestre = fields.Float(string='Minimum Terrestre', store=True)
    
    # Tarif de ventes
    tarif_minimum = fields.Float(string='Prix Minimum', default=0, required=True, store=True)
    
    # Définie la quantité selon l'unité de mesure utilisé
    @api.onchange('product_uom_id', 'r_volume', 'r_weight')
    def _onchange_update_qty(self):
        # --- Check if revatua is activated ---#
        if self.env.company.revatua_ck:
            vals = {'quantity': 1}
            
            m3 = self.env.ref('pe_revatua.revatua_udm_mcube')
            t = self.env.ref('pe_revatua.revatua_udm_tons')
            t_m3 = self.env.ref('pe_revatua.revatua_udm_mcube_tons')
            
            # T/M3
            if self.product_uom_id.id == t_m3.id and self.r_volume and self.r_weight:
                vals['quantity'] = round((self.r_volume + self.r_weight) / 2, 3)
            # T
            elif self.product_uom_id.id == t.id and self.r_weight:
                vals['quantity'] = self.r_weight
            # M3
            elif self.product_uom_id.id == m3.id and self.r_volume:
                vals['quantity'] = self.r_volume

            self.write(vals)

    @api.onchange('product_id')
    def _pe_onchange_product_id(self):
        # --- Check if revatua is activated ---#
        if self.env.company.revatua_ck and self.product_id:
            vals = {'check_adm': self.product_id.check_adm,
                    'tarif_minimum': self.product_id.tarif_minimum,
                    'base_terrestre': self.product_id.tarif_terrestre,
                    'tarif_terrestre': self.product_id.tarif_terrestre,
                    'tarif_minimum_terrestre': self.product_id.tarif_minimum_terrestre,
                    'base_maritime': self.product_id.tarif_maritime,
                    'tarif_maritime': self.product_id.tarif_maritime,
                    'tarif_minimum_maritime': self.product_id.tarif_minimum_maritime,
                    'base_rpa': self.product_id.tarif_rpa,
                    'tarif_rpa': self.product_id.tarif_rpa,
                    'tarif_minimum_rpa': self.product_id.tarif_minimum_rpa}
            
            self.with_context(check_move_validity=False).write(vals)
   
    # Méthode de calcule pour les tarifs par lignes
    def _compute_amount_base_revatua(self, base=0.0, qty=0.0, mini_amount=0.0, discount=1):
        """ Renvoie le montant de la part (terrestre,maritime,rpa) au changement de quantités

            param float base : Valeur de la base de la part à tester
            param float qty : la quantités
            param discount : 1 - (remise/100) -> si remise existant résultat < 0 sinon 1
            param mini_amount : Minimum que la part peut prendre
        """
        # Effectue une condition ternaire plutôt qu'une instruction if / else 
        res = round(mini_amount if (mini_amount and ((base * discount) * qty) < mini_amount) else (base * discount) * qty, 0)
        # _logger.error(f"[Facture : Calcul Tarif] _compute_amount_base_revatua : {res}")
        return res
        
    # Recalcul des part terrestre et maritime selon la quantité et la remise
    @api.onchange('quantity','discount')
    def _compute_revatua_part(self):
        # --- Check if revatua is activated ---#
        if self.env.company.revatua_ck and self.product_id:
            # Remise si existant : remise < 1 sinon = 1
            discount = 1-(self.discount/100)
            quantity = self.quantity
            self.tarif_terrestre = self._compute_amount_base_revatua(self.base_terrestre, quantity, self.tarif_minimum_terrestre, discount)
            self.tarif_maritime = self._compute_amount_base_revatua(self.base_maritime, quantity, self.tarif_minimum_maritime, discount)
            self.tarif_rpa_ttc = self._compute_amount_base_revatua(self.base_rpa, quantity, self.tarif_minimum_rpa, discount)
            self.tarif_rpa = self._compute_amount_base_revatua(self.base_rpa, quantity, self.tarif_minimum_rpa, discount)
    
    def _get_price_total_and_subtotal(self, price_unit=None, quantity=None, discount=None, currency=None, product=None, partner=None, taxes=None, move_type=None, line=None):
        # OVERRIDE
        self.ensure_one()
        return self._get_price_total_and_subtotal_model(
            price_unit=self.price_unit if price_unit is None else price_unit,
            quantity=self.quantity if quantity is None else quantity,
            discount=self.discount if discount is None else discount,
            currency=self.currency_id if currency is None else currency,
            product=self.product_id if product is None else product,
            partner=self.partner_id if partner is None else partner,
            taxes=self.tax_ids if taxes is None else taxes,
            move_type=self.move_id.move_type if move_type is None else move_type,
            # Récupération de ligne pour simplifier les calculs des taxes
            line= self if line is None else line,
        )
    
    @api.model
    def _get_price_total_and_subtotal_model(self, price_unit, quantity, discount, currency, product, partner, taxes, move_type, line=None):
        # OVERRIDE
        ''' This method is used to compute 'price_total' & 'price_subtotal'.

        :param price_unit:  The current price unit.
        :param quantity:    The current quantity.
        :param discount:    The current discount.
        :param currency:    The line's currency.
        :param product:     The line's product.
        :param partner:     The line's partner.
        :param taxes:       The applied taxes.
        :param move_type:   The type of the move.
        :return:            A dictionary containing 'price_subtotal' & 'price_total'.
        '''
        res = {}
        # Compute 'price_subtotal'.
        line_discount_price_unit = price_unit * (1 - (discount / 100.0))
        subtotal = quantity * line_discount_price_unit

        # Compute 'price_total'.
        if taxes:
            
        # OVERRIDE >>>
            taxes_res = taxes._origin.with_context(force_sign=1).compute_all(
                line_discount_price_unit,                                                             
                quantity= quantity,
                currency= currency,
                product= product,
                partner= partner,
                is_refund= move_type in ('out_refund', 'in_refund'),
                account_line = line
            )
            
            res['price_subtotal'] = taxes_res['total_excluded']
            res['price_total'] = taxes_res['total_included']
        else:
            res['price_total'] = res['price_subtotal'] = subtotal
            
        # <<< OVERRIDE
        
        #In case of multi currency, round before it's use for computing debit credit
        if currency:
            res = {k: currency.round(v) for k, v in res.items()}
        return res

    @api.model_create_multi
    def create(self, vals_list):
        # OVERRIDE
        # _logger.error(f"[CREATE LINES] ({self.env.company.revatua_ck})")
        # _logger.error(f"[Vals] ({vals_list})")
        # Permet de reprendre le bon PU car dans le cas d'un minimum terrestre ou maritime
        # Odoo recalcul le PU selon la quantités et le total HT
        res = super(AccountMoveLine, self).create(vals_list)
        if self.env.company.revatua_ck:
            for line in res:
                # _logger.warning(f"PU : {line.price_unit} | base {line.base_unit_price}")
                line.write(line._get_price_total_and_subtotal())
                if line.base_unit_price and line.price_unit != line.base_unit_price:
                    line.price_unit = line.base_unit_price
        return res