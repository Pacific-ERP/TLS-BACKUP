# -*- coding: utf-8 -*-
{
    "name": "Pacific-ERP: Customisation module Stock",
    "summary": "Modification fait dans le module stock",
    'description': """
        - Modifier la méthoded de calcul d'arrondis erreur car arrondi à 0
    """,
    "version": "15.0.0.0.2",
    "category": "Uncategorized",
    "author": "Mehdi Tepava",
    'website': "https://www.pacific-erp.com/",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": ["stock"],
    "data": [
        "security/res_group.xml",
        "security/ir.model.access.csv",
        "views/product_emplacement_view.xml",
        "views/product_template.xml",
        ],
}