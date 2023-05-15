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
            stage = self.env['crm.stage'].search([('company_id','=', res.company_id.id),('is_default_stage','=', True)]).id
            res.stage_id = stage if stage else self.env['crm.stage'].search([('company_id','=', company.id)])[0].id
        return res