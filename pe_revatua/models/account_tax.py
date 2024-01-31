# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.tools.float_utils import float_round as round
import logging
import math

_logger = logging.getLogger(__name__)

class AccountTaxInherit(models.Model):
    _inherit = "account.tax"
    
    # Ajout du paramètre terrestre pour le calcul de la taxe
    def _compute_amount(self, base_amount, price_unit, quantity=1.0, product=None, partner=None, invoice=None, terrestre=0, discount=0, rpa=0, line=None):
        # OVERRIDE
        _logger.error(f"[Taxe] : {self.name}")
        
        maritime = terrestre = rpa = 0.0
        adm = False
        
        if line:
            terrestre = line.tarif_terrestre
            maritime = line.tarif_maritime
            rpa = line.tarif_rpa if not line.check_adm else 0.0 # Part ADM non payé par le client
            adm = line.check_adm
            
        _logger.warning(f"Terrestre : {terrestre} | maritime : {maritime} | RPA : {rpa} | Line : {line} | adm : {adm}")
        
        self.ensure_one()
        if self.amount_type == 'fixed': # Taxes type fixed (RPA)
            if base_amount:
                # OVERRIDE >>>
                # --- Check if revatua is activate ---#
                if terrestre and self.name == 'RPA' and rpa:
                    # Si un coût minimum RPA est configuré et que le total RPA(qty*rpa) et inférieur au minimum RPA
                    if product.tarif_minimum_rpa and math.copysign(quantity, rpa) < product.tarif_minimum_rpa:
                        return product.tarif_minimum_rpa
                    else:
                        return rpa
                else:
                    return math.copysign(quantity, base_amount) * self.amount
                # <<< OVERRIDE
            else:
                return quantity * self.amount

        price_include = self._context.get('force_price_include', self.price_include)
        # base * (1 + tax_amount) = new_base
        if self.amount_type == 'percent' and not price_include: # Taxes type ratio (13% & CPS)
            # OVERRIDE >>>
            # --- Check if revatua is activate ---#
            # La taxe s'applique que à la part Terrestre
            if terrestre or rpa:
                base_amount = round(terrestre, 0)
                # Arrondis down pour la CPS uniquement
                if 'CPS' in self.name:
                    #('if cps') arrondi haut cps
                    cps_terrestre = math.ceil(base_amount * self.amount / 100)
                    # # _logger.error('CPS terrestre %s '% cps_terrestre)
                    return cps_terrestre
                else:
                    return base_amount * self.amount / 100
            else:
                return base_amount * self.amount / 100
            # <<< OVERRIDE

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

# --------------------------------- Modification des méthode de calculs des taxes et sous totaux  --------------------------------- #
    
    def compute_all(self, price_unit, currency=None, quantity=1.0, product=None, partner=None, is_refund=False, handle_price_include=True, include_caba_tags=False, discount=0.0, terrestre=0, maritime=0, adm=False, rpa=0, account_line=None, order_line=None):
        """ Returns all information required to apply taxes (in self + their children in case of a tax group).
            We consider the sequence of the parent for group of taxes.
                Eg. considering letters as taxes and alphabetic order as sequence :
                [G, B([A, D, F]), E, C] will be computed as [A, D, F, C, E, G]

            'handle_price_include' is used when we need to ignore all tax included in price. If False, it means the
            amount passed to this method will be considered as the base of all computations.

        RETURN: {
            'total_excluded': 0.0,    # Total without taxes
            'total_included': 0.0,    # Total with taxes
            'total_void'    : 0.0,    # Total with those taxes, that don't have an account set
            'taxes': [{               # One dict for each tax in self and their children
                'id': int,
                'name': str,
                'amount': float,
                'sequence': int,
                'account_id': int,
                'refund_account_id': int,
                'analytic': boolean,
            }],
        } """

        
        # OVERRIDE >>>

        
        taxes_name = ", ".join(tax.name for tax in self) if self else ""
        # Permet de récupéré la ligne de vente ou de facturation pour recalcul des taxes plus facilements
        line = adm = False
        terrestre = maritime = rpa = 0.0
        
        if order_line: # Ventes
            # _logger.warning(f"Tax Ventes : order_line = {order_line}")
            line = order_line
        if account_line: # Factures
            # _logger.warning(f"Tax Factures : account_line = {account_line}")
            line = account_line
        
        _logger.error(f"##### [Totaux Taxes] {line.product_id.name if line else 'None'} : {taxes_name} | {line} | context : {self.env.context}#####")
        
        if not self:
            company = self.env.company
        else:
            company = self[0].company_id

        _logger.warning(f"Default company : {company} | Revatua : {company.revatua_ck} ")

        
        # <<< OVERRIDE

        
        taxes, groups_map = self.flatten_taxes_hierarchy(create_map=True)
        if not currency:
            currency = company.currency_id
        prec = currency.rounding
        round_tax = False if company.tax_calculation_rounding_method == 'round_globally' else True
        if 'round' in self.env.context:
            round_tax = bool(self.env.context['round'])

        if not round_tax:
            prec *= 1e-5

        def recompute_base(base_amount, fixed_amount, percent_amount, division_amount):
            return (base_amount - fixed_amount) / (1.0 + percent_amount / 100.0) * (100 - division_amount) / 100

        base = currency.round(price_unit * quantity)
        sign = 1
        if currency.is_zero(base):
            sign = self._context.get('force_sign', 1)
        elif base < 0:
            sign = -1
        if base < 0:
            base = -base
            
        total_included_checkpoints = {}
        i = len(taxes) - 1
        store_included_tax_total = True
        # Keep track of the accumulated included fixed/percent amount.
        incl_fixed_amount = incl_percent_amount = incl_division_amount = 0
        # Store the tax amounts we compute while searching for the total_excluded
        cached_tax_amounts = {}
        if handle_price_include:
            for tax in reversed(taxes):
                tax_repartition_lines = (
                    is_refund
                    and tax.refund_repartition_line_ids
                    or tax.invoice_repartition_line_ids
                ).filtered(lambda x: x.repartition_type == "tax")
                sum_repartition_factor = sum(tax_repartition_lines.mapped("factor"))

                if tax.include_base_amount:
                    base = recompute_base(base, incl_fixed_amount, incl_percent_amount, incl_division_amount)
                    #('base 3nd compute : %s' % base)
                    incl_fixed_amount = incl_percent_amount = incl_division_amount = 0
                    store_included_tax_total = True
                if tax.price_include or self._context.get('force_price_include'):
                    if tax.amount_type == 'percent':
                        incl_percent_amount += tax.amount * sum_repartition_factor
                    elif tax.amount_type == 'division':
                        incl_division_amount += tax.amount * sum_repartition_factor
                    elif tax.amount_type == 'fixed':
                        incl_fixed_amount += abs(quantity) * tax.amount * sum_repartition_factor
                    else:
                        # tax.amount_type == other (python)
                        ########################################################################
                        ### 1 - Ajout de la remise pour le calcul de taxe + champs terrestre ###
                        ########################################################################
                        # soucis lors de l'éxé qui est pas bon et ce fait sur plusieurs société donc rentre pas dans le if pas d'idée (donc self.env.company.revatua_ck fonctionne pas)
                        if company.revatua_ck:
                            tax_amount = tax._compute_amount(base, sign * price_unit,
                                                             quantity,
                                                             product,
                                                             partner,
                                                             line= line,
                                                            ) * sum_repartition_factor
                        else:
                            tax_amount = tax._compute_amount(base, sign * price_unit, quantity, product, partner) * sum_repartition_factor
                        ########################################################################
                        ### 1 - Ajout de la remise pour le calcul de taxe + champs terrestre ###
                        ########################################################################
                        incl_fixed_amount += tax_amount
                        # Avoid unecessary re-computation
                        cached_tax_amounts[i] = tax_amount
                    # In case of a zero tax, do not store the base amount since the tax amount will
                    # be zero anyway. Group and Python taxes have an amount of zero, so do not take
                    # them into account.
                    if store_included_tax_total and (
                        tax.amount or tax.amount_type not in ("percent", "division", "fixed")
                    ):
                        total_included_checkpoints[i] = base
                        store_included_tax_total = False
                i -= 1
        total_excluded = currency.round(recompute_base(base, incl_fixed_amount, incl_percent_amount, incl_division_amount))

        # OVERRIDE >>>

        if line and company.revatua_ck:
            pv_terrestre = pv_maritime = 0.0
            
            # Part Terrestre
            if line.tarif_terrestre:
                pv_terrestre = line.tarif_terrestre
                # Minimum Terrestre
                if line.tarif_minimum_terrestre and line.tarif_terrestre < line.tarif_minimum_terrestre:
                    pv_terrestre = line.tarif_minimum_terrestre

            # Part Maritime
            if line.tarif_maritime:
                pv_maritime = line.tarif_maritime
                # Minimum Maritime
                if line.tarif_minimum_maritime and line.tarif_maritime < line.tarif_minimum_maritime:
                    pv_maritime = line.tarif_minimum_maritime

            if pv_terrestre or pv_maritime: # Produit avec part Maritime ou Terrestre
                
                # HT Produit non ADM = Terrestre + Maritime
                if not line.check_adm: 
                    _logger.warning(f"IF")
                    total_excluded = pv_terrestre + pv_maritime
                # HT Produit ADM 100% Maritime
                # elif line.check_adm and pv_maritime and not pv_terrestre:
                #     _logger.warning(f"ELIF")
                #     total_excluded = pv_maritime
                # HT Produit ADM = Terrestre
                else:
                    _logger.warning(f"ELSE")
                    total_excluded = pv_terrestre
        
        # <<< OVERRIDE

        # 4) Iterate the taxes in the sequence order to compute missing tax amounts.
        # Start the computation of accumulated amounts at the total_excluded value.
        base = total_included = total_void = total_excluded
        #('Total TTC 1 : %s' % total_included)
        # Flag indicating the checkpoint used in price_include to avoid rounding issue must be skipped since the base
        # amount has changed because we are currently mixing price-included and price-excluded include_base_amount
        # taxes.
        skip_checkpoint = False

        # Get product tags, account.account.tag objects that need to be injected in all
        # the tax_tag_ids of all the move lines created by the compute all for this product.
        product_tag_ids = product.account_tag_ids.ids if product else []

        taxes_vals = []
        i = 0
        cumulated_tax_included_amount = 0
        for tax in taxes:
            price_include = self._context.get('force_price_include', tax.price_include)

            if price_include or tax.is_base_affected:
                tax_base_amount = base
            else:
                tax_base_amount = total_excluded

            tax_repartition_lines = (is_refund and tax.refund_repartition_line_ids or tax.invoice_repartition_line_ids).filtered(lambda x: x.repartition_type == 'tax')
            sum_repartition_factor = sum(tax_repartition_lines.mapped('factor'))

            #compute the tax_amount
            if not skip_checkpoint and price_include and total_included_checkpoints.get(i) is not None and sum_repartition_factor != 0:
                # We know the total to reach for that tax, so we make a substraction to avoid any rounding issues
                tax_amount = total_included_checkpoints[i] - (base + cumulated_tax_included_amount)
                cumulated_tax_included_amount = 0
            else:

                
            # OVERRIDE >>>
                
                if company.revatua_ck:
                    tax_amount = tax.with_context(force_price_include=False)._compute_amount(
                        tax_base_amount,
                        sign * price_unit,
                        quantity,
                        product,
                        partner,
                        line=line,
                    )
                    
                else:
                    tax_amount = tax.with_context(force_price_include=False)._compute_amount(tax_base_amount, sign * price_unit, quantity, product, partner)
            
            # <<< OVERRIDE

            
            # Round the tax_amount multiplied by the computed repartition lines factor.
            tax_amount = round(tax_amount, precision_rounding=prec)
            factorized_tax_amount = round(tax_amount * sum_repartition_factor, precision_rounding=prec)

            if price_include and total_included_checkpoints.get(i) is None:
                cumulated_tax_included_amount += factorized_tax_amount

            # If the tax affects the base of subsequent taxes, its tax move lines must
            # receive the base tags and tag_ids of these taxes, so that the tax report computes
            # the right total
            subsequent_taxes = self.env['account.tax']
            subsequent_tags = self.env['account.account.tag']
            if tax.include_base_amount:
                subsequent_taxes = taxes[i+1:].filtered('is_base_affected')

                taxes_for_subsequent_tags = subsequent_taxes

                if not include_caba_tags:
                    taxes_for_subsequent_tags = subsequent_taxes.filtered(lambda x: x.tax_exigibility != 'on_payment')

                subsequent_tags = taxes_for_subsequent_tags.get_tax_tags(is_refund, 'base')

            # Compute the tax line amounts by multiplying each factor with the tax amount.
            # Then, spread the tax rounding to ensure the consistency of each line independently with the factorized
            # amount. E.g:
            #
            # Suppose a tax having 4 x 50% repartition line applied on a tax amount of 0.03 with 2 decimal places.
            # The factorized_tax_amount will be 0.06 (200% x 0.03). However, each line taken independently will compute
            # 50% * 0.03 = 0.01 with rounding. It means there is 0.06 - 0.04 = 0.02 as total_rounding_error to dispatch
            # in lines as 2 x 0.01.
            repartition_line_amounts = [round(tax_amount * line.factor, precision_rounding=prec) for line in tax_repartition_lines]
            total_rounding_error = round(factorized_tax_amount - sum(repartition_line_amounts), precision_rounding=prec)
            nber_rounding_steps = int(abs(total_rounding_error / currency.rounding))
            rounding_error = round(nber_rounding_steps and total_rounding_error / nber_rounding_steps or 0.0, precision_rounding=prec)

            for repartition_line, line_amount in zip(tax_repartition_lines, repartition_line_amounts):

                if nber_rounding_steps:
                    line_amount += rounding_error
                    nber_rounding_steps -= 1

                if not include_caba_tags and tax.tax_exigibility == 'on_payment':
                    repartition_line_tags = self.env['account.account.tag']
                else:
                    repartition_line_tags = repartition_line.tag_ids

                taxes_vals.append({
                    'id': tax.id,
                    'name': partner and tax.with_context(lang=partner.lang).name or tax.name,
                    'amount': sign * line_amount,
                    'base': round(sign * tax_base_amount, precision_rounding=prec),
                    'sequence': tax.sequence,
                    'account_id': tax.cash_basis_transition_account_id.id if tax.tax_exigibility == 'on_payment' else repartition_line.account_id.id,
                    'analytic': tax.analytic,
                    'price_include': price_include,
                    'tax_exigibility': tax.tax_exigibility,
                    'tax_repartition_line_id': repartition_line.id,
                    'group': groups_map.get(tax),
                    'tag_ids': (repartition_line_tags + subsequent_tags).ids + product_tag_ids,
                    'tax_ids': subsequent_taxes.ids,
                })

                if not repartition_line.account_id:
                    total_void += line_amount

            # Affect subsequent taxes
            if tax.include_base_amount:
                base += factorized_tax_amount
                if not price_include:
                    skip_checkpoint = True
            total_included += factorized_tax_amount
            i += 1
        
        base_taxes_for_tags = taxes
        if not include_caba_tags:
            base_taxes_for_tags = base_taxes_for_tags.filtered(lambda x: x.tax_exigibility != 'on_payment')

        base_rep_lines = base_taxes_for_tags.mapped(is_refund and 'refund_repartition_line_ids' or 'invoice_repartition_line_ids').filtered(lambda x: x.repartition_type == 'base')

        # Override
        vals = {
            'base_tags': base_rep_lines.tag_ids.ids + product_tag_ids,
            'taxes': taxes_vals,
            'total_excluded': sign * total_excluded,
            'total_included': sign * currency.round(total_included),
            'total_void': sign * currency.round(total_void),
        }
        _logger.warning(f" Total HT : {(sign * total_excluded)} | Total TTC : {sign * currency.round(total_included)} ")
        return vals