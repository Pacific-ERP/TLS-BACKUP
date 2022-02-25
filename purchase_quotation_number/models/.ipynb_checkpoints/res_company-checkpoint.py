# -*- coding: utf-8 -*-
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    purchase_rfq = fields.Boolean(string="Purchase RFQ différenciation",
        help="Si c'est décoché les demande de prix (achat - QO) seront nommé différément des bon de commande (achat - P)",
        default=True,
    )

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    purchase_rfq = fields.Boolean(related="company_id.purchase_rfq", readonly=False)
