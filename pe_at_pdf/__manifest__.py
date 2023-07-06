# -*- coding: utf-8 -*-
{
    "name": "Pacific-ERP: Aremiti custom PDF",
    "summary": "PDF société aremiti uniquement",
    "version": "0.0.3",
    "category": "Uncategorized",
    "author": "Mehdi Tepava",
    'website': "https://www.pacific-erp.com/",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": ["sale","account","stock","pe_revatua"],
    "data": [
        "data/at_paperformat.xml",
        "views/base_document_layout.xml",
        "report/at_custom_layout_header_footer.xml",
        "report/at_custom_layout.xml",
        "report/at_report_saleorder_document.xml",
        "report/at_report_invoice_document.xml",
        "report/report_invoice_with_payments.xml",
        "report/report_saleorder.xml",
    ],
}