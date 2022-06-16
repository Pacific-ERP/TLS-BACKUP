# -*- coding: utf-8 -*-
import logging
from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class AccountMoveAdmWizard(models.TransientModel):
    _name = 'account.move.adm.wizard'
    _description = 'Récupère les dates pour la récupération des factures'
    
    start_date = fields.Date(string='Du', store=True, copy=False, required=True)
    end_date = fields.Date(string='Au', store=True, copy=False)
    adm_invoice_ids = fields.Many2many(string='Factures ADM', comodel_name='account.move')
    
    @api.onchange('start_date','end_date')
    def _onchange_date_range_adm(self):
        for record in self:
            adms = []
            if record.start_date:
                moves = record.env['account.move'].search([('is_adm_invoice','=',True)])
                for move in moves:
                    if move.invoice_date and move.state not in ('draft','cancel'):
                        if record.end_date:
                            if record.end_date <= record.start_date:
                                raise ValidationError('La date de fin ne peut pas être inférieur à la date de départ')
                            else: 
                                if move.invoice_date >= record.start_date and move.invoice_date <= record.end_date:
                                   adms.append(move.id)
                        else:
                            if move.invoice_date >= record.start_date:
                               adms.append(move.id)
            _logger.error(adms)
            record.adm_invoice_ids = [(6,0,adms)]
    
    def group_adm_invoices(self):
        for record in self:
            _logger.error('Boutton activer')