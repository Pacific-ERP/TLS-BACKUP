# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api

_logger = logging.getLogger(__name__)

class PurchaseOrderInherit(models.Model):
    _inherit = "purchase.order"
    
    opportunity_id = fields.Many2one(string='Opportunité', comodel_name='crm.lead')
    
    @api.model_create_multi
    def create(self, vals_list):
        # OVERRIDE
        res = super(PurchaseOrderInherit, self).create(vals_list)
        _logger.error(res.opportunity_id)
        if res.origin and not res.opportunity_id:
            sale = self.env['sale.order'].sudo().search([('name','=',res.origin)])
            if sale:
                if sale.opportunity_id:
                    res.opportunity_id = sale.opportunity_id
        elif res.opportunity_id:
            message=('Cet acht à été créé à partir de <a href=# data-oe-model=crm.lead data-oe-id=%s>%s</a>') % (res.opportunity_id.id,res.opportunity_id.name)
            res.message_post(body=message)
        return res