# -*- coding: utf-8 -*-
import logging
from odoo import fields, models, api

_logger = logging.getLogger(__name__)

class SaleOrderInherit(models.Model):
    _inherit = "sale.order"
    
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
    sum_maritime = fields.Monetary(string="Maritime", store=True, help="La part maritime correspond à 40% du prix HT")
    sum_terrestre = fields.Monetary(string="Terrestre", store=True, help="La part terrestre correspond à 60% du prix HT")
    sum_mar_ter = fields.Monetary(string="Total Maritime & Terrestre", store=True)
    sum_adm = fields.Monetary(string="Montant ADM", store=True, help="La part qui sera payé par l'administration")
    sum_customer = fields.Monetary(string="Montant Client", store=True, help="La part qui sera payé par le client")
    
    # total_tarif
    @api.onchange('order_line')
    def _total_tarif(self):
        # --- Check if revatua is activate ---#
        if self.env.company.revatua_ck:
            sum_mar = 0
            sum_ter = 0
            sum_adm = 0
            sum_customer = 0
            for order in self:
                # Sum tarif_terrestre and maritime
                for line in order.order_line:
                    sum_customer += line.price_total
                    if line.tarif_maritime:
                        if line.check_adm:
                            sum_adm += round(line.tarif_maritime) + round(line.tarif_rpa)
                            sum_mar += round(line.tarif_maritime)
                        else:
                            sum_mar += round(line.tarif_maritime)
                    if line.tarif_terrestre:
                        sum_ter += round(line.tarif_terrestre)
                # Write fields values car les champs sont en readonly
                order.write({
                    'sum_maritime' : sum_mar,
                    'sum_terrestre' : sum_ter,
                    'sum_mar_ter' : sum_mar + sum_ter,
                    'sum_adm' : sum_adm,
                    'sum_customer' : sum_customer - sum_adm,
                })
        else:
            _logger.error('Revatua not activate : sale_order.py -> _total_tarif')
                
    def _prepare_invoice(self):
        #### OVERRIDE ####
        invoice_vals = super(SaleOrderInherit,self)._prepare_invoice()
        # --- Check if revatua is activate ---#
        if self.env.company.revatua_ck:
            _logger.error('Avant IV : %s ' % invoice_vals)
            invoice_vals.update({
                'sum_adm': self.sum_adm,
                'sum_customer': self.sum_customer,
            })
            _logger.error('Après IV : %s ' % invoice_vals)
        else:
            _logger.error('Revatua not activate : sale_order.py -> _prepare_invoice')
        return invoice_vals
    