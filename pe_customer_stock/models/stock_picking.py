# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        # OVERRIDE #
        """ Modification de la création des transferts pour avoir un emplacement Output dynamique
            Objectif : Livraison en 2 étapes, stocker dans l'emplacement interne client (fiche contact) avant envoi au client

            Par défaut :
            Stock -> Output
            Output -> Client

            Résultat souhaité :
            Stock -> Emplacement Interne Client
            Emplacement Interne Client -> Client
        """
        _logger.warning(f" Avant : {self.picking_ids}")
        res = super(SaleOrder, self).action_confirm()
        
        if self.partner_id.customer_location_id: # Si emplacement interne client configurer
            partner_loc = self.partner_id.customer_location_id
            for picking in self.picking_ids:
                # Stock -> Output
                if picking.location_dest_id.id == 11:
                    picking.location_dest_id = partner_loc.id
                    # for move in picking.move_lines:
                    #     move.location_dest_id = partner_loc.id
                    # for move in picking.move_ids_without_package:
                    #     move.location_dest_id = partner_loc.id
                    for move in picking.move_line_ids_without_package:
                        move.location_dest_id = partner_loc.id

                # Output -> Stock
                if picking.location_id.id == 11:
                    picking.location_id = partner_loc.id
                    for move in picking.move_lines:
                        move.location_id = partner_loc.id
                        
        _logger.warning(f" Après : {self.picking_ids}")
        return res