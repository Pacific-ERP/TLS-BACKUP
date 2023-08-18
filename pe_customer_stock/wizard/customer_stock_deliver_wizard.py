# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api
from odoo.exceptions import UserError
from markupsafe import Markup
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

class CustomerStockDeliverWizard(models.TransientModel):
    _name = "customer.stock.deliver.wizard"
    _description = "Pacific-ERP : wizard livraison customer stock"

    customer_stock_id = fields.Many2one(string="Stock Clients", comodel_name="customer.stock")
    origin = fields.Char(string="Origine")
    company_id = fields.Many2one(string="Société", comodel_name="res.company")

    wizard_lines = fields.One2many(string="Opération", comodel_name="customer.stock.deliver.wizard.line", inverse_name="wizard_id",
                                   store=True, context={'shortname': True})

    def _prepare_picking(self, location_origin=False):
        '''
            Retourne les informations nécessaires à la création d'un transfert
        '''
        delivery_picking_type = self.env.ref('stock.picking_type_out')
        
        vals = {
            'partner_id': self.customer_stock_id.partner_id.id,
            'user_id': self.env.user.id,
            'date': fields.Datetime.today(),
            'origin': self.origin,
            'company_id': self.company_id.id,
            'picking_type_id' : delivery_picking_type.id,
            'location_id' : location_origin.id,
            'location_dest_id' : delivery_picking_type.default_location_dest_id.id,
            'is_customer_picking' : True,
            'customer_picking_to_invoice' : True,
        }
        
        return vals

    def _get_custom_link(self, picking_id):
        return Markup("<a href=# data-oe-model='%s' data-oe-id='%s'>%s</a>") % (
            picking_id._name, picking_id.id, picking_id.display_name)

    def _post_message_link(self, picking_ids):
        if picking_ids:
            created_msg = "Transfert créer à partir de %s" % self.customer_stock_id._get_custom_link()
            for picking in picking_ids:
                picking.message_post(body=created_msg)

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
    
    def _create_delivery(self, go_to_record):
        '''
            Créer une livraison vers le client pour le stock réceptionner

            1 - Si bouton [Confirmer et voir] est séléctionner renvoie à la livraison pour validation
        '''
        _logger.warning("[A] _create_delivery")
        
        location_ids = self.wizard_lines.mapped('location_id')

        pickging_ids = self.env['stock.picking']
        for location in location_ids:
            # Création du transfert
            res = self._prepare_picking(location)
            picking = self.env['stock.picking'].create(res)
            pickging_ids += picking
            
            # Création des lignes de mouvement de stock et link avec transfert
            move_line_to_add = self.wizard_lines.filtered(lambda l : l.location_id.id == location.id)
            move_line_to_add._create_stock_moves(picking, self.customer_stock_id)
            picking.action_confirm()

        # Message chatter pour followup
        self._post_message_link(pickging_ids)

        if pickging_ids and go_to_record:
            return self._go_to_records(pickging_ids)
        return {'type': 'ir.actions.act_window_close'}
    
    def button_confirm(self):
        go_to_record = self._context.get('view_customer_picking', False)

        _logger.warning(f"[1] Transfert Stock client : {self.customer_stock_id.partner_id} | Go To {go_to_record}")
        return self._create_delivery(go_to_record)
    
class CustomerStockWizardLine(models.TransientModel):
    _name = "customer.stock.deliver.wizard.line"
    _description = "Pacific-ERP : Ligne de livraison wizard customer stock"

    @api.onchange('entry_date','exit_date')
    def _compute_delta_entry_exit(self):
        for line in self:
            delta = 0
            if line.entry_date and line.exit_date:
                delta = (line.exit_date - line.entry_date).days
                
            if line.delta_day < 0:
                raise UserError("La date de sortie est avant la date d'entrée")
                return False
            line.delta_day = delta
    
    wizard_id = fields.Many2one(string="Livraison customer stock", comodel_name="customer.stock.deliver.wizard")
    customer_stock_line_id = fields.Many2one(string="Ligne de mouvement de stock client", comodel_name="customer.stock.line")

    location_id = fields.Many2one(string="Emplacement client", comodel_name="stock.location")
    product_id = fields.Many2one(string="Articles", comodel_name="product.product", store=True)
    max_quantity = fields.Float(string="Max Quantité", default=0.0, required=True)
    max_volume = fields.Float(string="Max Volume", default=0.0, required=True)
    quantity = fields.Float(string="Quantité", default=0.0, required=True)
    volume = fields.Float(string="Volume", default=0.0, required=True)
    product_uom_id = fields.Many2one('uom.uom', 'UdM', domain="[('category_id', '=', product_uom_category_id)]")
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')

    entry_date = fields.Datetime(string="Entrée en stock")
    exit_date = fields.Datetime(string="Sortie de stock", store=True)
    delta_day = fields.Integer(string="Différence en jours", compute="_compute_delta_entry_exit", store=True)

    @api.onchange('quantity', 'volume')
    def _onchange_quantity_volume_error(self):
        if self.max_quantity and self.quantity > self.max_quantity:
            raise UserError("La quantité du transfert ne peux pas excéder la quantité restant en stock pour cette ligne")
        if self.max_volume and self.volume > self.max_volume:
            raise UserError("Le volume du transfert ne peux pas excéder le volume restant en stock pour cette ligne")
    
    def _create_stock_moves(self, picking_id, origin):
        _logger.warning(f'[Lines]_create_stock_moves')
        for line in self:
            if picking_id:
                template = {
                    'name': f"{line.product_id.name} : {origin.name} > {picking_id.name}",
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
                    'pe_volume_exit' : line.volume,
                    'pe_entry_date' : line.entry_date,
                    'pe_exit_date' : line.exit_date,
                    'delta_day' : line.delta_day,
                }
                move = self.env['stock.move'].create(template)
                line.customer_stock_line_id._add_exit(line.exit_date, line.quantity, line.volume, move)