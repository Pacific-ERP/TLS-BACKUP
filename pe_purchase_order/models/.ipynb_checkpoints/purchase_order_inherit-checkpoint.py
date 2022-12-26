# -*- coding: utf-8 -*-
import logging
from odoo import fields, models, api

_logger = logging.getLogger(__name__)

class PurchaseOrderInherit(models.Model):
    _inherit = "purchase.order"
    
    #ajouter le module purchase_stock dans les dépendances du manifest pour avoir le champs purchase_id sinon erreur d'existence
    delivery_line = fields.One2many(comodel_name='stock.picking', inverse_name='purchase_id', string='delivery line', copy=False)

    delivery_status = fields.Selection([
        ('no','Pas de réception'),
        ('in_delivery','Réception en cours'),
        ('all_delivered','Réception complète')
    ], string='État de reception', compute='_get_deliveries_state', store=True, readonly=True, copy=False, default='no')
    
    invoices_status = fields.Selection([
        ('no','Rien à facturé'),
        ('to_invoice','À facturé'),
        ('partial_invoiced','Factures en attente'),
        ('invoiced','Complètement Facturé')
    ], string='État de facturations', compute='_get_invoices_state', store=True, readonly=True, copy=False, default='no')
    
    # Vérification de l'avancement des livraison     
    @api.depends('delivery_line.state')
    def _get_deliveries_state(self):
        for purchase in self:
            if purchase.state not in ('purchase', 'done'):
                purchase.delivery_status = 'no'
                continue
            # Si il reste des livraison à valider
            if any(line.state not in ('done','cancel') for line in purchase.delivery_line):
                purchase.delivery_status = 'in_delivery'
            # Si toutes livraison sont faites ou si c'est uniquement des articles services passer en livraison complète
            elif (all(line.state in ('done','cancel') for line in purchase.delivery_line) and purchase.delivery_line) or (all(line.product_id.detailed_type == 'service' for line in purchase.order_line)):
                purchase.delivery_status = 'all_delivered'
            # Sinon aucune livraison fait
            else:
                purchase.delivery_status = 'no'

    # Si il n'ya que des services dans la liste des articles (donc pas de réception à faire) passer le status de reception en complète
    def button_confirm(self):
        ### OVERRIDE ###
        res = super(PurchaseOrderInherit, self).button_confirm()
        for record in self:
            if (all(line.product_id.detailed_type == 'service' for line in record.order_line)) and record.order_line and record.state in ('done','purchase'):
                record.delivery_status = 'all_delivered'
        return res

    # Vérification de l'avancement des factures     
    @api.depends('order_line.qty_to_invoice')
    def _get_invoices_state(self):
        for purchase in self:
            if purchase.state not in ('sale', 'done'):
                purchase.invoices_status = 'no'
                continue
            if purchase.delivery_status == 'all_delivered' and not purchase.invoice_ids:
                purchase.invoices_status = 'to_invoice'
            elif any(invoice.state != 'posted' for invoice in purchase.invoice_ids):
                purchase.invoices_status = 'partial_invoiced'
            elif (all(invoice.state == 'posted' for invoice in purchase.invoice_ids) and purchase.invoice_ids):
                purchase.invoices_status = 'invoiced'
            else:
                purchase.invoices_status = 'no'