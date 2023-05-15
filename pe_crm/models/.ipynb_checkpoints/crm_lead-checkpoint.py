# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

# Opportunité
class CrmLead(models.Model):
    _inherit = "crm.lead"
    
    crm_status = fields.Char(string='Status', compute="_get_crm_status")
    eta_date = fields.Datetime(string='ETA')
    customer_desc = fields.Text('Description')
    pe_sale_counter = fields.Integer(compute='_pe_compute_sale_order_count')
    
    # Permet de récupérer le status en text directe
    @api.depends('stage_id')
    def _get_crm_status(self):
        for crm in self:
            if crm.stage_id:
                crm.crm_status = crm.stage_id.name
            else:
                crm.crm_status = ''
    
    @api.onchange('stage_id')
    def _onchange_stage_id(self):
        if not self.name:
            default_stage = self.env['crm.stage'].sudo().search([('company_id','=', self.company_id.id),('is_default_stage','=', True)])
            if default_stage:
                self.stage_id = default_stage.id
    
    # Permet d'auto assigner le client à l'opportunité
    @api.model_create_multi
    def create(self, vals_list):
        # Override #
        res = super(CrmLead, self).create(vals_list)
        for crm in res:
            if crm.partner_id.grade_id:
                crm.partner_assigned_id = crm.partner_id
            if not crm.company_id:
                crm.company_id = self.env.company.id            
            if crm.company_id:
                default_stage = self.env['crm.stage'].sudo().search([('company_id','=', crm.company_id.id),('is_default_stage','=', True)])
                if default_stage:
                    res.stage_id = default_stage.id
        return res
    
    def copy(self, default=None):
        # OVERRIDE
        res = super(CrmLead, self).copy(default)
        default_stage = self.env['crm.stage'].sudo().search([('company_id','=', self.company_id.id),('is_default_stage','=', True)])
        if default_stage:
            res.stage_id = default_stage.id
        return res
    
    # Compteur pour les devis
    def _pe_compute_sale_order_count(self):
        for record in self:
            record.pe_sale_counter = 0
            if record.order_ids:
                record.pe_sale_counter = len(record.order_ids)
                
    def action_view_sale_order(self):
        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_orders")
        action['context'] = {
            'search_default_partner_id': self.partner_id.id,
            'default_partner_id': self.partner_id.id,
            'default_opportunity_id': self.id,
        }
        action['domain'] = [('opportunity_id', '=', self.id), ('state', '!=', 'cancel')]
        orders = self.mapped('order_ids').filtered(lambda l: l.state != 'cancel')
        if len(orders) == 1:
            action['views'] = [(self.env.ref('sale.view_order_form').id, 'form')]
            action['res_id'] = orders.id
        return action

from odoo import fields, models

# Etape des CRM
class CrmStage(models.Model):

    _inherit = "crm.stage"

    company_id = fields.Many2one(string="Company", comodel_name="res.company", default=lambda self: self.env.company.id, index=True)
    is_default_stage = fields.Boolean(string="Etape par défaut", default=False)
    
    @api.onchange('is_default_stage')
    def _onchange_is_default_stage(self):
        # Il peut y avoir qu'une seule étape par défaut
        another_onchange = self.env['crm.stage'].search([('company_id','=', self.company_id.id),('is_default_stage','=', True),('id','!=', self._origin.id)])
        if another_onchange:
            another_onchange.is_default_stage = False
        elif not self.is_default_stage and not another_onchange:
            raise UserError('Vous devez définir au moins une étape par défaut si vous voulez retirez')