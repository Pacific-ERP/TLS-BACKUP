# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api

_logger = logging.getLogger(__name__)

class PurchaseWheelMarkWizard(models.TransientModel):
    _name = "purchase.wheelmark.wizard"
    _description = "Pop-up Wheelmark"
    
    #html_vals = fields.Html(string='Attention', readonly=True)
    
    def action_confirm(self):
        return True