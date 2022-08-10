# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api

_logger = logging.getLogger(__name__)

class AccountMoveInherit(models.Model):
    _inherit = "account.move"
    
    pe_bc = fields.Char(string="Référence Client")
    pe_destination = fields.Many2one(string='Destination', comodel_name="sale.destination", store=True, copy=False)
    
    @api.model_create_multi
    def create(self, vals_list):
        res = super(AccountMoveInherit, self).create(vals_list)
        so = self.env['sale.order'].sudo().search([('name','=',res.invoice_origin)])
        if so:
            res.write({
                'pe_bc' : so.pe_bc,
                'pe_destination' : so.pe_destination,
            })
        return res