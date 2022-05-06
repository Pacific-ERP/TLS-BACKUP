# -*- coding: utf-8 -*-
import logging
from odoo import fields, models, api

_logger = logging.getLogger(__name__)

class SaleOrderInherit(models.Model):
    _inherit = "sale.order"
    
    #ajouter le module sale_stock dans les dépendances du manifest pour avoir le champs sale_id sinon erreur d'existence
    delivery_line = fields.One2many(comodel_name='stock.picking', inverse_name='sale_id', string='delivery line (sale)', copy=True)

    delivery_status = fields.Selection([
        ('no','Pas de livraison'),
        ('in_delivery','Livraison en cours'),
        ('all_delivered','Livraison complète')
    ], string='Statut reception', compute='_get_deliveries_state', store=True, readonly=True, copy=False, default='no')
          
    # Vérification de l'avancement des livraison     
    @api.depends('delivery_line.state')
    def _get_deliveries_state(self):
        for sale in self:
            if sale.state not in ('sale', 'done'):
                sale.delivery_status = 'no'
                continue
            if any(
                line.state != 'done'
                for line in sale.delivery_line
            ):
                sale.delivery_status = 'in_delivery'
            elif (
                all(
                    line.state == 'done'
                    for line in sale.delivery_line
                )
                and sale.delivery_line
            ):
                sale.delivery_status = 'all_delivered'
            else:
                sale.delivery_status = 'no'

        # Si trop de soucis avec le champs de base de facturation(invoice_status) refaire la méthode manuellement 