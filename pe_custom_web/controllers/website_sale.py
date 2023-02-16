# -*- coding: utf-8 -*-
import logging
from odoo.http import route, request
from odoo.addons.website_sale.controllers import main
from odoo.addons.payment.controllers import post_processing

_logger = logging.getLogger(__name__)

class PaymentPostProcessingExtends(post_processing.PaymentPostProcessing):
    
    @route()
    def display_status(self, **kwargs):
        _logger.error('display_status')
        _logger.error('k : %s' % kwargs)
        return super(PaymentPostProcessingExtends, self).display_status()
    
    @route()
    def poll_status(self):
        _logger.error('poll_status')
        return super(PaymentPostProcessingExtends, self).poll_status()
    
# class WebsiteSaleExtends(main.WebsiteSale):
#     @route()
#     def shop_payment(self, **post):
#         _logger.error('shop_payment')
#         _logger.error('Post : %s' % post)
#         return super(WebsiteSaleExtends, self).shop_payment(**post)
    
#     @route()
#     def shop_payment_validate(self, sale_order_id=None, **post):
#         _logger.error('shop_payment_validate')
#         if sale_order_id is None:
#             order = request.website.sale_get_order()
#             if not order and 'sale_last_order_id' in request.session:
#                 # Retrieve the last known order from the session if the session key `sale_order_id`
#                 # was prematurely cleared. This is done to prevent the user from updating their cart
#                 # after payment in case they don't return from payment through this route.
#                 last_order_id = request.session['sale_last_order_id']
#                 order = request.env['sale.order'].sudo().browse(last_order_id).exists()
#         else:
#             order = request.env['sale.order'].sudo().browse(sale_order_id)
#             assert order.id == request.session.get('sale_last_order_id')
#         _logger.error('Devis : %s' % order)
#         _logger.error('Self : %s' % self)
#         _logger.error('Post : %s' % post)
#         _logger.error('data : %s' % request)
#         _logger.error('data : %s' % request.__dict__)
#         _logger.error('data : %s' % dir(request))
        
#         return super(WebsiteSaleExtends, self).shop_payment_validate(sale_order_id,**post)
    
# class WebsiteSaleExtendsPaymentPortal(main.PaymentPortal):
    
#     @route()
#     def shop_payment_transaction(self, order_id, access_token, **kwargs):
#         _logger.error('shop_payment_transaction')
#         _logger.error('Devis : %s' % order_id)
#         _logger.error('Self : %s' % self)
#         _logger.error('Post : %s' % kwargs)
        
#         return super(WebsiteSaleExtendsPaymentPortal, self).shop_payment_transaction(order_id, access_token, **kwargs)