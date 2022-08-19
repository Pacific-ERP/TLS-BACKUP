# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api

_logger = logging.getLogger(__name__)

class PurchaseOrderInherit(models.Model):
    _inherit = "purchase.order"
    
    opportunity_ids = fields.Many2many(string='Opportunité', comodel_name='crm.lead', compute='_compute_opportunities')
    
    @api.model_create_multi
    def create(self, vals_list):
        # OVERRIDE
        res = super(PurchaseOrderInherit, self).create(vals_list)
        if res.opportunity_id:
            message=('Cet achat à été créé à partir de <a href=# data-oe-model=crm.lead data-oe-id=%s>%s</a>') % (res.opportunity_id.id,res.opportunity_id.name)
            res.message_post(body=message)
        return res
    
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
                
        
    
    