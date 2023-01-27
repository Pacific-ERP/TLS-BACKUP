# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class CrmLeadInherit(models.Model):
    _inherit = "crm.lead"
    
    @api.depends('purchase_ids')
    def _compute_purchases_number(self):
        for crm in self:
            counter = 0
            if crm.purchase_ids:
                counter = len(crm.purchase_ids)
            crm.pe_purchase_counter = counter
        
    invoice_ids = fields.One2many(string='Factures', comodel_name='account.move',inverse_name='opportunity_id', domain="[('opportunity_id','=',False)]")
    purchase_ids = fields.Many2many(string='Achats', comodel_name='purchase.order')
    pe_purchase_counter = fields.Integer(string='Compteur achat', compute='_compute_purchases_number')
    
    # Méthode du bouton de création d'un achat principe copier de la création d'un devis
    def action_purchase_quotations_new(self):
        if not self.partner_id:
            raise UserError('Il est nécéssaire de renseigner le clients pour générer un')
        else:
            return self.action_pe_new_po()
    
    # Méthode du bouton de création d'un achat principe copier de la création d'un devis
    def action_pe_new_po(self):
        action = self.env["ir.actions.actions"]._for_xml_id("pe_crm_purchase.purchase_action_quotations_new")
        action['context'] = {
            'search_default_opportunity_id': self.id,
            'default_opportunity_ids': [(4,self.id)],
            'search_default_partner_id': self.partner_id.id,
            'default_campaign_id': self.campaign_id.id,
            'default_medium_id': self.medium_id.id,
            'default_origin': self.name,
            'default_source_id': self.source_id.id,
            'default_company_id': self.company_id.id or self.env.company.id,
            'default_journal_id' : 1,
            'default_invoice_user_id': self.user_id.id,
            'default_invoice_date': fields.Datetime.now(),
            'default_x_studio_priorit_de_la_commande' : self.x_studio_priorit_de_la_commande,
        }
        if self.team_id:
            action['context']['default_team_id'] = self.team_id.id,
        if self.user_id:
            action['context']['default_user_id'] = self.user_id.id
        return action
    
    # Permet de visualiser les achats
    def action_view_purchase_orders(self):
        self.ensure_one()
        purchase_order_ids = self.purchase_ids.ids
        action = {
            'res_model': 'purchase.order',
            'type': 'ir.actions.act_window',
        }
        if len(purchase_order_ids) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': purchase_order_ids[0],
            })
        else:
            action.update({
                'name': ("Achat lié à %s", self.name),
                'domain': [('id', 'in', purchase_order_ids)],
                'view_mode': 'tree,form',
            })
        return action