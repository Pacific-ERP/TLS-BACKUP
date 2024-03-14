# -*- coding: utf-8 -*-
{
    'name': "Pacific-ERP Customs",
    'summary': """
        Ajout des différentes modifications hors studio""",
    'description': """
        Listing:
        - Rajout de champs Vente/Achat/Compta (Poids, Volume, Pays de provenance, Mode acheminement, Incoterms à déplacer)
        - Rajout de champs Articles (Code douanier, Référence constructeur)
        - Champs téléphone et email obligatoire sur contacts
        - Ajout de documents à envoyer pour le follow-ups (rapport de suivi)
        - Ajout de la remise dans les lignes comptables pour filtre
        - Restriction sur remise avec un champs limite
    """,
    'author': "Mehdi Tepava",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '15.0.0.0.1',
    'depends': ['purchase','account','pe_revatua','account_followup'],
    'data': [
        'views/account_move.xml',
        'views/res_partner.xml',
        'views/purchase_order.xml',
        'views/product_template.xml',
        'security/security_groups.xml',
    ],
    "license": "LGPL-3",
}
