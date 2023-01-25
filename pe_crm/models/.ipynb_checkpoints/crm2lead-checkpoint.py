# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api

_logger = logging.getLogger(__name__)

# Opportunité
class Lead2OpportunityPartner(models.TransientModel):
    _inherit = "crm.lead2opportunity.partner"
    
    def _action_convert(self):
        # Override #
        res = super(Lead2OpportunityPartner, self)._action_convert()
        if res.company_id:
            stage = self.env['crm.stage'].search([('company_id','=',res.company_id.id)])
            res.stage_id = stage[0]
        return res