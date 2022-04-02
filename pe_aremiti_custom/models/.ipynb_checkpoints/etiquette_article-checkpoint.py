# -*- coding: utf-8 -*-

from odoo import fields, models, api



class ProductTemplateInherit(models.Model):
    _name = "product.etiquette"
    _description = "Etiquette d'article"
    
    check_adm = fields.Boolean(string='Payé par ADM', default=False)
    check_barre_roue = fields.Boolean(string='Barre à roue', default=False)
    etiquette_produit = fields.