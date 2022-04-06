# -*- coding: utf-8 -*-
import logging
from odoo import fields, models, api

_logger = logging.getLogger(__name__)

class PurchaseOrderInherit(models.Model):
    _inherit = "purchase.order"
    
    #ajouter le module purchase_stock dans les dépendances du manifest pour avoir le champs purchase_id sinon erreur d'existence
    delivery_line = fields.One2many(comodel_name='stock.picking', inverse_name='purchase_id', string='delivery line', copy=True)

    delivery_status = fields.Selection([
        ('no','Pas de livraison'),
        ('in_delivery','Livraison en cour'),
        ('all_delivered','Livraison complète')
    ], string='Status reception', compute='_get_deliveries_state', store=True, readonly=True, copy=False, default='no')
          
    # Vérification de l'avancement des livraison     
    @api.depends('delivery_line.state')
    def _get_deliveries_state(self):
        for purchase in self:
            if purchase.state not in ('purchase', 'done'):
                purchase.delivery_status = 'no'
                continue
            if any(
                line.state != 'done'
                for line in purchase.delivery_line
            ):
                purchase.delivery_status = 'in_delivery'
            elif (
                all(
                    line.state == 'done'
                    for line in purchase.delivery_line
                )
                and purchase.delivery_line
            ):
                purchase.delivery_status = 'all_delivered'
            else:
                purchase.delivery_status = 'no'

        # Si trop de soucis avec le champs de base de facturation(invoice_status) refaire la méthode manuellement 