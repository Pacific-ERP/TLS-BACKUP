# -*- coding: utf-8 -*-
{
    "name": "Pacific-ERP: Gestion internes des stocks clients",
    "summary": "Permet la gestion du stock clients, jusqu'a la récupération imédiate ou différé des produits suivis d'une facture",
    "version": "0.0.1",
    "category": "Uncategorized",
    "author": "Mehdi Tepava",
    'website': "https://www.pacific-erp.com/",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": ["stock","crm", "pe_crm_purchase", "pe_crm"],
    "data": [
        "security/ir.model.access.csv",
        "views/stock_picking.xml",
        "wizard/customer_stock_wizard_view.xml"
        ],
}