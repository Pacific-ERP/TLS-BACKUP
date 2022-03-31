# -*- coding: utf-8 -*-

from odoo import fields, models, api

class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'

    #purchase_id_pe = fields.Many2one('purchase.order', string="Purchase Orders (PE)" ,compute='_get_purchase_id', readonly=True, store=True) 
    
    @api.depends('state')
    def _get_purchase_id(self):
        for stock in self:
            if stock.state and stock.state == 'done':
                stock.purchase_id.x_studio_full_reception = str(stock.id) + 'Good;'
            else:
                stock.purchase_id.x_studio_full_reception = 'Not good bruh'