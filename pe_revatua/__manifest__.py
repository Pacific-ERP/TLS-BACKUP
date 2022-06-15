# -*- coding: utf-8 -*-
{
    "name": "Revatua",
    "summary": "Ajout des fonctionnalité en liens à Revatua (création de connaissement, visualisation des planing bateau, etc...)",
    "version": "15.0.0.6.5",
    "category": "Pacific-ERP",
    "author": "Mehdi Tepava",
    'website': "https://www.pacific-erp.com/",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": ['account','stock','purchase','sale_management'],
    "data": [
        "wizard/account_move_adm_wizard.xml",
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "data/account_tax_data.xml",
        "data/ir_actions_report.xml",
        "views/connaissement_template.xml",
        "views/setting_inherits.xml",
        "views/contact_commune.xml",
        "views/menuitems_inherit.xml",
        "views/view_country_state_tree_inherit.xml",
        "views/product_template_inherit.xml",
        "views/sale_order_form_inherit.xml",
        "views/stock_picking_inherit.xml",
        "views/account_move_form_inherit.xml",
        ],
    'assets': {
        'web.assets_backend': [
            'pe_revatua/static/src/style.css',
        ],
    },
}
