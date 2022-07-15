# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api

_logger = logging.getLogger(__name__)

class ResCompany(models.Model):
    _name = "sale.destination"
    _description = "Destination"
    _order = "sequence"
    
    sequence = fields.Integer(string='Sequence', default=5)
    name = fields.Char("Nom")
    description = fields.Char("Description")
    
    