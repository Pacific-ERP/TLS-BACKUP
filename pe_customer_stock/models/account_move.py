# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api
from markupsafe import Markup

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = "account.move"

    customer_stock_id = fields.Many2one(string="Stock Clients", comodel_name="customer.stock")

    def _get_custom_link(self):
        return Markup("<a href=# data-oe-model='%s' data-oe-id='%s'>%s</a>") % (
            self._name, self.id, self.name)