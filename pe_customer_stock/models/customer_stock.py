# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api
from markupsafe import Markup
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

class CustomerStock(models.Model):
    _name = "customer.stock"
    _description = "Stock Clients"

    @api.depends('partner_id')
    def _compute_name(self):
        for custo_stock in self:
            custo_stock.name = custo_stock.partner_id.name
    
    name = fields.Char(string="Description", compute="_compute_name")
    partner_id = fields.Many2one(string="Client", comodel_name="res.partner")
    is_invoiceable = fields.Boolean(string="Facturable", default=True)
    company_id = fields.Many2one(string="Société", comodel_name="res.company")
    
    stock_lines = fields.One2many(string="Ligne stock clients", comodel_name="customer.stock.line",
                                  inverse_name="customer_stock_id", domain=[('to_show','=', True)], context={'shortname': True})
    history_lines = fields.One2many(string="Historique", comodel_name="customer.stock.line",
                                    inverse_name="customer_stock_id", domain=[('to_show','=', False)], context={'shortname': True} )
    
    invoice_ids = fields.One2many(string="Factures", comodel_name="account.move", inverse_name="customer_stock_id")
    picking_ids = fields.One2many(string="Transferts", comodel_name="stock.picking", inverse_name="customer_stock_id")

    # Alimenter grâce au ligne
    opportunity_ids = fields.Many2many(string="Opportunités", comodel_name="crm.lead")

    def _get_custom_link(self):
        return Markup("<a href=# data-oe-model='%s' data-oe-id='%s'>%s</a>") % (
            self._name, self.id, self.name)
        
    def button_to_deliver(self):
        '''
            Ouvre un Wizard pour livré les articles            
        '''
        view = self.env.ref('pe_customer_stock.pe_customer_stock_deliver_wizard_form')
        lines = self.stock_lines.filtered(lambda sl : sl.available_quantity)._prepare_wizard_lines()
        return {
            'name': ('Livraison Client'),
            'type': 'ir.actions.act_window',
            'res_model': 'customer.stock.deliver.wizard',
            'views': [(view.id, 'form')],
            'target': 'new',
            'context': {
                'default_customer_stock_id': self.id,
                'default_wizard_lines': lines,
                'default_origin': f"Stock : {self.partner_id.name}",
                'default_company_id': 1}
        } 
    
class CustomerStockLine(models.Model):
    _name = "customer.stock.line"
    _description = "Ligne de Stock Client"

    name = fields.Char(string="Description")
    picking_id = fields.Many2one(string="Transfert", comodel_name="stock.picking")
    move_id = fields.Many2one(string="Move", comodel_name="stock.move")
    customer_stock_id = fields.Many2one(string="Stock Clients", comodel_name="customer.stock")

    product_id = fields.Many2one(string="Article", comodel_name="product.product")
    location_id = fields.Many2one(string="Emplacement", comodel_name="stock.location")
    to_invoice = fields.Boolean(string="À Facturé", default=False)
    entry_date = fields.Datetime(string="Entrée en stock")
    entry_quantity = fields.Float(string="Qté entrée")
    entry_volume = fields.Float(string="Vol entrée")
    product_uom_id = fields.Many2one('uom.uom', 'UdM', domain="[('category_id', '=', product_uom_category_id)]")
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
    
    available_quantity = fields.Float(string="Qté restante", compute="_compute_available_quantity", store=True)
    available_volume = fields.Float(string="Vol restant", compute="_compute_available_quantity", store=True)
    to_show = fields.Boolean(string="À afficher", compute="_compute_available_quantity", store=True)
    is_invoiceable = fields.Boolean(string="Facturable", compute="_compute_available_quantity", store=True)
    
    exit_dates = fields.One2many(string="Sortie de stock", comodel_name="customer.stock.line.exit.dates", inverse_name="customer_stock_line_id")

    def _compute_default_exit_date(self):
        return fields.Datetime.now()
    
    @api.depends('exit_dates','entry_quantity','entry_volume')
    def _compute_available_quantity(self):
        for line in self:
            available_volume = line.entry_volume if line.entry_volume else 0.0
            available_quantity = line.entry_quantity if line.entry_quantity else 0.0
            if line.exit_dates:
                available_quantity -= sum(exit.exit_quantity for exit in line.exit_dates)
                available_volume -= sum(exit.exit_volume for exit in line.exit_dates)
            
            line.available_quantity = available_quantity
            line.available_volume = available_volume

            # La ligne est à afficher et facturé si une quantité est encore disponible
            show_and_invoice = True if available_quantity > 0 else False
            line.is_invoiceable = line.to_show = show_and_invoice

    def _compute_delta_day(self, exit_date):
        delta = 0
        if self.entry_date and exit_date:
            if exit_date > self.entry_date:
                delta = (exit_date - self.entry_date).days

        if delta > 0 and delta < 1 or delta <= 0:
            delta = 1    
            
        return delta
    
    def _prepare_wizard_lines(self):
        lines = []
        exit_date = self._compute_default_exit_date()
        for line in self:
            delta_day = line._compute_delta_day(exit_date)
            lines.append((0, 0, {
                'customer_stock_line_id': line.id,
                'product_id': line.product_id.id,
                'location_id': line.location_id.id,
                'entry_date': line.entry_date,
                'exit_date': exit_date,
                'product_uom_id': line.product_uom_id.id,
                'quantity': line.available_quantity,
                'max_volume' : line.available_volume,
                'max_quantity': line.available_quantity,
                'volume' : line.available_volume,
                'delta_day' : delta_day
            }))
        return lines

    def _add_exit(self, exit_date=False, quantity=0.0, volume=0.0, move=False):
        self.ensure_one()
        vals = {
            'name' : f"{exit_date.strftime('%d/%m/%Y')} : V = {volume} | Qté = {quantity}",
            'exit_date' : exit_date,
            'exit_quantity' : quantity,
            'exit_volume' : volume,
            'move_id' : move.id,
            'customer_stock_line_id' : self.id,
        }
        
        self.env['customer.stock.line.exit.dates'].create(vals)
    
class CustomerStockLineExitDates(models.Model):
    _name = "customer.stock.line.exit.dates"
    _description = "Ligne de Stock Client"
    
    name = fields.Char(string="Nom")
    customer_stock_line_id = fields.Many2one(string="Ligne de stock client", comodel_name="customer.stock.line")
    exit_date = fields.Datetime(string="Sortie du stock")
    exit_quantity = fields.Float(string="Qté sortie")
    exit_volume = fields.Float(string="Vol sortie")
    move_id = fields.Many2one(string="Move", comodel_name="stock.move")
    move_state = fields.Selection(related="move_id.state")