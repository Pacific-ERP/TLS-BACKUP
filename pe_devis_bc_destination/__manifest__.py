# -*- coding: utf-8 -*-
{
    "name": "Ventes : Ajout de champs (destination,bon commande)",
    "summary": "Pacific-ERP : devis bc et destinations",
    "version": "15.0.0.0.3",
    "category": "Pacific-ERP",
    "author": "Mehdi Tepava",
    'website': "https://www.pacific-erp.com/",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": ["sale_management","base","crm","sale_crm","account","stock"],
    "data": [
        "report/invoice_report_inherit.xml",
        "views/sale_form_inherit.xml",
        "views/account_form_inherit.xml",
        "views/destination_views.xml",
        "views/crm_lead_form_inherit.xml",
        "security/ir.model.access.csv",
        "views/menuitem.xml",
        ],
}
