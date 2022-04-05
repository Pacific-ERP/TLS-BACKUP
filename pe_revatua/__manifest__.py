# -*- coding: utf-8 -*-
{
    "name": "Revatua",
    "summary": "Ajout du module Revatua uniquement pour le groupe d'utilisateur Revatua / Users",
    "version": "0.1",
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
        "views/sale_order_inherit.xml",
        "views/menuitems_inherit.xml",
        "views/product_template_inherit.xml"        
        ],
}