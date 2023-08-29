# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = "stock.picking"

    is_customer_delivered = fields.Boolean(string="Transfert Client fait", default=False)
    is_customer_picking = fields.Boolean(string="Transfert Client", default=False)
    customer_picking_to_invoice = fields.Boolean(string="Transfert Client à facturé", default=False)
    
    customer_stock_id = fields.Many2one(string="Stock Clients", comodel_name="customer.stock")
    
    def _prepare_wizard_lines(self):
        lines = []
        for move in self.move_lines:
            lines.append((0, 0, {
                'move_id': move.id,
                'product_id': move.product_id.id,
                'product_uom_id': move.product_uom.id,
                'quantity': move.quantity_done
            }))
        return lines
        
    def _prepare_invoice_vals(self):
        """ Prépare les valeurs pour la création d'une facture

        """
        invoice_vals = {
            'move_type': 'out_invoice',
            'partner_id': self.partner_id.id,
            'invoice_date': fields.Datetime.now(),
            'date': fields.Datetime.now(),
            'customer_stock_id': self.customer_stock_id if self.customer_stock_id else False,
        }
        return invoice_vals
        
    def _create_invoice(self):
        '''
            Facturation de la livraison
        '''
        invoice_line = invoice_vals = []
        
        # Valeur de la facture (account.move)
        invoice_vals = self._prepare_invoice_vals()

        # Valeur des ligns de la facture (account.move.line)
        for line in self.move_lines:
            invoice_line.append((0,0,line._prepare_invoice_line_vals()))

        if invoice_line:
            invoice_vals.update({'invoice_line_ids': invoice_line})
            
        invoice = self.with_context(check_move_validity=False).env['account.move'].with_company(self.company_id).sudo().create(invoice_vals).with_user(self.env.uid)
        self.message_post(body=f"Facture client créer : {invoice._get_custom_link()}")

    def _get_invoice(self):
        ''' Récupère la 1er facture client si une existante en brouillons'''
        customer_stock = self.customer_stock_id
        invoice = self.env['account.move'].sudo().search([('state','=','draft'),('customer_stock_id','=', customer_stock.id)], limit=1)
        return invoice if invoice else False
    
    def _populate_invoice(self, invoice):
        line_to_add = []
        # Valeur des ligns de la facture (account.move.line)
        for line in self.move_lines:
            line_to_add.append((0,0,line._prepare_invoice_line_vals()))

        invoice.with_context(check_move_validity=False).write({'invoice_line_ids': line_to_add})
        invoice._recompute_dynamic_lines()
        self.message_post(body=f"Facture client alimenter : {invoice._get_custom_link()}")
    
    def _process_create_invoice(self):
        invoice = self._get_invoice()

        if invoice:
            self._populate_invoice(invoice)
        else:
            self._create_invoice()
        
    def _get_customer_stock(self):
        ''' Récupère le stock client si existants '''
        return self.env['customer.stock'].sudo().search([('partner_id','=', self.partner_id.id)], limit=1) or False
    
    def _check_customer_stock_available(self):
        '''
            Permet de vérifier si un stock client existe déjà
        '''
        return True if self._get_customer_stock() else False

    def _populate_customer_stock(self):
        '''
            Alimente le stock clients avec les nouvelles entrées
        '''
        # Récupération du stock client
        customer_stock = self._get_customer_stock()

        # Création des lignes du stock clients
        self.move_lines._create_customer_stock_lines(self, self.location_dest_id, customer_stock)

        # Lien entre transfert et stock clients pour suivis
        self.customer_stock_id = customer_stock.id

        self.message_post(body=f"Stocks client alimenter : {customer_stock._get_custom_link()}")

    def _prepare_customer_stock_vals(self):
        ''' Valeur nécessaires à la création d'un stock clients '''
        return {
            'name' : self.partner_id.name,
            'partner_id' : self.partner_id.id,
        }
    
    def _create_customer_stock(self):
        '''
            Créer le stock clients et l'alimente avec les nouvelles entrées
        '''
        # Création du stock clients
        res = self._prepare_customer_stock_vals()
        customer_stock = self.env['customer.stock'].create(res)

        # Création des lignes du stock clients
        self.move_lines._create_customer_stock_lines(self, self.location_dest_id, customer_stock)

        # Lien entre transfert et stock clients pour suivis
        self.customer_stock_id = customer_stock.id
        
        self.message_post(body=f"Stocks client créer : {customer_stock._get_custom_link()}")
        
    def _process_customer_stock(self):
        '''
            Prépare l'opération à faire selon l'existance du stock client
            True : Alimente les lignes du stock clients
            False : Créer un stock client et alimente se dernier
        '''
        if self._check_customer_stock_available():
            self._populate_customer_stock()
            self.customer_stock_id = self._get_customer_stock().id
        else:
            self._create_customer_stock()    
    
    def button_validate(self):
        '''
            !!! OVERRIDE !!!

            Surcharge le bouton principale pour rajouter les
            fonctionnalités de gestion de stock clients
        '''
        if self.is_customer_picking:
            if all(not line.quantity_done for line in self.move_lines):
                raise UserError("Aucune quantité n'a été faite, veuillez copier les quantités ou les renseigner")
                return False
                
            # Transfert interne
            if self.picking_type_code == 'internal':
                self._process_customer_stock()
            # Livraison
            elif self.picking_type_code == 'outgoing' and self.customer_picking_to_invoice:
                self._process_create_invoice()
                
        return super(StockPicking, self).button_validate()
        
    def button_customer_stock(self):
        '''
            Ouvre un Wizard pour les différents cas:
            1 - Livraison direct vers le client
            2 - Transfert Interne vers stock client

            Permet de récupéré les informations nécessaire pour la création des mouvements de stock:
            
            client m2o : Client destinataire
            volume float : Volume de l'article stocker
            documents m2m : liste des documents à joindre avec le mouvement
            
        '''
        if self.state == 'done':
            view = self.env.ref('pe_customer_stock.pe_customer_stock_wizard_form')
            lines = self._prepare_wizard_lines()
            return {
                'name': ('Transfert Client'),
                'type': 'ir.actions.act_window',
                'res_model': 'customer.stock.wizard',
                'views': [(view.id, 'form')],
                'target': 'new',
                'context': {
                    'default_wizard_lines': lines,
                    'default_origin': self.origin,
                    'default_picking_id': self.id,
                    'default_company_id': self.company_id.id}
            }            