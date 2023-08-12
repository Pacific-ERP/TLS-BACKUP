# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class CustomerStockWizard(models.TransientModel):
    _name = "customer.stock.wizard"
    _description = "Pacific-ERP : wizard customer stock"
    
    direct_delivery = fields.Boolean(string="Livraison direct ?", default=True)
    partner_id = fields.Many2one(string="Client", comodel_name="res.partner")
    
    origin = fields.Char(string="Origine")
    company_id = fields.Many2one(string="Société", comodel_name="res.company")
    picking_id = fields.Many2one(string="Transfert", comodel_name="stock.picking")

    wizard_lines = fields.One2many(string="Opération", comodel_name="customer.stock.wizard.line", inverse_name="wizard_id")

    @api.onchange('direct_delivery')
    def _onchange_direct_delivery(self):
        for line in self.wizard_lines:
            line.direct_delivery = self.direct_delivery

    def _prepare_picking(self, location_dest=False):
        '''
            Retourne les informations nécessaires à la création d'un transfert
        '''
        delivery_picking_type = self.env.ref('stock.picking_type_out')
        internal_picking_type = self.env.ref('stock.picking_type_internal')
        
        vals = {
            'partner_id': self.partner_id.id,
            'user_id': self.env.user.id,
            'date': fields.Datetime.today(),
            'origin': self.picking_id.name,
            'company_id': self.company_id.id,
            'picking_type_id': internal_picking_type.id,
            'location_dest_id': location_dest.id if location_dest else internal_picking_type.default_location_dest_id.id,
            'location_id': internal_picking_type.default_location_dest_id.id,
        }

        if self.direct_delivery:
            vals.update({
                'picking_type_id' : delivery_picking_type.id,
                'location_id' : delivery_picking_type.default_location_src_id.id,
                'location_dest_id' : delivery_picking_type.default_location_dest_id.id,
            })
        
        return vals
    
    def _process_customer_stock(self, go_to_record):
        '''
            Prépare le transfert dans le stock clients des articles réceptionner
            
            1 - Vérifie si le client à déjà un stock
                1A - Si oui rajoute les lignes de la réception à sont stock
                1B - Sinon Créer le un stock pour le client
            2 - Si bouton [Confirmer et voir] est séléctionner renvoie au transfert interne pour validation
            3 - Sinon reste sur la réception
        '''
        pass
        

    def _create_delivery(self, go_to_record):
        '''
            Créer une livraison vers le client pour le stock réceptionner

            1 - Si bouton [Confirmer et voir] est séléctionner renvoie à la livraison pour validation
        '''
        _logger.warning("[A] _create_delivery")
        res = self._prepare_picking()
        picking = self.env['stock.picking'].create(res)
        
        self._picking_is_delivered()
    
    def _picking_is_delivered(self):
        '''
            Permet de valider le fait que la réception à été envoyer soit en stock soit au client
        '''
        _logger.errorrreor()
        self.picking_id.is_customer_delivered = True
    
    def button_confirm(self):
        go_to_record = self._context.get('view_customer_picking', False)
        if not self.direct_delivery:
            _logger.warning(f"[1] Transfert Stock client : {self.partner_id} | Go To {go_to_record}")
            self._process_customer_stock(go_to_record)
        else:
            _logger.warning(f"[2] Livraison direct client : {self.partner_id} | Go To {go_to_record}")
            self._create_delivery(go_to_record)
    
class CustomerStockWizardLine(models.TransientModel):
    _name = "customer.stock.wizard.line"
    _description = "Pacific-ERP : Ligne wizard customer stock"

    def _get_destination_domain(self):
        customer_location = self.env.ref('stock.stock_location_customers')
        return [('location_id','=', customer_location.id)] if customer_location else []

    wizard_id = fields.Many2one(string="Customer Stock", comodel_name="customer.stock.wizard")
    move_id = fields.Many2one(string="Move", comodel_name="stock.move")
    direct_delivery = fields.Boolean(string="Livraison direct ?", default=True)
    
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    destination_id = fields.Many2one(string="Emplacement client", comodel_name="stock.location", domain=_get_destination_domain)
    product_uom_id = fields.Many2one('uom.uom', 'UdM', required=True, domain="[('category_id', '=', product_uom_category_id)]")
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
    quantity = fields.Float(string="Quantité")
