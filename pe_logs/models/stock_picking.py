# -*- coding: utf-8 -*-
import logging
from odoo import fields, models, api

_logger = logging.getLogger(__name__)

class SaleOrderInherit(models.Model):
    _inherit = "stock.picking"
    
    reliquat_refuser = fields.Char(string="Reliquat cancel")
    reliquat_accepter = fields.Char(string="Reliquat process")

class StockBackorderConfirmation(models.TransientModel):
    _inherit = 'stock.backorder.confirmation'

    def process(self):
        res = super(StockBackorderConfirmation, self).process()
        picking_ids = self.pick_ids
        if picking_ids:
            for picking in picking_ids:
                picking.reliquat_accepter = 'Reliquat Créer'
        return res

    def process_cancel_backorder(self):
        res = super(StockBackorderConfirmation, self).process_cancel_backorder()
        picking_ids = self.pick_ids
        if picking_ids:
            for picking in picking_ids:
                picking.reliquat_accepter = 'Reliquat refuser'
        return res