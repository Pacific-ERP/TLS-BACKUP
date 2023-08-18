# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

class StockMove(models.Model):
    _inherit = "stock.move"

    customer_stock_id = fields.Many2one(string="Stock Clients", comodel_name="customer.stock")
    crm_lead_id = fields.Many2one(string="Opportunité", comodel_name="crm.lead")

    def _prepare_invoice_line_vals(self):
        '''
            Retourne dictionnaire de valeur pour les lignes de facture
        '''
        return {
            'product_id' : self.product_id.id,
            'name' : f"{self.product_id.display_name}",
            'quantity' : self.quantity_done,
            'tax_ids': self.product_id.taxes_id.ids,
            'product_uom_id': self.product_uom.id,
            'price_unit' : self.product_id.lst_price,
        }
    
    def _prepare_customer_stock_line_vals(self, picking, location, customer_stock):
        '''
            Retourne dictionnaire de valeur pour les lignes de stocks clients
        '''
        return {
            'name' : f"{self.product_id.display_name} : {picking.name} > {customer_stock.name}",
            'customer_stock_id' : customer_stock.id,
            'move_id' : self.id,
            'picking_id' : picking.id,
            'product_id' : self.product_id.id,
            'location_id' : location.id,
            'entry_date' : fields.Datetime.today() + timedelta(hours=11),
            'entry_quantity' : self.quantity_done,
            'product_uom_id' : self.product_uom.id,
        }
    
    def _create_customer_stock_lines(self, picking, location, customer_stock):
        '''
            Créer les ligne des stocks clients 
        '''
        customer_stock_lines = []
        
        for line in self:
            vals = self._prepare_customer_stock_line_vals(picking, location, customer_stock)
            customer_stock_lines.append(vals)

        _logger.warning(customer_stock_lines)
        if customer_stock_lines:
            self.env['customer.stock.line'].create(customer_stock_lines)

class StockLocation(models.Model):
    _inherit = "stock.location"

    def name_get(self):
        _logger.warning(self._context.get('shortname'))
        _logger.warning(self._context)
        if self._context.get('shortname'):
            res = []
            for record in self:
                name = record.name
                res.append((record.id, name))
            return res
        else:
            return super(StockLocation, self).name_get()

    

            
                    