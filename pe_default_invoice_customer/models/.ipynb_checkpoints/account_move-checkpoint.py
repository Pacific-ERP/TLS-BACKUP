# -*- coding: utf-8 -*-

# import logging
from odoo import fields, models, api

# _logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = "account.move"
    
    @api.model_create_multi
    def create(self, vals_list):
        # OVERRIDE
        res = super(AccountMove, self).create(vals_list)
        for move in res:
            if move.partner_id.parent_id:
                move.partner_id = move.partner_id.parent_id
        return res