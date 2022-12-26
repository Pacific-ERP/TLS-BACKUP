# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    @api.model_create_multi
    def create(self, vals_list):
        records = super(SaleOrder, self).create(vals_list)
        for sale in records:
            if sale.opportunity_id:
                msg=("Le devis a été créée depuis : <a href=# data-oe-model=crm.lead data-oe-id=%d>%s</a>.") % (sale.opportunity_id.id, sale.opportunity_id.name)
                sale.message_post(body=msg)
        return records