# -*- coding: utf-8 -*-
from odoo import api, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def create(self, vals):
        if self.is_using_quotation_number(vals):
            sequence = self.env["ir.sequence"].next_by_code("purchase.order")
            vals["name"] = sequence or "/"
        return super(PurchaseOrder, self).create(vals)

    @api.model
    def is_using_quotation_number(self, vals):
        company = False
        if "company_id" in vals:
            company = self.env["res.company"].browse(vals.get("company_id"))
        else:
            company = self.env.company
        return not company.purchase_rfq
    
    #extend de l'action dupliquer
    def copy(self, default=None):
        self.ensure_one()
        if default is None:
            default = {}
        if self.origin and self.origin != "":
            default["origin"] = self.origin + ", " + self.name
        else:
            default["origin"] = self.name
        return super(PurchaseOrder, self).copy(default)
    
    #extend de l'action confirmation du rfq en bdc
    def button_confirm(self):
        for purchase in self:
            #Si name = P -> Continue
            if self.name[:2] != "QO":
                continue
            #Si état n'est pas draft ou sent ou que l'option différenciation est activé -> Continue
            if purchase.state not in ("draft", "sent") or purchase.company_id.purchase_rfq:
                continue
            #si origin existe et qu'il n'est pas vide -> quo = origin , name
            if purchase.origin and purchase.origin != "":
                quo = purchase.origin + ", " + purchase.name
            else:
                quo = purchase.name
            sequence = self.env["ir.sequence"].next_by_code("purchase.po")
            purchase.write({"origin": quo, "name": sequence})
        return super().button_confirm()
