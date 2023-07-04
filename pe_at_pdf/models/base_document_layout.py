# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api

_logger = logging.getLogger(__name__)

class ResCompany(models.Model):
    _inherit = 'res.company'

    contact_bloc = fields.Html(string="Contacts", readonly=False)
    payment_mode_bloc = fields.Html(string="Condition et modalités de paiement", readonly=False)
    other_information_bloc = fields.Html(string="Information additionnelles", readonly=False)
    
class BaseDocumentLayout(models.TransientModel):
    _inherit = "base.document.layout"

    contact_bloc = fields.Html(related='company_id.contact_bloc', readonly=False)    
    payment_mode_bloc = fields.Html(related='company_id.payment_mode_bloc', readonly=False)    
    other_information_bloc = fields.Html(related='company_id.other_information_bloc', readonly=False)