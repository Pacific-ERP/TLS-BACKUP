# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api

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

    opportunity_ids = fields.Many2many(string="Opportunités", comodel_name="crm.lead")
    invoice_ids = fields.One2many(string="Factures", comodel_name="account.move", inverse_name="customer_stock_id")
    picking_ids = fields.One2many(string="Transferts", comodel_name="stock.picking", inverse_name="customer_stock_id")
    stock_lines = fields.One2many(string="Ligne stock clients", comodel_name="customer.stock.line", inverse_name="customer_stock_id")

class CustomerStockLine(models.Model):
    _name = "customer.stock.line"
    _description = "Ligne de Stock Client"

    name = fields.Char(string="Description")
    picking_id = fields.Many2one(string="Transfert", comodel_name="stock.picking")
    move_id = fields.Many2one(string="Move", comodel_name="stock.move")
    customer_stock_id = fields.Many2one(string="Stock Clients", comodel_name="customer.stock")

    product_id = fields.Boolean(string="Article", comodel_name="product.product")
    location_id = fields.Many2one(string="Emplacement", comodel_name="stock.location")
    to_invoice = fields.Boolean(string="À Facturé", default=False)
    to_show = fields.Boolean(string="À afficher", default=True)
    is_invoiceable = fields.Boolean(string="Facturable", default=True)
    entry_date = fields.Datetime(string="Entrée en stock")
    entry_quantity = fields.Float(string="Quantité entrée")
    available_quantity = fields.Float(string="Quantité restante")
    exit_dates = fields.One2many(string="Sorties de stocks", comodel_name="customer.stock.line.exit.dates", inverse_name="customer_stock_line_id")

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