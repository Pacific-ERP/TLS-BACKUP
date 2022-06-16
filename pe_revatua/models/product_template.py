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
    #Ratio T/M
    ratio_terrestre = fields.Float(string='Terrestre(%)',
                                   help='La part du prix normal qui est pris pour la partie Terrestre en pourcentage',
                                   default=0.6,
                                   readonly=False)
    ratio_maritime = fields.Float(string='maritime(%)',
                                   help='La part du prix normal qui est pris pour la partie maritime en pourcentage (1-Terrestre)',
                                   default=0.4,
                                   readonly=False)
    #Terrestre 60% du prix normal & maritime 40% du prix normal
    @api.onchange('tarif_normal','ratio_terrestre')
    def _get_default_revatua(self):
        # --- Check if revatua is activate ---#
        if self.env.company.revatua_ck:
            for record in self:
                # Ratio maritime est égale au reste de la diff terrestre et normal >>> 1 - r_t
                r_t = record.ratio_terrestre
                r_m = 1 - r_t
                record.ratio_maritime = r_m
                # Si tarif normal existe on initialise tout les champs qui suivent (prix de vente,tarif terrester/maritime, RPA)
                # Vérification si l'option revatua est cocher pour cette société >>> self.env.company.revatua_ck
                if record.tarif_normal and self.env.company.revatua_ck:
                    record.tarif_terrestre = record.tarif_normal * r_t
                    record.tarif_maritime = record.tarif_normal * r_m
                    record.tarif_rpa = 100
                # Si le prix normal est remis à 0 on retirer les valeurs des champs pour éviter des soucis de calcul par la suite
                else:
                    record.list_price = 1
                    record.tarif_terrestre = 0
                    record.tarif_maritime = 0
                    record.tarif_rpa = 0
        else:
            _logger.error('Revatua not activate : product_template.py -> _get_default_revatua')
    
    #Ajout automatique de la taxes RPA si le champs RPA est remplis
    @api.onchange('tarif_rpa')
    def _add_rpa_taxe(self):
        # --- Check if revatua is activate ---#
        if self.env.company.revatua_ck:
            rpa = self.env['account.tax'].sudo().search([('name','=','RPA'),('company_id','=',2)])
            for record in self:
                if record.tarif_rpa:
                    record.taxes_id = [(4, rpa.id)]
                elif record.tarif_rpa == 0:
                    for taxe in record.taxes_id:
                        if str(rpa.id) in str(taxe.id):
                            record.taxes_id = [(3,taxe.id)]
        else:
            _logger.error('Revatua not activate : product_template.py -> _add_rpa_taxe')

    #Fields Maritime
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

    
    
    
    