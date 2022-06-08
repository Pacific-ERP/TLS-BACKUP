# -*- coding: utf-8 -*-
import logging
from odoo import fields, models, api

_logger = logging.getLogger(__name__)

class AccountMoveLineInherit(models.Model):
    _inherit = "account.move.line"
    
    tarif_rpa = fields.Float(string='RPA', default=0, required=True, store=True)
    tarif_maritime = fields.Float(string='Maritime', default=0, required=True, store=True)
    tarif_terrestre = fields.Float(string='Terrestre', default=0, required=True, store=True)
    r_volume = fields.Float(string='Volume Revatua (m³)', default=0, store=True)
    r_weight = fields.Float(string='Volume weight (T)', default=0, store=True)
    revatua_uom = fields.Char(string='Udm', store=True)
    check_adm = fields.Boolean(string='Payé par ADM', related="product_id.check_adm")