# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api

_logger = logging.getLogger(__name__)

class CrmLead(models.Model):
    _inherit = "crm.lead"
    
    crm_status = fields.Char(string='Status', compute="_get_crm_status")
    eta_date = fields.Datetime(string='ETA')
    customer_desc = fields.Text('Description')
    
    # Permet de récupérer le status en text directe
    @api.depends('stage_id')
    def _get_crm_status(self):
        for crm in self:
            if crm.stage_id:
                crm.crm_status = crm.stage_id.name
            else:
                crm.crm_status = ''
    
    # Permet d'auto assigner le client à l'opportunité
    @api.model_create_multi
    def create(self, vals_list):
        res = super(CrmLead, self).create(vals_list)
        for crm in res:
            if crm.partner_id.grade_id:
                crm.partner_assigned_id = crm.partner_id
        return res