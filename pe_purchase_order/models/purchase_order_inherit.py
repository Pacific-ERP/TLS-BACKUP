# -*- coding: utf-8 -*-
import logging
from odoo import fields, models, api

_logger = logging.getLogger(__name__)

class PurchaseOrderInherit(models.Model):
    _inherit = "purchase.order"
    
    ################################ Override State purchase.py ################################
    #state = fields.Selection( selection_add =[
    #    ('delivered', 'Commande à facturé'),   # Etat ajoutée
    #    ('invoicing', 'Facture en attentes'),   # Etat ajoutée
    #    ('all_done', 'Commande cloturée'),     # Etat ajoutée
    #], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)
    ################################ Override State purchase.py ################################ picking_ids invoice_status(to invoice, invoiced)
    
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
