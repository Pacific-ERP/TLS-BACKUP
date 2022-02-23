# © 2010-2012 Andy Lu <andy.lu@elico-corp.com> (Elico Corp)
# © 2013 Agile Business Group sagl (<http://www.agilebg.com>)
# © 2017 valentin vinagre  <valentin.vinagre@qubiq.es> (QubiQ)
# © 2020 Manuel Regidor  <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    purchase_name_rfq = fields.Boolean(string="Purchase RFQ différenciation",
        help="If this is unchecked, quotations use a different sequence from "
        "sale orders",
        default=True,
    )

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    purchase_name_rfq = fields.Boolean(related="company_id.purchase_name_rfq", readonly=False)