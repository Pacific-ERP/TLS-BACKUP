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
    sum_maritime = fields.Monetary(string="Maritime", store=True)
    sum_terrestre = fields.Monetary(string="Terrestre", store=True)
    sum_mar_ter = fields.Monetary(string="Total Maritime & Terrestre", store=True)
    
    # total_tarif
    @api.onchange('order_line')
    def _total_tarif(self):
        if self.env.company.revatua_ck:
            sum_mar = 0
            sum_ter = 0
            for record in self:
                # Sum tarif_terrestre and maritime
                for line in record.order_line:
                    if line.tarif_maritime:
                        sum_mar += round(line.tarif_maritime)
                    if line.tarif_terrestre:
                        sum_ter += round(line.tarif_terrestre)
                # Write fields values car les champs sont en readonly
                record.write({
                    'sum_maritime' : sum_mar,
                    'sum_terrestre' : sum_ter,
                    'sum_mar_ter' : sum_mar + sum_ter
                })
    
                
                        