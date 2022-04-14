# -*- coding: utf-8 -*-
import logging
from odoo import fields, models, api

_logger = logging.getLogger(__name__)

class ProductTemplateInherit(models.Model):
    _inherit = "product.template"
    #Fields Autres
    check_adm = fields.Boolean(string='Payé par ADM',
                               default=False)
    
    etiquette_produit = fields.Many2many(string="Etiquette d'article",
                                         comodel_name="product.etiquette",
                                         relation='product_etiquette_aremiti',
                                         column1='product_id',
                                         column2='etiquette_id')
    
    famille_produit = fields.Selection(selection=[('livraison_moorea','Livraison Moorea'),
                                                  ('livraison_tahiti','Livraison Tahiti'),
                                                  ('location','Locations'),
                                                  ('gardiennage_materiel','Gardiennage Matériel'),
                                                  ('depotage_empotage','Dépotage - Empotage'),
                                                  ('chargement_déchargement','Chargement - Déchargement'),
                                                  ('acconage','Acconage'),
                                                  ('bon_chauffeur','Bon chauffeur'),
                                                  ('gratuite','Gratuité'),
                                                  ('chauffeur','Chauffeur'),
                                                  ('assurance','Assurance'),
                                                  ('fut','Fût')],
                                       string='Famille', default='livraison_moorea')
    
    #Fields Normal
    tarif_normal = fields.Monetary(string='Tarif normal',
                                   default=0)
    tarif_minimum = fields.Monetary(string='Tarif minimum',
                                    default=0)
    #Fields RPA
    tarif_rpa = fields.Monetary(string='Tarif RPA',
                                default=100)
    tarif_minimum_rpa = fields.Monetary(string='Tarif minimum RPA',
                                        default=0)
        
    
    
    #Terrestre 60% du prix normal & maritime 40% du prix normal
    @api.depends('tarif_normal')
    def _get_default_value_m_t(self):
        for record in self:
            if record.tarif_normal and record.tarif_normal != 0:
                record.tarif_terrestre = (record.tarif_normal * 0.6)
                record.tarif_maritime = (record.tarif_normal * 0.4)
                
    #Fields maritime
    tarif_maritime = fields.Monetary(string='Tarif maritime',
                                     compute=_get_default_value_m_t,
                                     default=0,
                                     readonly=False)
    tarif_minimum_maritime = fields.Monetary(string='Tarif minimum maritime',
                                             default=0)
    #Fields Terrestre
    tarif_terrestre = fields.Monetary(string='Tarif terrestre',
                                      compute=_get_default_value_m_t,
                                      default=0,
                                      readonly=False)
    
    tarif_minimum_terrestre = fields.Monetary(string='Tarif minimum terrestre',
                                              default=0)

    
    
    
    