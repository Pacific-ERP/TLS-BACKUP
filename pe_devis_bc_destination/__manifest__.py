# -*- coding: utf-8 -*-
{
    "name": "Ventes : Ajout de champs (destination,bon commande)",
    "summary": "Pacific-ERP : devis bc et destination",
    "version": "15.0.0.0.1",
    "category": "Pacific-ERP",
    "author": "Mehdi Tepava",
    'website': "https://www.pacific-erp.com/",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": ["sale_management","base"],
    "data": [
        "views/sale_form_inherit.xml",
        "views/account_form_inherit.xml",
        "views/destination_views.xml",
        "security/ir.model.access.csv",
        "views/menuitem.xml",
        ],
}
