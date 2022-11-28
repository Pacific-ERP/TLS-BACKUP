# -*- coding: utf-8 -*-
{
    "name": "Custom access",
    "summary": "restricted acces for group of user",
    'description': """
        Modification :
        - Retire le bouton création de facture dans le module Achat pour les utilisateur du groupes "Achats / Pas de creation facture"
        - Retire le bouton confirmation des facture dans le module Facturation pour les utilisateur du groupes "Achats / Pas de confirmation"
        - Retire les onglet autres que 'informations générale au groupe "Inventaire / Modif article limité"
    """,
    "version": "0.3",
    "category": "Pacific-ERP",
    "author": "Mehdi Tepava",
    'website': "https://www.pacific-erp.com/",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": ["purchase","stock"],
    "data": [
        "security/security_groups.xml",
        "views/purchase_view_inherit.xml",
        "views/product_template.xml"
        ],
}
