# -*- coding: utf-8 -*-
import logging
from odoo import fields, models, api
from odoo.exceptions import AccessError

_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = "product.template"
    
    pe_emplacement = fields.Char(string="Emplacement")
    pe_customer_denomination = fields.Char(string="Dénomination client")
    pe_emplacement_bis = fields.Many2one(string="Emplacement(bis)", comodel_name="product.emplacement")
    
    def write(self, vals):
        editable_field = {'pe_emplacement','image_1920','pe_customer_denomination','default_code'}
        if any(val not in editable_field for val in vals) and self.env.user.has_group('pe_custom_stock.group_product_emplacement'):
            raise AccessError('Vous pouvez modifiez uniquement les champs(Emplacement,Images,Référence interne,Dénomination client) veuillez annuler la modification et recommencer.')
        return super(ProductTemplate, self).write(vals)
    
class ProductEmplacement(models.Model):
    _name = "product.emplacement"
    _description = "Emplacement d'article"
    
    name = fields.Char(string="Nom",required=True)
    desc = fields.Char(string="Description")