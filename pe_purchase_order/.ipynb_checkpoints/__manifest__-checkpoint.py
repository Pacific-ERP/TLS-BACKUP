# -*- coding: utf-8 -*-
{
    "name": "Ajout des détails d'état de facturation et livraison(PE)",
    "summary": "Récupère l'état d'avancement des facture et livraison lié à l'achat et les affiches sur la vue list du modèle achats",
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
