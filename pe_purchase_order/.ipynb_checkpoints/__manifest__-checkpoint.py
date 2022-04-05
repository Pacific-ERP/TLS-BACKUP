# -*- coding: utf-8 -*-
{
    "name": "Custom module Achats (PE)",
    "summary": "Modif non studio (PE)",
    "version": "0.1",
    "category": "Pacific-ERP",
    "author": "Mehdi Tepava",
    'website': "https://www.pacific-erp.com/",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": ['account','stock','purchase','purchase_stock'],
    "data": [
        "views/purchase_form.xml",
        "views/purchase_list.xml",
        ],
}
