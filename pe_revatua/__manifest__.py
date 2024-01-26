# -*- coding: utf-8 -*-
{
    "name": "Workflow Aremiti Transport",
    "summary": "Workflow Aremiti transport : Vente de service de transport avec calcul automatique des parts terrestre/maritime et prise en compte de la taxe RPA",
    "version": "15.4.0.0.3",
    "category": "Pacific-ERP",
    "author": "Mehdi Tepava",
    'website': "https://www.pacific-erp.com/",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": ['sale',
                'sale_stock',
                'sale_management',
                'account',
                'account_accountant',
                'stock','purchase',
                'pe_commune_ile',
                'account_edi',
                'pe_sale_order'],
    "data": [
        "data/account_journal.xml",
        "data/account_tax_data.xml",
        "data/udm_data.xml",
        "data/decimal_precision.xml",
        "views/ir_setting.xml",
        "views/res_partner.xml",
        "views/product_template.xml",
        "views/sale_order.xml",
        "views/account_move.xml",
        ],
}