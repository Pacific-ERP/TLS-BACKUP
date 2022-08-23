# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api

_logger = logging.getLogger(__name__)

class PurchaseOrderInherit(models.Model):
    _inherit = "purchase.order"
    
    opportunity_ids = fields.Many2many(string='Opportunités', comodel_name='crm.lead', compute='_compute_opportunities')
    
    @api.depends('origin')
    def _compute_opportunities(self):
        _logger.error('_compute_opportunities')
        for purchase in self:
            sales = self.env['sale.order']
            leads = self.env['crm.lead']
            if purchase.origin:
                origin = tuple(purchase.origin.replace(" ","").split(','))
                _logger.error(origin)
                sales += self.env['sale.order'].sudo().search([('name','in',origin)])
                origin2 = tuple(purchase.origin.split(','))
                _logger.error(origin2)
                leads += self.env['crm.lead'].sudo().search([('name','in',origin2)])
                if sales:
                    _logger.error('origin : sales %s' % sales)
                    for sale in sales:
                        if sale.opportunity_id:
                            purchase.opportunity_ids += sale.opportunity_id
                            crm = self.env['crm.lead'].sudo().search([('id','=',sale.opportunity_id.id)])
                            crm.purchase_ids += purchase
                        elif all(not so.opportunity_id for so in sales):
                            purchase.opportunity_ids = False
                        else:
                            continue
                if leads:
                    _logger.error('origin : leads %s ' % leads)
                    for lead in leads:
                        purchase.opportunity_ids += lead
                        lead.purchase_ids += purchase
                        
                if not sales and not leads:
                    purchase.opportunity_ids = False
            else:
                purchase.opportunity_ids = False            