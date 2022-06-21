# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.tools.float_utils import float_round as round
import logging
import math

_logger = logging.getLogger(__name__)

class AccountTaxInherit(models.Model):
    _inherit = "account.tax"
    
    def _compute_amount(self, base_amount, price_unit, quantity=1.0, product=None, partner=None, invoice=None):
        #########################
        #### OVERRIDE METHOD ####
        #########################
        self.ensure_one()
        if self.amount_type == 'fixed':
            if base_amount:
                
                #############################################################################################################################
                #==================================#
                #=============OVERRIDE=============#
                #========================================================================#
                # --- Check if revatua is activate ---#
                if self.name == 'RPA' and product.tarif_rpa > 0:
                    return math.copysign(quantity, base_amount) * product.tarif_rpa
                else:
                    return math.copysign(quantity, base_amount) * self.amount
                #========================================================================#
                #=============OVERRIDE=============#
                #==================================#
                #############################################################################################################################
            else:
                return quantity * self.amount

        price_include = self._context.get('force_price_include', self.price_include)
        # base * (1 + tax_amount) = new_base
        if self.amount_type == 'percent' and not price_include:
            
            #############################################################################################################################
            #==================================#
            #=============OVERRIDE=============#
            #========================================================================#
            # --- Check if revatua is activate ---#
            # La taxe s'applique que à la part Terrestre base_amount = montant HT multilier par 0.6 pour obtenir la part terrestre
            if product.tarif_terrestre and product.tarif_terrestre > 0:
                base_amount = base_amount * 0.6
                ## Arrondis down pour la CPS uniquement
                if 'CPS' in self.name and self.env.company.id == 2:
                    return math.floor(base_amount * self.amount / 100)
                else:
                    return base_amount * self.amount / 100
            else:
                return base_amount * self.amount / 100
            #========================================================================#
            #=============OVERRIDE=============#
            #==================================#
            #############################################################################################################################

        # <=> new_base = base / (1 + tax_amount)
        if self.amount_type == 'percent' and price_include:
            return base_amount - (base_amount / (1 + self.amount / 100))
        # base / (1 - tax_amount) = new_base
        if self.amount_type == 'division' and not price_include:
            return base_amount / (1 - self.amount / 100) - base_amount if (1 - self.amount / 100) else 0.0
        # <=> new_base * (1 - tax_amount) = base
        if self.amount_type == 'division' and price_include:
            return base_amount - (base_amount * (self.amount / 100))
        # default value for custom amount_type
        return 0.0