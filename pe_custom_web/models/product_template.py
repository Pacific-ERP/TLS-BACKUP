# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.depends('name')
    def _technical_data_name(self):
        for template in self:
            if template.name:
                template.technical_data_name = "Fiche_technique_%s" % template.name.replace(" ","_")
            else:
                template.technical_data_name = "Fiche_technique"
            
    technical_data = fields.Many2many(string='Fiche technique',
                                      comodel_name='ir.attachment',
                                      context={'default_public': True},
                                      relation='product_files', column1='attachment_id', column2='pe_ir_attachement')
    technical_data_name = fields.Char(string="Fiche technique name", compute=_technical_data_name)

    old_website_sequence = fields.Integer(string="Ancienne séquence")

    @api.onchange('technical_data')
    def _onchange_technical_data(self):
        if len(self.technical_data) > 1:
            raise UserError("Vous ne pouvez ajoutez que une seuls fiche technique à la fois, supprimer celle existante")

    @api.onchange('website_ribbon_id')
    def _onchange_bandeau(self):
        for template in self:
            
            if template.website_ribbon_id and not template.old_website_sequence:
                template.old_website_sequence = template.website_sequence
                
            if template.website_ribbon_id.id == 3: # Nouveau
                template.website_sequence = 1
            elif template.website_ribbon_id.id == 6: # Promotion
                template.website_sequence = 0
            elif template.old_website_sequence:
                template.website_sequence = template.old_website_sequence
    
    def write(self, values):
        # OVERRIDE
        _logger.warning(f"Values : {values}")
        res = super(ProductTemplate, self).write(values)
        
        # Context sur M2m non fonctionnel
        if 'technical_data' in values:
            for data in self.technical_data:
                data.public = True

    def _get_combination_info(self, combination=False, product_id=False, add_qty=1, pricelist=False, parent_combination=False, only_template=False):
        # OVERRIDE
        combination_info = super(ProductTemplate, self)._get_combination_info(
            combination=combination,
            product_id=product_id,
            add_qty=add_qty,
            pricelist=pricelist,
            parent_combination=parent_combination,
            only_template=only_template,
        )

        # Quantité disponible
        combination_info['virtual_available'] = self.virtual_available
        # Id de la fiche technique
        combination_info['technical_data_id'] = self.technical_data[0].id if self.technical_data else False

        return combination_info