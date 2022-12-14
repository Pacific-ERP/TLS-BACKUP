# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api

_logger = logging.getLogger(__name__)

class CrmLead(models.Model):
    _inherit = "crm.lead"
    
    crm_status = fields.Char(string='Status', compute="_get_crm_status")
    eta_date = fields.Datetime(string='ETA')
    
    @api.depends('stage_id')
    def _get_crm_status(self):
        for crm in self:
            if crm.stage_id:
                crm.crm_status = crm.stage_id.name
            else:
                crm.crm_status = ''