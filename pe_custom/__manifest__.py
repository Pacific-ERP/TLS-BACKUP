# -*- coding: utf-8 -*-
{
    'name': "Pacific-ERP Customs",
    'summary': """
        Ajout des différentes modifications hors studio""",
    'description': """
        Listing:
        - Rajout de champs Vente/Achat/Compta (Poids, Volume, Pays de provenance, Mode acheminement, Incoterms à déplacer)
        - Rajout de champs Articles (Code douanier, Référence constructeur)
    """,
    'author': "Mehdi Tepava",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '15.0.0.0.1',
    'depends': ['purchase','account','pe_revatua'],
    'data': [
        'views/account_move.xml',
        'views/purchase_order.xml',
        'views/product_template.xml',
    ],
    "license": "LGPL-3",
}