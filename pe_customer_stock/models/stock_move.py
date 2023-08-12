# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api

_logger = logging.getLogger(__name__)

class StockMove(models.Model):
    _inherit = "stock.move"

    customer_stock_id = fields.Many2one(string="Stock Clients", comodel_name="customer.stock")