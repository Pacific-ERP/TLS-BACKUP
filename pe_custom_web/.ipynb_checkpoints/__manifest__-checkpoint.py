# -*- coding: utf-8 -*-
{
    "name": "Pacific-ERP : Personalisation custom web",
    "summary": "Regroupe toutes les modifications de rapport fait sur la base (PDF,étiquette article, page web,etc...) ",
    'description': """
        Listing:
            - Partie portail clients (devis, bon de commande) ajouter les totaux
            - Partie 
    """,
    "version": "0.0.1",
    "category": "Uncategorized",
    "author": "Mehdi Tepava",
    'website': "https://www.pacific-erp.com/",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": ["sale","website_crm_partner_assign"],
    "data": [
        "report/portal_my_orders.xml",
        "report/portal_my_quotations.xml",
        "report/portal_my_opportunity.xml",
        "report/portal_my_opportunities.xml",
        ],
}