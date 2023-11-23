# -*- coding: utf-8 -*-
{
    "name": "Revatua",
    "summary": "Ajout des fonctionnalité en liens à Revatua (création de connaissement, visualisation des planing bateau, etc...)",
    "version": "15.3.0.0.2",
    "category": "Pacific-ERP",
    "author": "Mehdi Tepava",
    'website': "https://www.pacific-erp.com/",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": ['sale','sale_stock','sale_management','account','account_accountant','stock','purchase','pe_commune_ile','account_edi','pe_sale_order'],
    "data": [
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "data/account_journal.xml",
        "data/account_tax_data.xml",
        "data/ir_actions_report.xml",
        "data/account_move_adm_sequence.xml",
        "data/udm_data.xml",
        "data/decimal_precision.xml",
        "report/external_layout_standard.xml",
        "report/bon_livraison_template.xml",
        "report/devis_commande_template.xml",
        "report/facture_template.xml",
        "report/connaissement_template.xml",
        "report/admg_template.xml",
        "report/sale_order_portal.xml",
        "report/sale_order_portal_template.xml",
        "wizard/sale_line_full_detail_view.xml",
        "views/ir_setting.xml",
        "views/contact_partner.xml",
        "views/menuitems.xml",
        "views/product_template.xml",
        "views/sale_order.xml",
        "views/stock_picking.xml",
        "views/account_move.xml",
        "views/accocunt_move_adm.xml",
        ],
}