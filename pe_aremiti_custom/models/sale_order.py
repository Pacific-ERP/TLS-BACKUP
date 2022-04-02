# -*- coding: utf-8 -*-

from odoo import fields, models, api


class SaleOrderInherit(models.Model):
    _inherit = "sale.order"
    
    mt_txt1 = fields.Char(string='Texte(A)')
    mt_txt2 = fields.Char(string='Texte(A) required')
    mt_numb = fields.Integer(string='Interger(A)')
    mt_boolean = fields.Boolean(string='Boolean(A)')
    mt_date = fields.Date(string='Date(A)')
    
    