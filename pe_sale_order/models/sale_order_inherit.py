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
    ], string='État de Livraisons', compute='_get_deliveries_state', store=True, readonly=True, copy=False, default='no')
    
    invoices_status = fields.Selection([
        ('no','Rien à facturé'),
        ('to_invoice','À facturé'),
        ('partial_invoiced','Factures en attente'),
        ('invoiced','Complètement Facturé')
    ], string='État de facturations', compute='_get_invoices_state', store=True, readonly=True, copy=False, default='no')
    
    # Vérification de l'avancement des livraisons     
    @api.depends('delivery_line.state')
    def _get_deliveries_state(self):
        for sale in self:
            _logger.error('_get_deliveries_state')
            if sale.state not in ('sale', 'done'):
                sale.delivery_status = 'no'
                continue
            if any(line.state != 'done' for line in sale.delivery_line):
                sale.delivery_status = 'in_delivery'
            elif (all(line.state == 'done' for line in sale.delivery_line) and sale.delivery_line) or sale.is_deliver:
                sale.delivery_status = 'all_delivered'
            else:
                sale.delivery_status = 'no'
                
    # Vérification de l'avancement des factures     
    @api.depends('order_line.qty_to_invoice')
    def _get_invoices_state(self):
        for sale in self:
            if sale.state not in ('sale', 'done'):
                sale.invoices_status = 'no'
                continue
            if sale.delivery_status == 'all_delivered' and not sale.invoice_ids:
                sale.invoices_status = 'to_invoice'
            elif any(invoice.state != 'posted' for invoice in sale.invoice_ids):
                sale.invoices_status = 'partial_invoiced'
            elif (all(invoice.state == 'posted' for invoice in sale.invoice_ids) and sale.invoice_ids):
                sale.invoices_status = 'invoiced'
            else:
                sale.invoices_status = 'no'