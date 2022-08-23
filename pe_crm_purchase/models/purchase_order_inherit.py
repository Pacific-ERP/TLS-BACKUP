# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api

_logger = logging.getLogger(__name__)

class PurchaseOrderInherit(models.Model):
    _inherit = "purchase.order"
    
    opportunity_ids = fields.Many2many(string='Opportunités', comodel_name='crm.lead', compute='_compute_opportunities')
    
    @api.depends('origin')
    def _compute_opportunities(self):
        for purchase in self:
            sales = self.env['sale.order']
            if purchase.origin:
                origin = tuple(purchase.origin.replace(" ","").split(','))
                sales += self.env['sale.order'].sudo().search([('name','in',origin)])
                if sales:
                    for sale in sales:
                        if sale.opportunity_id:
                            purchase.opportunity_ids += sale.opportunity_id
                            crm = self.env['crm.lead'].sudo().search([('id','=',sale.opportunity_id.id)])
                            crm.purchase_ids += purchase
                else:
                    purchase.opportunity_ids = False
            else:
                purchase.opportunity_ids = False
                
        
    
    