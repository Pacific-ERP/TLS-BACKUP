# © 2010-2012 Andy Lu <andy.lu@elico-corp.com> (Elico Corp)
# © 2013 Agile Business Group sagl (<http://www.agilebg.com>)
# © 2017 valentin vinagre  <valentin.vinagre@qubiq.es> (QubiQ)
# © 2020 Manuel Regidor  <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def create(self, vals):
        if self.is_using_quotation_number(vals):
            sequence = self.env["ir.sequence"].next_by_code("purchase.rfq")
            vals["name"] = sequence or "/"
        return super(PurchaseOrder, self).create(vals)

    @api.model
    def is_using_quotation_number(self, vals):
        company = False
        if "company_id" in vals:
            company = self.env["res.company"].browse(vals.get("company_id"))
        else:
            company = self.env.company
        return not company.purchase_name_rfq

    def copy(self, default=None):
        self.ensure_one()
        if default is None:
            default = {}
        if self.origin and self.origin != "":
            default["origin"] = self.origin + ", " + self.name
        else:
            default["origin"] = self.name
        return super(PurchaseOrder, self).copy(default)

    def action_confirm(self):
        for purchase in self:
            if self.name[:2] != "QO":
                continue
            if purchase.state not in ("draft", "sent") or purchase.company_id.purchase_name_rfq:
                continue
            if purchase.origin and purchase.origin != "":
                quo = purchase.origin + ", " + purchase.name
            else:
                quo = purchase.name
            sequence = self.env["ir.sequence"].next_by_code("purchase.rfq")
            purchase.write({"origin": quo, "name": sequence})
        return super().action_confirm()
