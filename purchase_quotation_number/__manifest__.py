# -*- coding: utf-8 -*-
{
    "name": "Purchase RFQ number",
    "summary": "Différencie les demande de prix (achat) et les bon de commande (achat)",
    "version": "0.1",
    "category": "Purchase",
    "author": "Mehdi Tepava",
    'website': "https://www.pacific-erp.com/",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": ["purchase"],
    "data": [
        #Création de la séquence dans le modèle ir.sequence
        "data/purchase_rfq_sequence.xml",
        #Ajout de case à coché pour activer/désactiver l'option de différentiation
        "views/purchase_number_setting.xml",
        ],
}
