# -*- coding: utf-8 -*-
import logging
import json
from odoo import fields, models, api
from odoo.tools import float_is_zero
from itertools import groupby

_logger = logging.getLogger(__name__)

class SaleOrderInherit(models.Model):
    _inherit = "sale.order"
    
    # Vérification si la coche Revatua est activé
    revatua_ck = fields.Boolean(string="Mode Revatua", related="company_id.revatua_ck")
    
    #Lieu Livraison
    commune_recup = fields.Many2one(string='Commune de récupération',comodel_name='res.commune')
    ile_recup = fields.Char(string='Île de récupération', related='commune_recup.ile_id.name', store=True)
    contact_expediteur = fields.Many2one(string='Contact expéditeur',comodel_name='res.partner')
    tel_expediteur = fields.Char(string='Téléphone expéditeur', related='contact_expediteur.phone', store=True)
    mobil_expediteur = fields.Char(string='Mobile expéditeur', related='contact_expediteur.mobile', store=True)
    
    # Lieu destinataire
    commune_dest = fields.Many2one(string='Commune de destination',comodel_name='res.commune')
    ile_dest = fields.Char(string='Île de destination', related='commune_dest.ile_id.name', store=True)
    contact_dest = fields.Many2one(string='Contact de destination',comodel_name='res.partner')
    tel_dest = fields.Char(string='Téléphone destinataire', related='contact_dest.phone', store=True)
    mobil_dest = fields.Char(string='Mobile destinataire', related='contact_dest.mobile', store=True)
                
    # Maritime
    sum_adm = fields.Monetary(string="Montant ADM", store=True, help="La part qui sera payé par l'administration")
    sum_customer = fields.Monetary(string="Montant Client", store=True, help="La part qui sera payé par le client")
    
    # Calcul des parts client et ADM
    @api.onchange('order_line')
    def _total_tarif(self):
        # --- Check if revatua is activated ---#
        if self.env.company.revatua_ck:
            sum_customer = 0
            sum_adm = 0
            
            for line in self.order_line:
                taxes = sum(tax.amount/100 for tax in line.tax_id)
                if line.check_adm:
                    sum_adm += round(line.tarif_maritime, 0) + round(line.tarif_rpa_ttc, 0)
                    sum_customer += line.tarif_terrestre + (line.price_tax - line.tarif_rpa_ttc) 
                else:
                    sum_customer += line.price_total

            self.write({'sum_adm': sum_adm, 'sum_customer' : sum_customer})
        else:
            _logger.error('Revatua not activate : sale_order.py -> _total_tarif')
            
    @api.depends('order_line.tax_id', 'order_line.price_unit', 'amount_total', 'amount_untaxed')
    def _compute_tax_totals_json(self):
        # OVERRIDE
        def compute_taxes(order_line):
            price = order_line.price_unit * (1 - (order_line.discount or 0.0) / 100.0)
            order = order_line.order_id
            # Ajout des champs Revatua au compute_all pour récupéré les bon totaux
            return order_line.tax_id._origin.compute_all(price, order.currency_id, order_line.product_uom_qty, product=order_line.product_id, partner=order.partner_shipping_id, discount=order_line.discount,terrestre=order_line.tarif_terrestre, maritime=order_line.tarif_maritime, rpa=order_line.tarif_rpa)

        account_move = self.env['account.move']
        for order in self:
            tax_lines_data = account_move._prepare_tax_lines_data_for_totals_from_object(order.order_line, compute_taxes)
            tax_totals = account_move._get_tax_totals(order.partner_id, tax_lines_data, order.amount_total, order.amount_untaxed, order.currency_id)
            order.tax_totals_json = json.dumps(tax_totals)
    
    #------------------------------------------------------------------------------------------------------------------------------------------#
    #                                                    Modification Création d'une Facture (Override)                                        #
    #------------------------------------------------------------------------------------------------------------------------------------------#
    
    # Méthode de préparation des champs pour la facture
    def _prepare_invoice(self):
        # OVERRIDE
        invoice_vals = super(SaleOrderInherit,self)._prepare_invoice()
        # --- Check if revatua is activate ---#
        if self.env.company.revatua_ck:
            invoice_vals.update({
                'sum_adm': self.sum_adm,
                'sum_customer': self.sum_customer,
                'commune_recup': self.commune_recup,
                'contact_expediteur': self.contact_expediteur,
                'commune_dest': self.commune_dest,
                'contact_dest': self.contact_dest,
                'invoice_line_ids': [],
            })
        else:
            _logger.error('Revatua not activate : sale_order.py -> _prepare_invoice')
        return invoice_vals

    def _create_invoices(self, grouped=False, final=False, date=None):
        # OVERRIDE
        """
        Create the invoice associated to the SO.
        :param grouped: if True, invoices are grouped by SO id. If False, invoices are grouped by
                        (partner_invoice_id, currency)
        :param final: if True, refunds will be generated if necessary
        :returns: list of created invoices
        """
        _logger.error('######################################################### Création de facture #########################################################')
        if not self.env['account.move'].check_access_rights('create', False):
            try:
                self.check_access_rights('write')
                self.check_access_rule('write')
            except AccessError:
                return self.env['account.move']

        # 1) Create invoices.
        # OVERRIDE >>>
        # [] : Variable qui regroupe la liste des factures adm
        invoice_vals_list_adm = []
        # <<< OVERRIDE
        
        invoice_vals_list = []
        invoice_item_sequence = 0 # Incremental sequencing to keep the lines order on the invoice.
        for order in self:
            
            order = order.with_company(order.company_id)
            current_section_vals = None
            down_payments = order.env['sale.order.line']
            
            invoice_vals = order._prepare_invoice()
            invoiceable_lines = order._get_invoiceable_lines(final)

            if not any(not line.display_type for line in invoiceable_lines):
                continue
            invoice_line_vals = []
            down_payment_section_added = False
            
            # OVERRIDE >>>
            # Variable Revatua
            journal_adm = self.env['account.journal'].sudo().search([('name','=','Facture ADM'),('company_id','=', order.company_id.id)])
            invoice_line_vals_adm = []
            invoice_line_vals_no_adm = []
            # <<< OVERRIDE
            
            for line in invoiceable_lines:
                if not down_payment_section_added and line.is_downpayment:
                    # Create a dedicated section for the down payments
                    # (put at the end of the invoiceable_lines)
                    invoice_line_vals.append(
                        (0, 0, order._prepare_down_payment_section_line(
                            sequence=invoice_item_sequence,
                        )),
                    )
                    down_payment_section_added = True
                    invoice_item_sequence += 1
                    
                # OVERRIDE >>>
                # --- Check if revatua is activate ---#
                if self.env.company.revatua_ck:
                    # Si article ADM
                    if line.check_adm:
                        invoice_line_vals_no_adm.append((0, 0, line._prepare_invoice_line(sequence=invoice_item_sequence, type="custo_part")),)
                        invoice_line_vals_adm.append((0, 0, line._prepare_invoice_line(sequence=invoice_item_sequence, type="adm_part")),)
                        if line.product_id.contact_adm:
                            # Si une facture adm existe déjà pour ce département rajouter la ligne à la liste
                            if any(adm_invoice.get('partner_id') == line.product_id.contact_adm for adm_invoice in invoice_vals_list_adm):
                                # ajouter la ligne d'article au liste d'articles et cumulé à la liste des facture adm
                                adm_invoice = list(filter(lambda x: x['partner_id'].id == line.product_id.contact_adm.id, invoice_vals_list_adm))[1]
                                adm_invoice['invoice_line_ids'].append((0, 0, line._prepare_invoice_line(sequence=invoice_item_sequence, type="adm_part")),)
                            # Sinon ajouter une facture à la liste avec le bon client
                            else:
                                invoice_sub = order._prepare_invoice()
                                invoice_sub.update({
                                    'partner_id': line.product_id.contact_adm.id,
                                    'partner_shipping_id': line.product_id.contact_adm,
                                    'is_adm_invoice':True,
                                    'journal_id':journal_adm.id,
                                })
                                invoice_sub['invoice_line_ids'].append((0, 0, line._prepare_invoice_line(sequence=invoice_item_sequence, type="adm_part")),)
                                invoice_vals_list_adm.append(invoice_sub)
                    else:
                        invoice_line_vals.append((0, 0, line._prepare_invoice_line(sequence=invoice_item_sequence,)),)
                else:
                    _logger.error('Revatua not activate : sale_order.py -> _create_invoices 2')
                    invoice_line_vals.append((0, 0, line._prepare_invoice_line(sequence=invoice_item_sequence,)),)
                # <<< OVERRIDE
                
                invoice_item_sequence += 1
            
            invoice_vals['invoice_line_ids'] += invoice_line_vals
            
            # OVERRIDE >>>
            # --- Check if revatua is activate ---#
            if self.env.company.revatua_ck:
                # Facture adm partie client
                invoice_vals['invoice_line_ids'] += invoice_line_vals_no_adm
            else:
                _logger.error('Revatua not activate : sale_order.py -> _create_invoices 3')
            # <<< OVERRIDE
            
            invoice_vals_list.append(invoice_vals)
            # OVERRIDE >>>
            # --- Check if revatua is activate ---#
            if self.env.company.revatua_ck:
                # Facture adm partie client
                invoice_vals_list += invoice_vals_list_adm
            else:
                _logger.error('Revatua not activate : sale_order.py -> _create_invoices 4')
            # <<< OVERRIDE
        if not invoice_vals_list:
            raise self._nothing_to_invoice_error()

        # 2) Manage 'grouped' parameter: group by (partner_id, currency_id).
        if not grouped:
            new_invoice_vals_list = []
            invoice_grouping_keys = self._get_invoice_grouping_keys()
            invoice_vals_list = sorted(
                invoice_vals_list,
                key=lambda x: [
                    x.get(grouping_key) for grouping_key in invoice_grouping_keys
                ]
            )
            for grouping_keys, invoices in groupby(invoice_vals_list, key=lambda x: [x.get(grouping_key) for grouping_key in invoice_grouping_keys]):
                origins = set()
                payment_refs = set()
                refs = set()
                ref_invoice_vals = None
                for invoice_vals in invoices:
                    if not ref_invoice_vals:
                        ref_invoice_vals = invoice_vals
                    else:
                        ref_invoice_vals['invoice_line_ids'] += invoice_vals['invoice_line_ids']
                    origins.add(invoice_vals['invoice_origin'])
                    payment_refs.add(invoice_vals['payment_reference'])
                    refs.add(invoice_vals['ref'])
                ref_invoice_vals.update({
                    'ref': ', '.join(refs)[:2000],
                    'invoice_origin': ', '.join(origins),
                    'payment_reference': len(payment_refs) == 1 and payment_refs.pop() or False,
                })
                new_invoice_vals_list.append(ref_invoice_vals)
            invoice_vals_list = new_invoice_vals_list
            
        # 3) Create invoices.

        # As part of the invoice creation, we make sure the sequence of multiple SO do not interfere
        # in a single invoice. Example:
        # SO 1:
        # - Section A (sequence: 10)
        # - Product A (sequence: 11)
        # SO 2:
        # - Section B (sequence: 10)
        # - Product B (sequence: 11)
        #
        # If SO 1 & 2 are grouped in the same invoice, the result will be:
        # - Section A (sequence: 10)
        # - Section B (sequence: 10)
        # - Product A (sequence: 11)
        # - Product B (sequence: 11)
        #
        # Resequencing should be safe, however we resequence only if there are less invoices than
        # orders, meaning a grouping might have been done. This could also mean that only a part
        # of the selected SO are invoiceable, but resequencing in this case shouldn't be an issue.
        if len(invoice_vals_list) < len(self):
            SaleOrderLine = self.env['sale.order.line']
            for invoice in invoice_vals_list:
                sequence = 1
                for line in invoice['invoice_line_ids']:
                    line[2]['sequence'] = SaleOrderLine._get_invoice_line_sequence(new=sequence, old=line[2]['sequence'])
                    sequence += 1
                    
        # Manage the creation of invoices in sudo because a salesperson must be able to generate an invoice from a
        # sale order without "billing" access rights. However, he should not be able to create an invoice from scratch.
        moves = self.env['account.move'].sudo().with_context(default_move_type='out_invoice').create(invoice_vals_list)
        
        # 4) Some moves might actually be refunds: convert them if the total amount is negative
        # We do this after the moves have been created since we need taxes, etc. to know if the total
        # is actually negative or not
        if final:
            moves.sudo().filtered(lambda m: m.amount_total < 0).action_switch_invoice_into_refund_credit_note()
        for move in moves:
            move.message_post_with_view('mail.message_origin_link',
                values={'self': move, 'origin': move.line_ids.mapped('sale_line_ids.order_id')},
                subtype_id=self.env.ref('mail.mt_note').id
            )
            # OVERRIDE >>>
            # --- Check if revatua is activate ---#
            # Recalculer les totaux car utilisation d'une méthode à la création qui foire les totaux à la création
            if self.env.company.revatua_ck:
                for line in move.invoice_line_ids:
                    line._get_price_total_and_subtotal()
                    _logger.error('RPA %s'% line.tarif_rpa)
                    # Vérification si c'est une ligne avec part terrestre ou maritime sinon pass
                    if line.tarif_terrestre or line.tarif_maritime:
                        line['price_subtotal'] = line._get_revatua_totals('excluded', line.tarif_terrestre, line.tarif_maritime, line.check_adm, line.tarif_rpa, line.product_id)
                        line['price_total'] = line._get_revatua_totals('included', line.tarif_terrestre, line.tarif_maritime, line.check_adm, line.tarif_rpa, line.product_id)
            # <<< OVERRIDE
        return moves