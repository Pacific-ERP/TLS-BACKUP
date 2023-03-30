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
    @api.onchange('product_uom', 'r_volume', 'r_weight')
    def _onchange_update_qty(self):
        # --- Check if revatua is activated ---#
        if self.env.company.revatua_ck:
            quantity = 1
            
            # Volume weight
            if self.product_uom_id.name == 'T/m³' and self.r_volume and self.r_weight:
                quantity = round((self.r_volume + self.r_weight) / 2, 3)
            # Tonne
            elif self.product_uom_id.name == 'T' and self.r_weight:
                quantity = self.r_weight
            # Cubic meter
            elif self.product_uom_id.name == 'm3' and self.r_volume:
                quantity = self.r_volume

            self.write({
                'quantity': quantity,
                'product_uom_id': self.product_id.uom_id if quantity == 1 else self.product_uom_id,
            })

        else:
            _logger.error('Revatua not activated: account_move_line.py -> _onchange_update_qty')

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

            # Facture ADM ligne adm
            if self.move_id.journal_id.id == 27 and self.product_id.check_adm:
                vals.write({'price_unit': self.product_id.tarif_maritime,
                            'base_terrestre': 0.0,
                            'tarif_terrestre': 0.0,
                            'tarif_minimum_terrestre': 0.0})
                self.move_id.is_adm_invoice = True
            
            # Facture Client ligne adm
            elif self.product_id.check_adm:
                vals.write({'price_unit': self.product_id.tarif_terrestre,
                            'base_maritime': 0.0,
                            'tarif_maritime': 0.0,
                            'tarif_minimum_maritime': 0.0})
                self.move_id.is_adm_invoice = False

            self.write(vals)
   
    # Méthode de calcule pour les tarifs par lignes
    def _compute_amount_base_revatua(self, base=0.0, qty=0.0, mini_amount=0.0, discount=1):
        """ Renvoie le montant de la part (terrestre,maritime,rpa) au changement de quantités

            param float base : Valeur de la base de la part à tester
            param float qty : la quantités
            param discount : 1 - (remise/100) -> si remise existant résultat < 0 sinon 1
            param mini_amount : Minimum que la part peut prendre
        """
        # Effectue une condition ternaire plutôt qu'une instruction if / else 
        res = mini_amount if (mini_amount and ((base * discount) * qty) < mini_amount) else (base * discount) * qty
        return round(res, 0)
        
    # Recalcul des part terrestre et maritime selon la quantité et la remise
    @api.onchange('quantity','discount')
    def _compute_revatua_part(self):
        # --- Check if revatua is activated ---#
        if self.env.company.revatua_ck and self.product_id:
            # Remise si existant : remise < 1 sinon = 1
            discount = 1-(self.discount/100)
            quantity = self.quantity
            rpa = self.env['account.tax'].sudo().search([('name','=','RPA'),('company_id','=',self.env.company.id),('type_tax_use','=','sale')])
            # Ligne ADM
            if self.check_adm:
                # Facture Clients
                if not self.move_id.is_adm_invoice:
                    taxe_ids = self.product_id.taxes_id - rpa
                    self.tarif_terrestre = self._compute_amount_base_revatua(self.base_terrestre, quantity, self.tarif_minimum_terrestre, discount)
                    self.tarif_maritime = 0.0
                    self.tarif_rpa_ttc = 0.0
                    self.tarif_rpa = 0.0
                    self.tax_ids = [(6,0,[taxe_ids.ids])]
                # Facture ADM
                else:
                    self.tarif_maritime = self._compute_amount_base_revatua(self.base_maritime, quantity, self.tarif_minimum_maritime, discount)
                    self.tarif_rpa_ttc = self._compute_amount_base_revatua(self.base_rpa, quantity, self.tarif_minimum_rpa, discount)
                    self.tarif_rpa = self._compute_amount_base_revatua(self.base_rpa, quantity, self.tarif_minimum_rpa, discount)
                    self.tarif_terrestre = 0.0
                    self.tax_ids = [(6,0,[rpa.id])]
            # Ligne normal
            else:
                self.tarif_terrestre = self._compute_amount_base_revatua(self.base_terrestre, quantity, self.tarif_minimum_terrestre, discount)
                self.tarif_maritime = self._compute_amount_base_revatua(self.base_maritime, quantity, self.tarif_minimum_maritime, discount)
                self.tarif_rpa_ttc = self._compute_amount_base_revatua(self.base_rpa, quantity, self.tarif_minimum_rpa, discount)
                self.tarif_rpa = self._compute_amount_base_revatua(self.base_rpa, quantity, self.tarif_minimum_rpa, discount)
        else:
            _logger.error('Revatua not activate : sale_order_line.py -> _compute_revatua_part')
    
    # Recalcul des Totaux pour les lignes ADM (Client et Administration)
    def _get_revatua_totals(self, type, terrestre, maritime, adm, rpa, product):
        _logger.error('----------------------- _get_revatua_totals -----------------------')
        terrestre = round(terrestre, 0) if terrestre else None
        maritime = round(maritime, 0) if maritime else None
        total_excluded = sum(filter(None, [terrestre, maritime]))
        totals_tax = 0.0
        # Calcul des taxes
        if product.taxes_id:
            for tax in product.taxes_id:
                if 'CPS' in tax.name:
                    totals_tax += math.ceil(terrestre * (tax.amount/100))
                elif 'RPA' in tax.name:
                    totals_tax += rpa
                else:
                    totals_tax += round(terrestre * (tax.amount/100), 0)
                        
        if adm and maritime:
            total_included = maritime + rpa if rpa else 0.0
        elif product.check_adm and terrestre:
            total_included = total_excluded + totals_tax
        else:
            total_included = total_excluded + totals_tax
        
        _logger.error('HT : %s' % total_excluded if type == 'excluded' else 'TTC : %s' % total_included)
        return round(total_excluded, 0) if type == 'excluded' else round(total_included, 0)
        
    def _get_price_total_and_subtotal(self, price_unit=None, quantity=None, discount=None, currency=None, product=None, partner=None, taxes=None, move_type=None, terrestre=None, maritime=None, adm=None, rpa=None, type=None):
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
            # Ajout des champs Revatua
            terrestre=self.tarif_terrestre if terrestre is None else terrestre,
            maritime=self.tarif_maritime if maritime is None else maritime,
            adm=self.move_id.is_adm_invoice if adm is None else adm,
            rpa=self.tarif_rpa if rpa is None else rpa,
        )
    
    @api.model
    def _get_price_total_and_subtotal_model(self, price_unit, quantity, discount, currency, product, partner, taxes, move_type, terrestre=None, maritime=None, adm=None, rpa=None):
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
        # OVERRIDE >>>
        # ----- Modification du prix unitaire pour chaque état possible d'une facture Aremiti ----- #
        if self.env.company.revatua_ck:
            # Facture ADM administration
            if self.move_id.is_adm_invoice:
                price_unit = self.base_maritime
            # Facture ADM client
            elif not self.tarif_maritime and self.tarif_terrestre:
                price_unit = self.base_terrestre
            # Facture Aremiti normal
            elif self.tarif_maritime and self.tarif_terrestre:
                price_unit = self.base_maritime + self.base_terrestre
            # Facture normal
            else:
                price_unit = price_unit
        # <<< OVERRIDE 
                
        # Compute 'price_subtotal'.
        line_discount_price_unit = price_unit * (1 - (discount / 100.0))
        subtotal = quantity * line_discount_price_unit

        # Compute 'price_total'.
        if taxes:
        # OVERRIDE >>>
        # ----- Ajout du discount et du terrestre pour simplifier le calculs des taxes (car taxes s'applique uniquement à la part terrestre) ----- #
            if self.env.company.revatua_ck and self.move_id.move_type in ('out_invoice','out_refund'):
                taxes_res = taxes._origin.with_context(force_sign=1).compute_all(line_discount_price_unit,
                quantity=quantity, currency=currency, product=product, partner=partner, is_refund=move_type in ('out_refund', 'in_refund'), terrestre=terrestre, maritime=maritime, adm=adm, discount=discount, rpa=rpa)
                taxes_res['total_excluded'] = self._get_revatua_totals('excluded', terrestre, maritime, adm, rpa, product)
                taxes_res['total_included'] = self._get_revatua_totals('included', terrestre, maritime, adm, rpa, product)
            else:
                taxes_res = taxes._origin.with_context(force_sign=1).compute_all(line_discount_price_unit,
                quantity=quantity, currency=currency, product=product, partner=partner, is_refund=move_type in ('out_refund', 'in_refund'))
            res['price_subtotal'] = taxes_res['total_excluded']
            res['price_total'] = taxes_res['total_included']
        else:
            res['price_total'] = res['price_subtotal'] = subtotal
        # <<< OVERRIDE
        
        #In case of multi currency, round before it's use for computing debit credit
        if currency:
            res = {k: currency.round(v) for k, v in res.items()}
        return res
        
    # Méthode de récupération des champs du model : account.admg
    def _prepare_line_admg(self, sequence=1):
        self.ensure_one()
        rpa = self.env['account.tax'].sudo().search([('name','=','RPA'),('company_id','=', self.env.company.id),('type_tax_use','=','sale')])
        vals = {
            'sequence': sequence,
            'display_type': self.display_type,
            'product_id': self.product_id,
            'r_volume': self.r_volume,
            'r_weight': self.r_weight,
            'quantity': self.quantity,
            'price_subtotal': self.price_subtotal,
            'tax_id': [(6,0,[rpa.id])],
            'price_unit': self.price_unit,
            'tarif_terrestre': self.tarif_terrestre,
            'tarif_maritime': self.tarif_maritime,
            'tarif_rpa': self.tarif_rpa,
            'price_total': self.price_total,
        }
        return vals