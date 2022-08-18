# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api

_logger = logging.getLogger(__name__)

class AccountMoveInherit(models.Model):
    _inherit = "account.move"
    
    opportunity_id = fields.Many2one(string='Opportunité', comodel_name='crm.lead')
    
    @api.model_create_multi
    def create(self, vals_list):
        # OVERRIDE
        res = super(AccountMoveInherit, self).create(vals_list)
        if res.invoice_origin and not res.opportunity_id:
            sale = self.env['sale.order'].sudo().search([('name','=',res.invoice_origin)])
            achat = self.env['purchase.order'].sudo().search([('name','=',res.invoice_origin)])
            if sale:
                if sale.opportunity_id:
                    res.opportunity_id = sale.opportunity_id
            elif achat:
                if achat.opportunity_id:
                    res.opportunity_id = achat.opportunity_id
        return res