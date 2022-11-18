# -*- coding: utf-8 -*-
{
    "name": "Pacific-ERP : Liens Achat et CRM",
    "summary": "Lie le module CRM au module Achats avec automatisme de status",
    "version": "15.0.0.0.5",
    "category": "Pacific-ERP",
    "author": "Mehdi Tepava",
    'website': "https://www.pacific-erp.com/",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": ["account","crm","sale_management","purchase"],
    "data": [
        "views/crm_lead_form_inherit.xml",
        "views/account_move_inherit.xml",
        "views/purchase_order_inherit.xml",
        ],
}
