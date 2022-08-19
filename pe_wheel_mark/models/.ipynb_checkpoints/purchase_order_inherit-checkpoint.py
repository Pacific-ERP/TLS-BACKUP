# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError

_logger = logging.getLogger(__name__)

class PurchaseOrderInherit(models.Model):
    _inherit = "purchase.order"
    
    one_article_wheelmark = fields.Boolean(string='Articles Wheelmark', compute='_check_wheelmark', default=False)
    
    @api.depends('order_line.product_id.x_studio_barre_roue')
    def _check_wheelmark(self):
        for order in self:
            if order.order_line and any(line.product_id.x_studio_barre_roue for line in order.order_line):
                order.one_article_wheelmark = True
            else:
                order.one_article_wheelmark = False
    
    def button_confirm_wheelmark(self):
        return super(PurchaseOrderInherit,self).button_confirm()
    
    def action_rfq_send_wheelmark(self):
        return super(PurchaseOrderInherit,self).action_rfq_send()
    
    def print_quotation_wheelmark(self):
        return super(PurchaseOrderInherit,self).print_quotation()
    
    def button_approve_wheelmark(self, force=False):
        return super(PurchaseOrderInherit,self).button_approve(force=force)