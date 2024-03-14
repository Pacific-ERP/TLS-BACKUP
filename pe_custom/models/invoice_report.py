# -*- coding: utf-8 -*-

from odoo import fields, models


class AccountInvoiceReport(models.Model):
    _inherit = 'account.invoice.report'

    discount = fields.Float(string='Remises(%)')
    discount_amount = fields.Float(string='Montant de la remise')

    def _select(self):
        return super(AccountInvoiceReport, self)._select() + ", line.discount as discount, line.price_unit * (line.discount/100) as discount_amount"