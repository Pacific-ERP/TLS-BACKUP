# -*- coding: utf-8 -*-
{
    "name": "Vente : Ajout des détails d'état de facturation et livraison(PE)",
    "summary": "Récupère l'état d'avancement des facture et livraison lié à la vente et les affiches sur la vue list du modèle ventes",
    "version": "15.0.0.0.2",
    "category": "Pacific-ERP",
    "author": "Mehdi Tepava",
    'website': "https://www.pacific-erp.com/",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": ['account','stock','sale_management','sale_stock'],
    "data": [
        "views/sale_form.xml",
        "views/sale_list.xml",
        ],
}
