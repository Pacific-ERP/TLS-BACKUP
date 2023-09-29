# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    transport_type = fields.Selection(string="Mode d'acheminement", selection=[('plane','Avion'),
                                                                               ('boat','Bateau'),
                                                                               ('terreste','Terrestre')]
                                      , default=False, copy=False)
    
    provenance = fields.Many2one(string="Provenance", comodel_name="res.country")