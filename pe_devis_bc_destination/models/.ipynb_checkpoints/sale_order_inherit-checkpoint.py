# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api

_logger = logging.getLogger(__name__)

class SaleOrderInherit(models.Model):
    _inherit = "sale.order"
    
    pe_bc = fields.Char(string="Référence Client")
    pe_destination = fields.Many2one(string='Destination', comodel_name="sale.destination", store=True)
