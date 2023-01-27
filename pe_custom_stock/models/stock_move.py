# -*- coding: utf-8 -*-
import logging
from collections import defaultdict
from datetime import timedelta
from itertools import groupby
from odoo.tools import groupby as groupbyelem
from operator import itemgetter

from odoo import _, api, Command, fields, models
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.tools.misc import clean_context, OrderedSet

_logger = logging.getLogger(__name__)
    
class StockMove(models.Model):
    _inherit = "stock.move"
    
    def _merge_moves(self, merge_into=False):
        # Override #
        """ This method will, for each move in `self`, go up in their linked picking and try to
        find in their existing moves a candidate into which we can merge the move.
        :return: Recordset of moves passed to this method. If some of the passed moves were merged
        into another existing one, return this one and not the (now unlinked) original.
        """
        distinct_fields = self._prepare_merge_moves_distinct_fields()

        candidate_moves_list = []
        if not merge_into:
            self._update_candidate_moves_list(candidate_moves_list)
        else:
            candidate_moves_list.append(merge_into | self)

        # Move removed after merge
        moves_to_unlink = self.env['stock.move']
        # Moves successfully merged
        merged_moves = self.env['stock.move']

        moves_by_neg_key = defaultdict(lambda: self.env['stock.move'])
        # Need to check less fields for negative moves as some might not be set.
        neg_qty_moves = self.filtered(lambda m: float_compare(m.product_qty, 0.0, precision_rounding=m.product_uom.rounding) < 0)
        # Detach their picking as they will either get absorbed or create a backorder, so no extra logs will be put in the chatter
        neg_qty_moves.picking_id = False
        excluded_fields = self._prepare_merge_negative_moves_excluded_distinct_fields()
        neg_key = itemgetter(*[field for field in distinct_fields if field not in excluded_fields])
        price_unit_prec = self.env['decimal.precision'].precision_get('Product Price')

        for candidate_moves in candidate_moves_list:
            # First step find move to merge.
            candidate_moves = candidate_moves.filtered(lambda m: m.state not in ('done', 'cancel', 'draft')) - neg_qty_moves
            for k, g in groupbyelem(candidate_moves, key=itemgetter(*distinct_fields)):
                moves = self.env['stock.move'].concat(*g)
                # Merge all positive moves together
                if len(moves) > 1:
                    # link all move lines to record 0 (the one we will keep).
                    moves.mapped('move_line_ids').write({'move_id': moves[0].id})
                    # merge move data
                    moves[0].write(moves._merge_moves_fields())
                    # update merged moves dicts
                    moves_to_unlink |= moves[1:]
                    merged_moves |= moves[0]
                # Add the now single positive move to its limited key record
                moves_by_neg_key[neg_key(moves[0])] |= moves[0]

        for neg_move in neg_qty_moves:
            # Check all the candidates that matches the same limited key, and adjust their quantites to absorb negative moves
            for pos_move in moves_by_neg_key.get(neg_key(neg_move), []):
                currency_prec = pos_move.product_id.currency_id.decimal_places
                rounding = min(currency_prec, price_unit_prec)
                _logger.error('Rounding : %s' % rounding)
                if rounding == 0:
                    rounding = 0.01
                if float_compare(pos_move.price_unit, neg_move.price_unit, precision_rounding=rounding) == 0:
                    new_total_value = pos_move.product_qty * pos_move.price_unit + neg_move.product_qty * neg_move.price_unit
                    # If quantity can be fully absorbed by a single move, update its quantity and remove the negative move
                    if float_compare(pos_move.product_uom_qty, abs(neg_move.product_uom_qty), precision_rounding=pos_move.product_uom.rounding) >= 0:
                        pos_move.product_uom_qty += neg_move.product_uom_qty
                        pos_move.write({
                            'price_unit': float_round(new_total_value / pos_move.product_qty, precision_digits=price_unit_prec) if pos_move.product_qty else 0,
                            'move_dest_ids': [Command.link(m.id) for m in neg_move.mapped('move_dest_ids') if m.location_id == pos_move.location_dest_id],
                            'move_orig_ids': [Command.link(m.id) for m in neg_move.mapped('move_orig_ids') if m.location_dest_id == pos_move.location_id],
                        })
                        merged_moves |= pos_move
                        moves_to_unlink |= neg_move
                        break
                    neg_move.product_uom_qty += pos_move.product_uom_qty
                    neg_move.price_unit = float_round(new_total_value / neg_move.product_qty, precision_digits=price_unit_prec)
                    pos_move.product_uom_qty = 0

        if moves_to_unlink:
            # We are using propagate to False in order to not cancel destination moves merged in moves[0]
            moves_to_unlink._clean_merged()
            moves_to_unlink._action_cancel()
            moves_to_unlink.sudo().unlink()

        return (self | merged_moves) - moves_to_unlink