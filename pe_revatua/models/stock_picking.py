# -*- coding: utf-8 -*-
from odoo import fields, models, api

class StockPickingInherit(models.Model):
    _inherit = "stock.picking"
    
    # Vérification si la coche Revatua est activé
    revatua_ck = fields.Boolean(string="Mode Revatua", related="company_id.revatua_ck")
    travel_date = fields.Datetime(string='Date de voyage')
    
    #Lieu Livraison
    commune_recup = fields.Many2one(string='Commune de récupération',comodel_name='res.commune', related='sale_id.commune_recup')
    ile_recup = fields.Char(string='Île de récupération', related='commune_recup.ile_id.name', store=True)
    contact_expediteur = fields.Many2one(string='Contact expéditeur',comodel_name='res.partner', related='sale_id.contact_expediteur')
    tel_expediteur = fields.Char(string='Téléphone expéditeur', related='contact_expediteur.phone', store=True)
    mobil_expediteur = fields.Char(string='Mobile expéditeur', related='contact_expediteur.mobile', store=True)
    
    # Lieu destinataire
    commune_dest = fields.Many2one(string='Commune de destination',comodel_name='res.commune', related='sale_id.commune_dest')
    ile_dest = fields.Char(string='Île de destination', related='commune_dest.ile_id.name', store=True)
    contact_dest = fields.Many2one(string='Contact de destination',comodel_name='res.partner', related='sale_id.contact_dest')
    tel_dest = fields.Char(string='Téléphone destinataire', related='contact_dest.phone', store=True)
    mobil_dest = fields.Char(string='Mobile destinataire', related='contact_dest.mobile', store=True)