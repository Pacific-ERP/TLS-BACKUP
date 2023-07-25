# -*- coding: utf-8 -*-

import json
import xlsxwriter
import io
import logging
import itertools
from odoo import fields, models, api
from datetime import datetime, timedelta 
from odoo.tools import date_utils
from dateutil.relativedelta import *
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class SaleLineDetailWizard(models.TransientModel):
    _name = "sale.line.detail.wizard"
    _description = "Wizard détails des lignes de ventes"

    sale_order_id = fields.Many2one(string="Ventes", comodel_name="sale.order")
    order_line = fields.Many2many(string="Ligne de vente", comodel_name="sale.order.line")
    order_line_details = fields.Many2many(string="Détails ligne de vente", comodel_name="sale.line.detail.wizard.line")

class SaleLineDetailWizardLine(models.TransientModel):
    _name = "sale.line.detail.wizard.line"
    _description = "Wizard ligne détaillés des différentes part de la ventes"

    order_line = fields.Many2one(string="Ligne de vente", comodel_name="sale.order.line")
    name = fields.Char(string="Articles", related="order_line.product_id.name")
    tax_id = fields.Many2many(string="Taxes", related="order_line.tax_id")
    qty = fields.Float(string="Qty", default=0.0)
    udm = fields.Many2one(string="Udm", comodel_name="uom.uom")
    tarif_t = fields.Float(string="Terrestre")
    tarif_m = fields.Float(string="Maritime")
    tarif_rpa = fields.Float(string="RPA")
    taxes_detail = fields.Char(string="Détails des Taxes")
    subtotal = fields.Float(string="Total HT")
    total = fields.Float(string="Total TTC")
    