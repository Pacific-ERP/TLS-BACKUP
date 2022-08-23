# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api

_logger = logging.getLogger(__name__)

class AccountMoveInherit(models.Model):
    _inherit = "account.move"
    
    opportunity_id = fields.Many2one(string='Opportunité', comodel_name='crm.lead')
    opportunity_ids = fields.Many2many(string='Opportunités', comodel_name='crm.lead')
    
    @api.model_create_multi
    def create(self, vals_list):
        # OVERRIDE
        res = super(AccountMoveInherit, self).create(vals_list)
        for record in res:
            if record.invoice_origin and not record.opportunity_id:
                sale = self.env['sale.order'].sudo().search([('name','=',record.invoice_origin)])
                achat = self.env['purchase.order'].sudo().search([('name','=',record.invoice_origin)])
                if sale:
                    if sale.opportunity_id:
                        lead = self.env['crm.lead'].sudo().search([('id','=',sale.opportunity_id.id)])
                        if lead:
                            record.write({'opportunity_ids':[(4,lead.id)]})
                            lead.write({'invoice_ids': [(4,record.id)]})
                elif achat:
                    if achat.opportunity_ids:
                        for opportunity in achat.opportunity_ids:
                            lead = self.env['crm.lead'].sudo().search([('id','=',opportunity.id)])
                            if lead:
                                record.write({'opportunity_ids':[(4,lead.id)]})
                                lead.write({'invoice_ids': [(4,record.id)]})
        return res