# -*- coding: utf-8 -*-
{
    "name": "Pacific-ERP: Customisation module Stock",
    "summary": "Modification fait dans le module achat",
    'description': """
        Long description of module's purpose
    """,
    "version": "15.0.0.0.1",
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