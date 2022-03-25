# -*- coding: utf-8 -*-

from odoo import fields, models


class PurchaseOrderInherit(models.Model):
    _inherit = "puchase.order"
    
    ##### Override State purchase.py ######
    state = fields.Selection([
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Commande validée'),     # Value modifier old :Locked
        ('cancel', 'Cancelled'),
        ('to_invoice', 'Commande à facturé'),   # Etat ajoutée
        ('fully_done', 'Commande cloturée')     # Etat ajoutée
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)
    ##### Override State purchase.py ###### picking_ids
    
    delivery_line = fields.One2many(comodel_name='stock.picking', inverse_name='purchase_id', string='delivery line', copy=False)

    delivery_state : fields.Selection([
        ('no','pas de livraison faites')
        ('in_delivery','livraison en cour')
        ('full_delivered','livraison complète')
        
    ], string='Status reception', readonly=True, index=True, copy=False, default='draft', tracking=True)
    
    @api.depends('delivery_state')
    def _deliveries_state_now(self):
        for purchase in self:
            if purchase.delivery_state and purchase.delivery_state == 'full_delivered':
                purchase.state = 'to_invoice'
            else:
                continue
    
    @api.depends('invoice_status')
    def _invoice_state_now(self):
        for purchase in self:
            if purchase.invoice_status and purchase.invoice_status == 'invoiced' and purchase.delivery_state == 'full_delivered':
                purchase.state = 'fully_done'
            else:
                continue
        
    @api.depends('state','delivery_line.state')
    def _get_deliveries_state(self):
        for purchase in self:
            if purchase.state not in ('purchase', 'done'):
                purchase.delivery_state = 'no'
                continue

            if any(line.state != 'done'
                for line in purchase.delivery_line
            ):
                purchase.delivery_state = 'in_delivery'
            elif (
                all(
                    line.state == 'done')
                    for line in purchase.delivery_line
                )
                and purchase.delivery_line
            ):
                order.invoice_status = 'full_delivery'
            else:
                order.invoice_status = 'no'