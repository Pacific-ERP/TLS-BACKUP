# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api

_logger = logging.getLogger(__name__)

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    transport_type = fields.Selection(string="Mode d'acheminement", selection=[('plane','Avion'),
                                                                               ('boat','Bateau'),
                                                                               ('terreste','Terrestre')]
                                      , default=False, copy=False)
    
    provenance = fields.Many2one(string="Provenance", comodel_name="res.country")

    def _prepare_invoice(self):
        # OVERRIDE #
        res = super(PurchaseOrder, self)._prepare_invoice()
        res['transport_type'] = self.transport_type
        res['provenance'] = self.provenance
        return res
    
class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    pe_poid = fields.Float(string="Poids", default=0.0)
    pe_volume = fields.Float(string="Volume", default=0.0)
    
    def _prepare_account_move_line(self, move=False):
        # OVERRIDE #
        res = super(PurchaseOrderLine, self)._prepare_account_move_line(move)
        res['r_volume'] = self.pe_poid
        res['r_weight'] = self.pe_volume
        return res

    
    