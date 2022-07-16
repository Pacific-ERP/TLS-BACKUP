# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api

_logger = logging.getLogger(__name__)

class AccountMoveInherit(models.Model):
    _inherit = "account.move"
    
    pe_bc = fields.Char(string="Bon de commande")
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
            _logger.warning("c'est good bro")
        return res
    
    """
    for vals in vals_list:
            origin = vals.get('invoice_origin')
            so = self.env['sale.order'].sudo().search([('name','=',origin)])
            if so:
                vals_list['pe_bc'] : so.pe_bc,
                vals_list['pe_destination'] : so.pe_destination,
                _logger.warning('ici')
    """