# -*- coding: utf-8 -*-

from odoo import fields, models, api

class ProductTemplateInherit(models.Model):
    _inherit = "product.template"
    
    check_adm = fields.Boolean(string='Payé par ADM', default=False)
    check_barre_roue = fields.Boolean(string='Barre à roue', default=False)
    etiquette_produit = fields.Many2many(string="Etiquette d'article",comodel_name="product.etiquette", relation='product_etiquette_aremiti', column1='product_id', column2='etiquette_id')
    
    tarif_normal = fields.Monetary(string='Tarif normal')
    tarif_minimum = fields.Monetary(string='Tarif minimum')
    
    tarif_fret = fields.Monetary(string='Tarif fret')
    tarif_minimum_fret = fields.Monetary(string='Tarif minimum fret')
    
    tarif_terrestre = fields.Monetary(string='Tarif terrestre')
    tarif_minimum_terrestre = fields.Monetary(string='Tarif minimum terrestre')
    
    tarif_rpa = fields.Monetary(string='Tarif RPA')
    tarif_minimum_rpa = fields.Monetary(string='Tarif minimum RPA')
    
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
                                                  ('fut','Fût')                                           
    ], string='Famille', default='livraison_moorea')