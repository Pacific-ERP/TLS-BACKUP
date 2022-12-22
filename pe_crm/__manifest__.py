# -*- coding: utf-8 -*-
{
    "name": "Customisation module CRM (Pacifi-ERP)",
    "summary": "Custom modules regroupant les customisations apporté au modules CRM",
    "version": "15.0.0.0.5",
    "category": "Pacific-ERP",
    "author": "Mehdi Tepava",
    'website': "https://www.pacific-erp.com/",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": ["crm","website_crm_partner_assign"],
    "data": [
        "security/res_group.xml",
        "views/crm_lead.xml",
        "views/crm_restricted.xml",
        ],
}
