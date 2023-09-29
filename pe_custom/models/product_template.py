# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = "product.template"

    code_douanier = fields.Char(string="Code douanier")
    ref_constructeur = fields.Char(string="Référence constructeur")