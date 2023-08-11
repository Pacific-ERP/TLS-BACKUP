# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api

_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = "stock.picking"

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
            return {
                'name': ('Transfert Client'),
                'type': 'ir.actions.act_window',
                'res_model': 'customer.stock.wizard',
                'views': [(view.id, 'form')],
                'target': 'new',
                'context': {
                    'default_wizard_lines': self._prepare_wizard_lines(),
                    'default_origin': self.origin,
                    'default_picking_id': self.id},
            }