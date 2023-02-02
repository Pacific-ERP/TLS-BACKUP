# -*- coding: utf-8 -*-
import logging
from odoo.http import route, request
from odoo.addons.website_sale.controllers import main

_logger = logging.getLogger(__name__)

class WebsiteSaleExtends(main.WebsiteSale):
    @route()
    def shop_payment_validate(self, sale_order_id=None, **post):
        if sale_order_id is None:
            order = request.website.sale_get_order()
            if not order and 'sale_last_order_id' in request.session:
                # Retrieve the last known order from the session if the session key `sale_order_id`
                # was prematurely cleared. This is done to prevent the user from updating their cart
                # after payment in case they don't return from payment through this route.
                last_order_id = request.session['sale_last_order_id']
                order = request.env['sale.order'].sudo().browse(last_order_id).exists()
        else:
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            assert order.id == request.session.get('sale_last_order_id')
        
        _logger.error('Devis : %s' % order)
        _logger.error('Self : %s' % self)
        _logger.error('Post : %s' % post)
            
        return super(WebsiteSaleExtends, self).shop_payment_validate(sale_order_id,**post)