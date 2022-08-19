from odoo import api,fields, models, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class PurchaseOrderReport(models.AbstractModel):
    _name = "report.purchase.report_purchaseorder"
    _description = "Warning if purchase order state is not in purchase order"
     
    @api.model
    def _get_report_values(self, docids, data=None):
        purchases = self.env['purchase.order'].browse(docids)
        for purchase in purchases:
            _logger.error("Name : " + purchase.name + "| State : " +purchase.state)
            if purchase.state not in ('purchase','done'):
                raise UserError("Impossible d'imprimer le bon de commande car le document n'en est pas un")
        return {
            'doc_ids': docids,
            'doc_model': 'purchase.report',
            'docs': purchases,
        }
