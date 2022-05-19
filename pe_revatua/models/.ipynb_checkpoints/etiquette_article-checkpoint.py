# -*- coding: utf-8 -*-

from odoo import fields, models, api

class ProductEtiquette(models.Model):
    _name = "product.etiquette"
    _description = "Etiquette d'article"
    
    name = fields.Char(string='Nom')