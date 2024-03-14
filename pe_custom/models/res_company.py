# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class ResCompany(models.Model):
    _inherit = "res.company"

    technical_data = fields.Many2many(string='Fiche technique',
                                      comodel_name='ir.attachment',
                                      context={'default_public': True})

    