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
                                default=0)
    tarif_minimum_rpa = fields.Monetary(string='Tarif minimum RPA',
                                        default=0)
        
    #Terrestre 60% du prix normal & maritime 40% du prix normal
    @api.onchange('tarif_normal')
    def _get_default_value_m_t(self):
        for record in self:
            t_normal = record.tarif_normal
            # si tarif normal existe et qu'il n'est pas = à 0 et si les tarifs terrestre 
            if t_normal and t_normal != 0:
                record.list_price = t_normal
                record.tarif_terrestre = (t_normal * 0.6)
                record.tarif_maritime = (t_normal * 0.4)
                if record.tarif_rpa == 0:
                    record.tarif_rpa = 100
                
    #Fields maritime
    tarif_maritime = fields.Monetary(string='Tarif maritime',
                                     default=0,
                                     readonly=False)
    tarif_minimum_maritime = fields.Monetary(string='Tarif minimum maritime',
                                             default=0)
    #Fields Terrestre
    tarif_terrestre = fields.Monetary(string='Tarif terrestre',
                                      default=0,
                                      readonly=False)
    tarif_minimum_terrestre = fields.Monetary(string='Tarif minimum terrestre',
                                              default=0)

    
    
    
    