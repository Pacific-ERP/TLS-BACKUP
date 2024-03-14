# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    transport_type = fields.Selection(string="Mode d'acheminement", selection=[('plane','Avion'),
                                                                               ('boat','Bateau'),
                                                                               ('terreste','Terrestre')]
                                      , default=False, copy=False)
    
    provenance = fields.Many2one(string="Provenance", comodel_name="res.country")

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.onchange('discount')
    def _check_discount_limit(self):
        limit = 20
        for line in self:
            if self.env.user.has_group('pe_custom.group_discount_limit'):
                # Si remise > limite et que ce n'est pas un article adm 100% maritime 
                if line.discount > limit and not (line.check_adm and line.base_maritime and not line.base_terrestre):
                    raise ValidationError(_('Vous ne pouvez pas attribué plus de 20% de remise, rapprochez vous de (Hokini, Tea, Mélissa ou Terai)'))