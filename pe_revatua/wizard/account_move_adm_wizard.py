# -*- coding: utf-8 -*-
import logging
from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class AccountMoveAdmWizard(models.TransientModel):
    _name = 'account.move.adm.wizard'
    _description = 'Récupère les dates pour la récupération des factures'
    
    start_date = fields.Date(string='Du', store=True, copy=False)
    end_date = fields.Date(string='Au', store=True, copy=False)
    adm_target = fields.Html(string='Factures')
    
    def group_adm_invoices(self):
        for record in self:
            _logger.error('Boutton activer')