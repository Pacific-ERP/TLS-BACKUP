# -*- coding: utf-8 -*-
{
    "name": "Pacific-ERP: Aremiti custom PDF",
    "summary": "PDF société aremiti uniquement",
    "version": "0.0.1",
    "category": "Uncategorized",
    "author": "Mehdi Tepava",
    'website': "https://www.pacific-erp.com/",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": ["sale","account","stock"],
    "data": [
        "report/at_custom_layout_header_footer.xml",
        "report/at_custom_layout.xml",
        "report/at_report_saleorder_document.xml",
        "report/report_saleorder.xml",
    ],
}