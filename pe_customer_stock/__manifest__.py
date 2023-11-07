# -*- coding: utf-8 -*-
{
    "name": "Pacific-ERP: Gestion internes des stocks clients",
    "summary": "Permet la gestion du stock clients, jusqu'a la récupération imédiate ou différé des produits suivis d'une facture",
    "version": "1.0.1",
    "category": "Uncategorized",
    "author": "Mehdi Tepava",
    'website': "https://www.pacific-erp.com/",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": ["stock","crm","account","pe_crm_purchase", "pe_crm"],
    "data": [
        "views/res_partner.xml",
        # "security/ir.model.access.csv",
        # "data/product_template.xml",
        # "views/menuitem.xml",
        # "views/customer_stock.xml",
        # "wizard/customer_stock_wizard_view.xml",
        # "wizard/customer_stock_deliver_wizard_view.xml"
        ],
}