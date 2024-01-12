# -*- coding: utf-8 -*-
import logging
from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class AccountMoveAdm(models.Model):
    _name = 'account.move.adm'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Facture global ADM'
                
#--------- Ligne ADMG ---------#   
class AccountMoveAdmLine(models.Model):
    _name = 'account.move.adm.line'
    _description = 'Ligne des facture grouper pour les administrations'