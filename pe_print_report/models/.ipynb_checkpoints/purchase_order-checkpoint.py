# -*- coding: utf-8 -*-
import logging
from odoo import api, models, fields

_logger = logging.getLogger(__name__)

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    pdf_name_po = fields.Char(string='PDF file name PO', compute='pdf_format_name', readonly=True, store=True)
    pdf_name_qo = fields.Char(string='PDF file name QO', compute='pdf_format_name', readonly=True, store=True)
    check_text = fields.Boolean(string="Launch Def",default=False, store=True)
    field_reload_compute = fields.Char(string='Reload compute')
    
    """"
    Voir la gestion multisociété activer l'action    
    """
    @api.depends('field_reload_compute','check_text','x_studio_socit_demandeuse','partner_id','name','state')
    def pdf_format_name(self):
        for purchase in self:
            if purchase.state and purchase.name != 'New':
                name = purchase.name.replace("/","-")
                fournisseur = ''
                societe_demandeuse = ''
                state = ''
                if purchase.partner_id.company_type == 'company':	
                    fournisseur = purchase.partner_id.name
                else:
                    fournisseur = purchase.partner_id.parent_id.name
                if purchase.x_studio_socit_demandeuse:
                    societes = purchase.x_studio_socit_demandeuse.sorted()
                    for societe in societes:
                        # récupération du nom de la société au lieu de passer par 
                        if societe.company_type == 'company':
                            societe_demandeuse = societe_demandeuse + '-' + societe.name
                        elif societe.parent_id.name:
                            societe_demandeuse = societe_demandeuse + '-' + societe.parent_id.name
                        else:
                            societe_demandeuse = societe_demandeuse + '-' + societe.name
                            # String formating python
                if purchase.state in ('draft','sent'):
                    state = 'Demande de prix'
                    purchase.pdf_name_qo = "%s-%s%s-%s" % (name,fournisseur,societe_demandeuse,state)
                elif purchase.state not in ('draft','sent'):
                    state = 'Bon de commande'
                    purchase.pdf_name_po = "%s-%s%s-%s" % (name,fournisseur,societe_demandeuse,state)
                    if not purchase.pdf_name_qo and purchase.origin:
                        name = purchase.origin.replace("/","-")
                        state = 'Demande de prix'
                        purchase.pdf_name_qo = "%s-%s%s-%s" % (name,fournisseur,societe_demandeuse,state)   
                    elif purchase.pdf_name_qo and purchase.origin:
                        name = purchase.origin.replace("/","-")
                        state = 'Demande de prix'
                        purchase.pdf_name_qo = "%s-%s%s-%s" % (name,fournisseur,societe_demandeuse,state)
                            
# à mettre sur les rapport nom du fichier action>rapport ne pas oublier les traduction éviter tout problème:

# Bon de commande (purchase.order)
#(object.pdf_name_po) and '%s' % (object.pdf_name_po) or '%s - Bon de comamnde' % (object.name)

# Demande de prix (purchase.order)
#(object.pdf_name_qo) and '%s' % (object.pdf_name_qo) or '%s - Demande de prix' % (object.name)

# Devis / Commande:
#(object.state in ('draft', 'sent') and '%s-%s-Devis - ' % (object.name,object.partner_id.name)) or '%s-Commande  ' % (object.name)