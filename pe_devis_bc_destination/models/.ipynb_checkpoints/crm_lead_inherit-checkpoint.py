# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api

_logger = logging.getLogger(__name__)

class CrmLeadInherit(models.Model):
    _inherit = "crm.lead"
    
    pe_bc = fields.Char(string="Référence Client", store=True)
    pe_destination = fields.Many2one(string='Destination', comodel_name="sale.destination", store=True)
    
    def action_new_quotation(self):
        res = super(CrmLeadInherit,self).action_new_quotation()
        if self.pe_bc:
            res['context']['default_pe_bc'] = self.pe_bc
        if self.pe_destination:
            res['context']['default_pe_destination'] = self.pe_destination.id
        return res
