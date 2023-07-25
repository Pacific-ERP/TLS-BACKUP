# -*- coding: utf-8 -*-
import logging
from odoo import fields, models, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class SaleOrderLineInherit(models.Model):
    _inherit = "sale.order.line"
    
    # Tarif de ventes
    tarif_minimum = fields.Float(string='Prix Minimum', default=0, required=True, store=True)
    
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
    
    # Calcul & check
    r_volume = fields.Float(string='Volume Revatua (m³)', store=True, digits=(12, 3))
    r_weight = fields.Float(string='Volume weight (T)', store=True, digits=(12, 3))
    check_adm = fields.Boolean(string='Payé par ADM', store=True)
    
    def _compute_line_detail(self):
        vals = {}
        return vals
    
    # Calcul des lignes à facturer vu que la quantité est séparer entre
    # facture ADM et Client ne prendre en compte que celle du Client
    @api.depends('invoice_lines.move_id.state', 'invoice_lines.quantity', 'untaxed_amount_to_invoice')
    def _compute_qty_invoiced(self):
        # OVERRIDE
        """
        Compute the quantity invoiced. If case of a refund, the quantity invoiced is decreased. Note
        that this is the case only if the refund is generated from the SO and that is intentional: if
        a refund made would automatically decrease the invoiced quantity, then there is a risk of reinvoicing
        it automatically, which may not be wanted at all. That's why the refund has to be created from the SO
        """
        for line in self:
            qty_invoiced = 0.0
            for invoice_line in line._get_invoice_lines():
                if invoice_line.move_id.state != 'cancel' or invoice_line.move_id.payment_state == 'invoicing_legacy':
                    if invoice_line.move_id.move_type == 'out_invoice':
                        # OVERRIDE >>>
                        if not invoice_line.move_id.is_adm_invoice:
                            qty_invoiced += invoice_line.product_uom_id._compute_quantity(invoice_line.quantity, line.product_uom)
                        # <<< OVERRIDE
                    elif invoice_line.move_id.move_type == 'out_refund':
                        qty_invoiced -= invoice_line.product_uom_id._compute_quantity(invoice_line.quantity, line.product_uom)
            line.qty_invoiced = qty_invoiced
                
    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        # OVERRIDE
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            # OVERRIDE >>>
            # Ajout du discount et du terrestre pour simplifier le calculs des taxes (car taxes s'applique uniquement à la part terrestre)
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_shipping_id, discount=line.discount, terrestre=line.tarif_terrestre, maritime=line.tarif_maritime,rpa = line.tarif_rpa)
            # <<< OVERRIDE
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })
            if self.env.context.get('import_file', False) and not self.env.user.user_has_groups('account.group_account_manager'):
                line.tax_id.invalidate_cache(['invoice_repartition_line_ids'], [line.tax_id.id])
    
    @api.depends('state', 'price_reduce', 'product_id', 'untaxed_amount_invoiced', 'qty_delivered', 'product_uom_qty')
    def _compute_untaxed_amount_to_invoice(self):
        # OVERRIDE
        """ Total of remaining amount to invoice on the sale order line (taxes excl.) as
                total_sol - amount already invoiced
            where Total_sol depends on the invoice policy of the product.

            Note: Draft invoice are ignored on purpose, the 'to invoice' amount should
            come only from the SO lines.
        """
        for line in self:
            amount_to_invoice = 0.0
            if line.state in ['sale', 'done']:
                # Note: do not use price_subtotal field as it returns zero when the ordered quantity is
                # zero. It causes problem for expense line (e.i.: ordered qty = 0, deli qty = 4,
                # price_unit = 20 ; subtotal is zero), but when you can invoice the line, you see an
                # amount and not zero. Since we compute untaxed amount, we can use directly the price
                # reduce (to include discount) without using `compute_all()` method on taxes.
                price_subtotal = 0.0
                uom_qty_to_consider = line.qty_delivered if line.product_id.invoice_policy == 'delivery' else line.product_uom_qty
                price_reduce = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                price_subtotal = price_reduce * uom_qty_to_consider
                if len(line.tax_id.filtered(lambda tax: tax.price_include)) > 0:
                    # As included taxes are not excluded from the computed subtotal, `compute_all()` method
                    # has to be called to retrieve the subtotal without them.
                    # `price_reduce_taxexcl` cannot be used as it is computed from `price_subtotal` field. (see upper Note)
                    # OVERRIDE >>>
                    # Ajout des champs Revatua pour le calcul des taxes
                    price_subtotal = line.tax_id.compute_all(
                        price_reduce,
                        currency=line.order_id.currency_id,
                        quantity=uom_qty_to_consider,
                        product=line.product_id,
                        terrestre = line.tarif_terrestre,
                        maritime = line.tarif_maritime,
                        rpa = line.tarif_rpa,
                        partner=line.order_id.partner_shipping_id)['total_excluded']
                    # <<< OVERRIDE
                inv_lines = line._get_invoice_lines()
                if any(inv_lines.mapped(lambda l: l.discount != line.discount)):
                    # In case of re-invoicing with different discount we try to calculate manually the
                    # remaining amount to invoice
                    amount = 0
                    for l in inv_lines:
                        if len(l.tax_ids.filtered(lambda tax: tax.price_include)) > 0:
                            # OVERRIDE >>>
                            # Ajout des champs Revatua pour le calcul des taxes
                            amount += l.tax_ids.compute_all(l.currency_id._convert(l.price_unit, line.currency_id, line.company_id, l.date or fields.Date.today(), round=False) * l.quantity,terrestre=line.tarif_terrestre,rpa = line.tarif_rpa,)['total_excluded']
                            # <<< OVERRIDE
                        else:
                            amount += l.currency_id._convert(l.price_unit, line.currency_id, line.company_id, l.date or fields.Date.today(), round=False) * l.quantity

                    amount_to_invoice = max(price_subtotal - amount, 0)
                else:
                    amount_to_invoice = price_subtotal - line.untaxed_amount_invoiced

            line.untaxed_amount_to_invoice = amount_to_invoice
            
    @api.onchange('product_id')
    def product_id_change(self):
        # OVERRIDE
        res = super(SaleOrderLineInherit, self).product_id_change()
        # --- Check if revatua is activate ---#
        if self.env.company.revatua_ck:
            vals = {
                'tarif_minimum' : self.product_id.tarif_minimum,
                'check_adm' : self.product_id.check_adm,
                'base_terrestre' : self.product_id.tarif_terrestre,
                'tarif_terrestre' : self.product_id.tarif_terrestre,
                'tarif_minimum_terrestre' : self.product_id.tarif_minimum_terrestre,
                'base_maritime' : self.product_id.tarif_maritime,
                'tarif_maritime' : self.product_id.tarif_maritime,
                'tarif_minimum_maritime' : self.product_id.tarif_minimum_maritime,
                'base_rpa' : self.product_id.tarif_rpa,
                'tarif_rpa_ttc' : self.product_id.tarif_rpa,
                'tarif_rpa' : self.product_id.tarif_rpa,
                'tarif_minimum_rpa' : self.product_id.tarif_minimum_rpa,
            }
            self.write(vals)
        else:
            _logger.error('Revatua not activate : sale_order_line.py -> product_id_change')
        _logger.error(res)
        return res        
    
    # Définie la quantité selon l'unité de mesure utilisé
    @api.onchange('product_uom', 'r_volume', 'r_weight')
    def _onchange_update_qty(self):
        # --- Check if revatua is activated ---#
        if self.env.company.revatua_ck:
            quantity = 1
            
            # Volume weight
            if self.product_uom.name == 'T/m³' and self.r_volume and self.r_weight:
                quantity = round((self.r_volume + self.r_weight) / 2, 3)
            # Tonne
            elif self.product_uom.name == 'T' and self.r_weight:
                quantity = self.r_weight
            # Cubic meter
            elif self.product_uom.name == 'm3' and self.r_volume:
                quantity = self.r_volume

            self.write({
                'product_uom_qty': quantity,
                'product_uom': self.product_id.uom_id if quantity == 1 else self.product_uom,
            })

        else:
            _logger.error('Revatua not activated: account_move_line.py -> _onchange_update_qty')

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
        _logger.error(res)
        return res
        
    # Calcul des part terrestre et maritime selon la quantité et la remise
    @api.onchange('product_uom_qty','discount')
    def _compute_revatua_part(self):
        if self.env.company.revatua_ck:
            for line in self:
                # Remise si existant : remise < 1 sinon = 1
                discount = 1-(line.discount/100)
                quantity = line.product_uom_qty
                line.tarif_terrestre = line._compute_amount_base_revatua(line.base_terrestre, quantity, line.tarif_minimum_terrestre, discount)
                line.tarif_maritime = line._compute_amount_base_revatua(line.base_maritime, quantity, line.tarif_minimum_maritime, discount)
                line.tarif_rpa_ttc = line._compute_amount_base_revatua(line.base_rpa, quantity, line.tarif_minimum_rpa)
                line.tarif_rpa = line._compute_amount_base_revatua(line.base_rpa, quantity, line.tarif_minimum_rpa)
        else:
            _logger.error('Revatua not activate : sale_order_line.py -> _compute_revatua_part')
        
# --------------------------------- Méthode de récupération des champs pour le model -> stock.picking  --------------------------------- #

    def _prepare_procurement_values(self, group_id=False):
        # OVERRIDE
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

# --------------------------------- Méthodes de récupération des champs pour le model -> stock.rule  --------------------------------- #    
    # Méthode de récupération des valeurs pour les stocks
    def _prepare_procurement_values(self, group_id=False):
        # OVERRIDE 
        res = super(SaleOrderLineInherit, self)._prepare_procurement_values(group_id)
        vals = {
            'tarif_rpa' : self.tarif_rpa,
            'tarif_maritime' : self.tarif_maritime,
            'tarif_terrestre' : self.tarif_terrestre,
            'r_volume' : self.r_volume,
            'r_weight' : self.r_weight,
        }
        res.update(vals)
        return res
    
# --------------------------------- Méthodes de récupération des champs pour le model -> account.move  --------------------------------- #

    def _prepare_invoice_line(self,**optional_values):
        # OVERRIDE
        values = super(SaleOrderLineInherit, self)._prepare_invoice_line(**optional_values)
        type = optional_values.get("type", False)
        # Retire le type utiliser pour récupérer le type de lignes à formatté
        # [TO DO] Modifier utiliser le système de contexte plus propre.
        if type:
            values.pop('type')

        values.update({
            'r_volume': self.r_volume,
            'r_weight': self.r_weight,
        })
        # --- Check if revatua is activate ---#
        if self.env.company.revatua_ck:
            values.update({
                'check_adm': self.check_adm,
                'base_qty': self.product_uom_qty,
                'base_unit_price':self.price_unit,
                'base_subtotal':self.price_subtotal,
                'base_rpa':self.base_rpa,
                'base_maritime':self.base_maritime,
                'base_terrestre':self.base_terrestre,
                'base_total':self.price_total,
            })
            if type == 'custo_part':
                tax_custo = self.tax_id.filtered(lambda tax: tax.name != 'RPA').ids if self.tax_id else []
                values.update({
                    'tarif_rpa': 0,
                    'tarif_maritime': 0,
                    'tarif_rpa_ttc': self.tarif_rpa_ttc,
                    'tarif_terrestre': self.tarif_terrestre if self.check_adm else 0,
                    'tax_ids': [(6, 0, tax_custo)]
                })
                
            elif type == 'adm_part':
                tax_adm = self.tax_id.filtered(lambda tax: tax.name == 'RPA').ids if self.tax_id else []
                values.update({
                    'tarif_rpa': self.tarif_rpa,
                    'tarif_rpa_ttc' : self.tarif_rpa_ttc,
                    'tarif_maritime': self.tarif_maritime,
                    'tarif_terrestre': 0,
                    'tax_ids': [(6, 0, tax_adm)]
                })
            
            else: # Ligne normal non ADM
                values.update({
                    'tarif_rpa': self.tarif_rpa,
                    'tarif_maritime': self.tarif_maritime,
                    'tarif_rpa_ttc' : self.tarif_rpa_ttc,
                    'tarif_terrestre': self.tarif_terrestre,
                })

        return values