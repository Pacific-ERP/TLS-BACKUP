# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api

_logger = logging.getLogger(__name__)

class CustomerStockWizard(models.TransientModel):
    _name = "customer.stock.wizard"
    _description = "Pacific-ERP : wizard customer stock"

    def _get_destination_domain(self):
        customer_location = self.env.ref('stock.stock_location_customers')
        return [('location_id','=', customer_location.id)] if customer_location else []
    
    direct_delivery = fields.Boolean(string="Livraison direct ?", default=True)
    partner_id = fields.Many2one(string="Client", comodel_name="res.partner")
    destination_id = fields.Many2one(string="Emplacement client", comodel_name="stock.location", domain=_get_destination_domain)
    origin = fields.Char(string="Origine")
    picking_id = fields.Many2one(string="Transfert", comodel_name="stock.picking")

    wizard_lines = fields.One2many(string="Opération", comodel_name="customer.stock.wizard.line", inverse_name="wizard_id")

    def button_confirm(self):
        pass
    
class CustomerStockWizardLine(models.TransientModel):
    _name = "customer.stock.wizard.line"
    _description = "Pacific-ERP : Ligne wizard customer stock"

    wizard_id = fields.Many2one(string="Customer Stock", comodel_name="customer.stock.wizard")
    move_id = fields.Many2one(string="Move", comodel_name="stock.move")
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    product_uom_id = fields.Many2one('uom.uom', 'UdM', required=True, domain="[('category_id', '=', product_uom_category_id)]")
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
    quantity = fields.Float(string="Quantité")
