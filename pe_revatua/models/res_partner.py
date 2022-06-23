# -*- coding: utf-8 -*-

from odoo import fields, models, api

class ResPartnerInherit(models.Model):
    _inherit = "res.partner"
    
    id_adm = fields.Boolean(string='Administration', default=False, copy=False, store=True)