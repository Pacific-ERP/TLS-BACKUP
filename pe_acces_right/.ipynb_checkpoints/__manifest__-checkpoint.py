# -*- coding: utf-8 -*-
{
    "name": "Custom access",
    "summary": "restricted acces for group of user",
    "version": "0.1",
    "category": "Pacific-ERP",
    "author": "Mehdi Tepava",
    'website': "https://www.pacific-erp.com/",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": ["purchase"],
    "data": [
        "security/security_groups.xml",
        "views/purchase_view_inherit.xml"
        ],
}
