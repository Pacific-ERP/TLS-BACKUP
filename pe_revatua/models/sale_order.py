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

    pe_attachment_ids = fields.Many2many(
        string="Bon de livraison",
        context={'default_public': True},
        comodel_name='ir.attachment',
        help="Bon de Livraison.",
    )

    # Maritime
    sum_adm = fields.Monetary(string="Montant ADM", store=True, help="La part qui sera payé par l'administration")
    sum_customer = fields.Monetary(string="Montant Client", store=True, help="La part qui sera payé par le client")
    
    def write(self, values):
        # OVERRIDE
        res = super(SaleOrderInherit, self).write(values)
        
        # Context sur M2m non fonctionnel
        if 'pe_attachment_ids' in values:
            # Rends les documents public pour consultation client
            for data in self.pe_attachment_ids:
                data.public = True
        return res

    @api.model
    def create(self,vals):
        res = super(SaleOrderInherit, self).create(vals)
        if res.pe_attachment_ids:
            for attachment in res.pe_attachment_ids:
                # A la création de l'enregistrements les documents ne prend pas en compte
                # le context du model de l'objet créer ce qui pose une erreur d'accès aux users 
                # force le model d'objet et l'id de l'enregistrement pour chaque documents
                attachment.write({'res_model': self._name, 'res_id': res.id})
        return res
        
    
    @api.onchange('order_line','tax_totals_json')
    def _compute_total_custo_adm(self):
        """
            Calcul les totaux ADM et clients
        """
        _logger.error('[Ventes : Part Client & ADM]')
        # --- Check if revatua is activated ---#
        if self.revatua_ck:
            sum_customer = 0
            sum_adm = 0
            
            for line in self.order_line:
                # Clients = Total car taxe déduit et maritime aussi
                sum_customer += line.price_total
                if line.check_adm: # Si ligne ADM (Séparation des montants Administration & Clients)
                    # Administration = Maritime + RPA
                    sum_adm += round(line.tarif_maritime, 0) + round(line.tarif_rpa, 0)

            self.write({'sum_adm': sum_adm, 'sum_customer' : sum_customer})
            _logger.warning(f"Adm = {sum_adm} | Custo = {sum_customer}")
            
    @api.depends('order_line.tax_id', 'order_line.price_unit', 'amount_total', 'amount_untaxed')
    def _compute_tax_totals_json(self):
        # OVERRIDE
        _logger.error('[Total Taxes]')
        
        # Relance le cacul des totaux ADM et clients
        self._compute_total_custo_adm()
        
        def compute_taxes(order_line):
            price = order_line.price_unit * (1 - (order_line.discount or 0.0) / 100.0)
            order = order_line.order_id
            
            # Récupération de la ligne dans le calcul des taxes 
            return order_line.tax_id._origin.compute_all(price,
                                                         order.currency_id,
                                                         order_line.product_uom_qty,
                                                         product= order_line.product_id,
                                                         partner= order.partner_shipping_id,
                                                         discount= order_line.discount,
                                                         order_line= order_line)

        account_move = self.env['account.move']
        for order in self:
            tax_lines_data = account_move._prepare_tax_lines_data_for_totals_from_object(order.order_line, compute_taxes)
            tax_totals = account_move._get_tax_totals(order.partner_id, tax_lines_data, order.amount_total, order.amount_untaxed, order.currency_id)
            order.tax_totals_json = json.dumps(tax_totals)
    
    def _prepare_invoice(self):
        # OVERRIDE
        # Méthode de préparation des champs pour la facture
        invoice_vals = super(SaleOrderInherit,self)._prepare_invoice()
        # --- Check if revatua is activate ---#
        if self.revatua_ck:
            invoice_vals.update({
                'sum_adm': self.sum_adm,
                'sum_customer': self.sum_customer,
                'commune_recup': self.commune_recup,
                'contact_expediteur': self.contact_expediteur,
                'commune_dest': self.commune_dest,
                'contact_dest': self.contact_dest,
                'invoice_line_ids': [],
            })
        return invoice_vals