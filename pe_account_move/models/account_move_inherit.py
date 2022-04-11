# -*- coding: utf-8 -*-
import logging
from odoo import fields, models, api, _
from datetime import timedelta, date, datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
from odoo.tools.misc import formatLang, format_date, get_lang

_logger = logging.getLogger(__name__)

class AccountMoveIhnerit(models.Model):
    _inherit = "account.move"
    
    def _check_month_lock_date(self):# 644 302
        for move in self:
            invoice_date = move.date # date du document
            today = date.today() # date d'aujourd'hui
            lock_date = today + relativedelta(day=10) # date limite avant blocage définitif des facture M-1
            last_day_of_prev_month = date.today().replace(day=1) - timedelta(days=1) # dernier jours M-1
            # Pour récupérer le group de l'utilisateur : self.user_has_groups() ici group_account_manager c'est le [Comptabilité / Paramétrage facturation]
            if invoice_date <= last_day_of_prev_month and lock_date <= today and not self.user_has_groups('account.group_account_manager'):
                message = _("You cannot add/modify entries prior to and inclusive of the lock date %s, refer to your invoice manager.", format_date(self.env, lock_date))
                raise UserError(message)
        return True
        
    def write(self, vals):
        ### OVERRIDE Write method account.move
        result = super(AccountMoveIhnerit, self).write(vals)
        for move in self:
            
            # You can't change the date of a move being inside a locked period.
            if move.state == "posted" and 'date' in vals and move.date != vals['date']:
                move._check_month_lock_date()
            
            # You can't post subtract a move to a locked period.
            if 'state' in vals and move.state == 'posted' and vals['state'] != 'posted':
                move._check_month_lock_date()
        
        # You can't post a new journal entry inside a locked period.
        if 'date' in vals or 'state' in vals:
            posted_move = self.filtered(lambda m: m.state == 'posted')
            posted_move._check_month_lock_date()
        return result
    
    def button_draft(self):
        ### OVERRIDE Write method account.move afin de bloquer la remise en brouillon des factures si délais dépasser 
        res = super(AccountMoveIhnerit, self).button_draft()
        for move in self:
            move._check_month_lock_date()
        return res
    
class AccountMoveLineIhnerit(models.Model):
    _inherit = "account.move.line"

    @api.model_create_multi
    def create(self, vals_list):
        #OVERRIDE Create method account.move.line
        lines = super(AccountMoveLineIhnerit, self).create(vals_list)
        moves = lines.mapped('move_id')
        moves.filtered(lambda m: m.state == 'posted')._check_month_lock_date()
        return lines
    
    def write(self, vals):
        # OVERRIDE Write method account.move.line
        PROTECTED_FIELDS_TAX_LOCK_DATE = ['debit', 'credit', 'tax_line_id', 'tax_ids', 'tax_tag_ids']
        PROTECTED_FIELDS_LOCK_DATE = PROTECTED_FIELDS_TAX_LOCK_DATE + ['account_id', 'journal_id', 'amount_currency', 'currency_id', 'partner_id']
        res = super(AccountMoveLineIhnerit, self).write(vals)
        for line in self:
            if line.parent_state == 'posted' and any(self.env['account.move']._field_will_change(line, vals, field_name) for field_name in PROTECTED_FIELDS_LOCK_DATE):
                line.move_id._check_month_lock_date()
        return res
    
    def unlink(self):
        #OVERRIDE Unlink method account.move.line
        res = super(AccountMoveLineIhnerit, self).unlink()
        moves = self.mapped('move_id')
        moves._check_month_lock_date()
        return res
    
    
            
            