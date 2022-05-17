# -*- coding: utf-8 -*-
{
    "name": "Revatua",
    "summary": "Ajout des fonctionnalité en liens à Revatua (création de connaissement, visualisation des planing bateau, etc...)",
    "version": "15.0.0.2.0",
    "category": "Pacific-ERP",
    "author": "Mehdi Tepava",
    'website': "https://www.pacific-erp.com/",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": ['account','stock','purchase','sale_management'],
    "data": [
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "views/setting_inherits.xml",
        "views/menuitems_inherit.xml",
        "views/product_template_inherit.xml",
        "views/sale_order_inherit.xml",
        ],
}
