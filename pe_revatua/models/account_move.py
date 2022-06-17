# -*- coding: utf-8 -*-
import logging
from odoo import fields, models, api

_logger = logging.getLogger(__name__)

class AccountMoveInherit(models.Model):
    _inherit = "account.move"
    
    is_adm_invoice = fields.Boolean(string='Est pour ADM', store=True, default=False)
    adm_group_id = fields.Many2one(string='Facture globale ADM', store=True, comodel_name='account.move.adm')
    
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
                
    # Maritime & terrestre
    sum_maritime = fields.Monetary(string="Maritime", store=True, help="La part maritime correspond à 40% du prix HT")
    sum_terrestre = fields.Monetary(string="Terrestre", store=True, help="La part terrestre correspond à 60% du prix HT")
    sum_mar_ter = fields.Monetary(string="Total Maritime & Terrestre", store=True)
    sum_adm = fields.Monetary(string="Montant ADM", store=True, help="La part qui sera payé par l'administration")
    sum_customer = fields.Monetary(string="Montant Client", store=True, help="La part qui sera payé par le client")
    
    def _add_move_line(self, sequence=1):
        self.ensure_one()
        vals = {
            'sequence': sequence,
            'name': self.name,
            'display_type': 'line_section',
            'product_id': False,
            'r_volume': 0,
            'r_weight': 0,
            'quantity': 0,
            'revatua_uom': '',
            'price_subtotal': 0,
            'tax_id': [], #RPA id
            'tarif_terrestre': 0,
            'tarif_maritime': 0,
            'tarif_rpa': 0,
            'price_total': 0,
        }
        _logger.error('Seq : %s | Ligne: %s' % (sequence,vals))
        return vals