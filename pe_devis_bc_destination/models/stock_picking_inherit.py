# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api

_logger = logging.getLogger(__name__)

class StockPickingInherit(models.Model):
    _inherit = "stock.picking"
    
    pe_bc = fields.Char(string="Référence Client", related="sale_id.pe_bc")
    pe_destination = fields.Many2one(string='Destination', store=True, related="sale_id.pe_destination")
