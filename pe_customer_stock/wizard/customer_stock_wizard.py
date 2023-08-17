# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api
from odoo.exceptions import UserError
from markupsafe import Markup

_logger = logging.getLogger(__name__)

class CustomerStockWizard(models.TransientModel):
    _name = "customer.stock.wizard"
    _description = "Pacific-ERP : wizard customer stock"

    def _get_destination_domain(self):
        customer_location = self.env.ref('stock.stock_location_customers')
        return [('location_id','=', customer_location.id)] if customer_location else []
    
    direct_delivery = fields.Boolean(string="Livraison direct ?", default=True)
    partner_id = fields.Many2one(string="Client", comodel_name="res.partner")
    destination_id = fields.Many2one(string="Emplacement client", comodel_name="stock.location", domain=_get_destination_domain)
    
    origin = fields.Char(string="Origine")
    company_id = fields.Many2one(string="Société", comodel_name="res.company")
    picking_id = fields.Many2one(string="Transfert", comodel_name="stock.picking")

    wizard_lines = fields.One2many(string="Opération", comodel_name="customer.stock.wizard.line", inverse_name="wizard_id", store=True)

    @api.onchange('direct_delivery')
    def _onchange_direct_delivery(self):
        for line in self.wizard_lines:
            line.direct_delivery = self.direct_delivery

    @api.onchange('destination_id')
    def _onchange_direct_delivery(self):
        for line in self.wizard_lines:
            line.destination_id = self.destination_id.id

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

    def _get_custom_link(self, picking_id):
        return Markup("<a href=# data-oe-model='%s' data-oe-id='%s'>%s</a>") % (
            picking_id._name, picking_id.id, picking_id.display_name)

    def _post_message_link(self, picking_ids):
        if picking_ids:
            actual_msg = "Transfert vers stock client créer:"
            created_msg = "Transfert créer à partir de %s" % self._get_custom_link(self.picking_id)
            # Livraison -> 1
            if self.direct_delivery:
                actual_msg = "Livraison %s créer " % self._get_custom_link(picking_ids)
            # Transfert interne -> 1 or X
            else:
                actual_msg = actual_msg + '<br/>'.join(self._get_custom_link(self.picking) for picking in picking_ids)

            # Message sur transfert créer
            for picking in picking_ids:
                picking.message_post(body=created_msg)

            # Message sur actuel transfert
            self.picking_id.message_post(body=actual_msg)

    def _go_to_records(self, pickings):
        '''
            Permet d'accédé au transfert tout juste créer
        '''
        if pickings:
            _logger.warning(f"[GO TO] {pickings}")
            action = self.env["ir.actions.actions"]._for_xml_id("stock.action_picking_tree_all")
            if len(pickings) > 1:
                action['domain'] = [('id', 'in', pickings.ids)]
            elif pickings:
                form_view = [(self.env.ref('stock.view_picking_form').id, 'form')]
                if 'views' in action:
                    action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
                else:
                    action['views'] = form_view
                action['res_id'] = pickings.id
            else:
                action = {'type': 'ir.actions.act_window_close'}
            _logger.warning(f"Action : {action}")
            return action            
    
    def _process_customer_stock(self, go_to_record):
        '''
            Prépare le transfert dans le stock clients des articles réceptionner
            
            1 - Vérifie si le client à déjà un stock
                1A - Si oui rajoute les lignes de la réception à sont stock
                1B - Sinon Créer le un stock pour le client
            2 - Si bouton [Confirmer et voir] est séléctionner renvoie au transfert interne pour validation
            3 - Sinon reste sur la réception
        '''
        if not any(line.destination_id for line in self.wizard_lines):
            raise UserError("Un lieu de destination est nécessaire pour chaque articles")
            
        destination_ids = self.wizard_lines.mapped('destination_id')
        _logger.warning(f"Destinations : {destination_ids}")
        pass
        
    
    def _create_delivery(self, go_to_record):
        '''
            Créer une livraison vers le client pour le stock réceptionner

            1 - Si bouton [Confirmer et voir] est séléctionner renvoie à la livraison pour validation
        '''
        _logger.warning("[A] _create_delivery")
        
        # Création du transfert
        res = self._prepare_picking()
        picking = self.env['stock.picking'].create(res)
        # Création des lignes de mouvement de stock et link avec transfert
        
        self.wizard_lines._create_stock_moves(picking)
        picking.action_confirm()

        # Message chatter pour followup
        self._post_message_link(picking)
        self._picking_is_delivered()

        if picking and go_to_record:
            return self._go_to_records(picking)
        return {'type': 'ir.actions.act_window_close'}
    
    def _picking_is_delivered(self):
        '''
            Permet de valider le fait que la réception à été envoyer soit en stock soit au client
        '''
        self.picking_id.is_customer_delivered = True
    
    def button_confirm(self):
        go_to_record = self._context.get('view_customer_picking', False)

        if not self.direct_delivery:
            _logger.warning(f"[1] Transfert Stock client : {self.partner_id} | Go To {go_to_record}")
            return self._process_customer_stock(go_to_record)
        else:
            _logger.warning(f"[2] Livraison direct client : {self.partner_id} | Go To {go_to_record}")
            return self._create_delivery(go_to_record)
    
class CustomerStockWizardLine(models.TransientModel):
    _name = "customer.stock.wizard.line"
    _description = "Pacific-ERP : Ligne wizard customer stock"

    def _get_destination_domain(self):
        customer_location = self.env.ref('stock.stock_location_customers')
        return [('location_id','=', customer_location.id)] if customer_location else []

    wizard_id = fields.Many2one(string="Customer Stock", comodel_name="customer.stock.wizard")
    move_id = fields.Many2one(string="Move", comodel_name="stock.move")
    direct_delivery = fields.Boolean(string="Livraison direct ?", default=True)
    
    product_id = fields.Many2one(string="Articles", comodel_name="product.product", store=True)
    destination_id = fields.Many2one(string="Emplacement client", comodel_name="stock.location", domain=_get_destination_domain)
    product_uom_id = fields.Many2one('uom.uom', 'UdM', domain="[('category_id', '=', product_uom_category_id)]")
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
    quantity = fields.Float(string="Quantité", default=1, required=True)

    def _create_stock_moves(self, picking_id):
        _logger.warning(f'[Lines]_create_stock_moves')
        for line in self:
            if picking_id:
                template = {
                    'name': f"Livraison : {line.product_id.name}",
                    'picking_id': picking_id.id,
                    'product_id': line.product_id.id or line.move_id.product_id.id,
                    'product_uom': line.product_uom_id.id,
                    'location_id': picking_id.location_id.id,
                    'location_dest_id': picking_id.location_dest_id.id,
                    'state': 'draft',
                    'company_id': picking_id.company_id.id,
                    'price_unit': line.product_id.lst_price,
                    'product_uom_qty': line.quantity,
                    'picking_type_id': picking_id.picking_type_id.id,
                    'warehouse_id': picking_id.picking_type_id.warehouse_id.id,
                }
                move = self.env['stock.move'].create(template)