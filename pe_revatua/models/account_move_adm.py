# -*- coding: utf-8 -*-
import logging
from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class AccountMoveAdm(models.Model):
    _name = 'account.move.adm'
    _description = 'Historique des facture grouper pour les administrations'
    
    name = fields.Char(string='Numéro', store=True, readonly=True, copy=False)
    start_date = fields.Date(string='Du', store=True, copy=False)
    end_date = fields.Date(string='Au', store=True, copy=False)
    partner_id = fields.Many2one(string='Client', store=True, comodel_name='res.partner')
    company_id = fields.Many2one('res.company', string='Company', readonly=True, states={'draft': [('readonly', False)], 'refused': [('readonly', False)]}, default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string='Currency')
    state = fields.Selection(string='État de facturation', selection=[('no','Aucun paiement'),
                                                                      ('in_payment','Paiement partiel'),
                                                                      ('invoiced','Paiement complet')]
                             ,store=True, default='no', copy=False)
    
    invoice_line_ids = fields.One2many(string='Factures ADM', store=True, comodel_name='account.move', inverse_name='adm_group_id')
    product_line_ids = fields.One2many(string='Articles', store=True, comodel_name='account.move.adm.line', inverse_name='invoice_id')
    
class AccountMoveAdmLine(models.Model):
    _name = 'account.move.adm.line'
    _description = 'Ligne des facture grouper pour les administrations'
    
    invoice_id = fields.Many2one(string='Facture globale', comodel_name='account.move.adm')
    
    # Article
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    product_id = fields.Many2one(
        'product.product', string='Product', domain="[('sale_ok', '=', True), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        change_default=True, ondelete='restrict', check_company=True)  # Unrequired company
    product_template_id = fields.Many2one(
        'product.template', string='Product Template',
        related="product_id.product_tmpl_id", domain=[('sale_ok', '=', True)])
    quantity = fields.Float(string='Quantité', default=0.0, store=True)
    
    # Prix
    price_unit = fields.Float('Unit Price', required=True, digits='Product Price', default=0.0)
    currency_id = fields.Many2one(related='invoice_id.currency_id', depends=['invoice_id.currency_id'], store=True, string='Currency')
    price_subtotal = fields.Monetary(string='Subtotal', store=True)
    tax_id = fields.Many2many('account.tax', string='Taxes', context={'active_test': False})
    price_tax = fields.Float(string='Total Tax', store=True)
    price_total = fields.Monetary(string='Total', store=True)
    
    # Revatua
    tarif_rpa = fields.Float(string='RPA', default=0, required=True, store=True)
    tarif_maritime = fields.Float(string='Maritime', default=0, required=True, store=True)
    tarif_terrestre = fields.Float(string='Terrestre', default=0, required=True, store=True)
    r_volume = fields.Float(string='Volume Revatua (m³)', default=0, store=True)
    r_weight = fields.Float(string='Volume weight (T)', default=0, store=True)
    revatua_uom = fields.Char(string='Udm', store=True)
    check_adm = fields.Boolean(string='Payé par ADM', related="product_id.check_adm")