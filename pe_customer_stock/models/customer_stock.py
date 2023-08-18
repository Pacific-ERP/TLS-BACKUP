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
    
    stock_lines = fields.One2many(string="Ligne stock clients", comodel_name="customer.stock.line", inverse_name="customer_stock_id")
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
    entry_quantity = fields.Float(string="Quantité entrée")
    product_uom_id = fields.Many2one('uom.uom', 'UdM', domain="[('category_id', '=', product_uom_category_id)]")
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
    
    available_quantity = fields.Float(string="Quantité restante", compute="_compute_available_quantity", store=True)
    to_show = fields.Boolean(string="À afficher", compute="_compute_available_quantity", store=True)
    is_invoiceable = fields.Boolean(string="Facturable", compute="_compute_available_quantity", store=True)
    
    exit_dates = fields.One2many(string="Sortie de stock", comodel_name="customer.stock.line.exit.dates", inverse_name="customer_stock_line_id")

    def _compute_default_exit_date(self):
        return fields.Datetime.today()
    
    @api.depends('exit_dates','entry_quantity')
    def _compute_available_quantity(self):
        for line in self:
            available_quantity = 0.0
            if line.entry_quantity:
                available_quantity = line.entry_quantity
                if line.exit_dates:
                    available_quantity -= sum(exit.exit_quantity for exit in line.exit_dates)
            
            _logger.warning(f"Quantité restante : {available_quantity}")
            line.available_quantity = available_quantity

            # La ligne est à afficher et facturé si une quantité est encore disponible
            show_and_invoice = True if available_quantity > 0 else False
            line.is_invoiceable = line.to_show = show_and_invoice

    def _prepare_wizard_lines(self):
        lines = []
        exit_date = self._compute_default_exit_date()
        for line in self:
            lines.append((0, 0, {
                'customer_stock_line_id': line.id,
                'product_id': line.product_id.id,
                'entry_date': line.entry_date,
                'exit_date': exit_date,
                'product_uom_id': line.product_uom_id.id,
                'quantity': line.available_quantity
            }))
        return lines

    def _add_exit(self, exit_date, quantity, move):
        self.ensure_one()
        vals = {
            'exit_date' : exit_date,
            'exit_quantity' : quantity,
            'move_id' : move.id,
            'customer_stock_line_id' : self.id,
        }
        
        self.env['customer.stock.line.exit.dates'].create(vals)
    
class CustomerStockLineExitDates(models.Model):
    _name = "customer.stock.line.exit.dates"
    _description = "Ligne de Stock Client"

    @api.depends('exit_date', 'exit_quantity')
    def _compute_exit_dates_name(self):
        for exit_date in self:
            exit_date.name = f"{exit_date.exit_date.strftime('%d/%m/%Y')} : {exit_date.exit_quantity}"
    
    name = fields.Char(string="Nom")
    customer_stock_line_id = fields.Many2one(string="Ligne de stock client", comodel_name="customer.stock.line")
    exit_date = fields.Datetime(string="Sortie du stock")
    exit_quantity = fields.Float(string="Quantité entrée")
    move_id = fields.Many2one(string="Move", comodel_name="stock.move")
    move_state = fields.Selection(related="move_id.state")