# -*- coding: utf-8 -*-

from odoo import fields, models, api


class PurchaseOrderInherit(models.Model):
    _inherit = "purchase.order"
    
    ################################ Override State purchase.py ################################
    state = fields.Selection( selection_add =[
        ('delivered', 'Commande à facturé'),   # Etat ajoutée
        ('invoicing', 'Facture en attentes'),   # Etat ajoutée
        ('all_done', 'Commande cloturée'),     # Etat ajoutée
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)
    ################################ Override State purchase.py ################################ picking_ids invoice_status(to invoice, invoiced)
    
    delivery_line = fields.One2many(comodel_name='stock.picking', inverse_name='purchase_id', string='delivery line', copy=True)

    delivery_status = fields.Selection([
        ('no','pas de Livraison faites'),
        ('in_delivery','Livraison en cour'),
        ('all_delivered','Livraison complète')
    ], string='Status reception', compute='_get_deliveries_state', store=True, readonly=True, copy=False, default='no')
    
    # Changement d'état vers Commande à facturée si toute les livraison sont closes
    @api.depends('delivery_status')
    def _deliveries_state_now(self):
        for purchase in self:
            if purchase.delivery_status and purchase.delivery_status == 'all_delivered':
                purchase.x_studio_full_reception = 'Good all delivered'
                purchase.state = 'delivered'
            else:
                purchase.x_studio_full_reception = 'Not good'
                continue
                
    # Changement d'état à Commande en facturation si les factures ne sont pas toute valider
    @api.depends('invoice_status')
    def _invoice_state_in_progress(self):
        for purchase in self:
            if purchase.invoice_status and purchase.invoice_status == 'to invoice' and purchase.delivery_status == 'all_delivered':
                purchase.state = 'invoicing'
            else:
                continue
                
    # Changement d'état à Commande totalement terminé si la facture est complète et 
    @api.depends('invoice_status')
    def _invoice_state_now(self):
        for purchase in self:
            if purchase.invoice_status and purchase.invoice_status == 'invoiced' and purchase.delivery_status == 'all_delivered':
                purchase.state = 'all_done'
            else:
                continue
                
    # Vérification de l'avancement des livraison     
    @api.depends('state','delivery_line.state')
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
