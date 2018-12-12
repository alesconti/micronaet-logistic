#!/usr/bin/python
# -*- coding: utf-8 -*-
###############################################################################
#
# ODOO (ex OpenERP) 
# Open Source Management Solution
# Copyright (C) 2001-2015 Micronaet S.r.l. (<https://micronaet.com>)
# Developer: Nicola Riolini @thebrush (<https://it.linkedin.com/in/thebrush>)
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
# See the GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

import os
import sys
import logging
import xlsxwriter
from odoo import api, fields, models, tools, exceptions, SUPERUSER_ID
from odoo.addons import decimal_precision as dp
from odoo.tools.translate import _


_logger = logging.getLogger(__name__)

class StockLocationTable(models.Model):
    """ Model name: Location Table
    """
    
    _name = 'stock.location.table'
    _description = 'Delivery table'
    _rec_name = 'name'
    _order = 'code'
    
    # -------------------------------------------------------------------------    
    # Columns:
    # -------------------------------------------------------------------------
    code = fields.Char('Code', size=15, required=True)
    name = fields.Char('Name', size=40, required=True)


class StockLocationSlot(models.Model):
    """ Model name: Stock Location Slot
    """
    
    _name = 'stock.location.slot'
    _description = 'Stock Location Slot'
    _rec_name = 'name'
    _order = 'name'

    @api.multi
    def slot_detail(self):
        ''' Open detail view:
        '''
        return {
            'type': 'ir.actions.act_window',
            'name': _('Slot detail'),
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_id': self.id,
            'res_model': 'stock.location.slot',
            #'view_id': view_id, # False
            'views': [(False, 'form'), (False, 'tree')],
            'domain': [],
            'context': self.env.context,
            'target': 'current', # 'new'
            'nodestroy': False,
            }
        
    #@api.depends('name', 'mode')
    @api.multi
    def _get_slot_description(self, ):
        ''' Update description
        '''        
        row_map = {
            '0': _('bottom'),
            '1': _('middle'),
            '2': _('top'),
            }
        drawer_map = {
            'A': _('front'),
            'B': _('back'),
            }
        mapping = {
            'stock': 'MAGA',
            'supplier': 'FORN',
            'pending': 'TEMP',
            }
        mask = _('[Mode %s] [Col %s] [Row %s] [Drawer %s] [Side %s] [Slot %s]')
        for slot in self:
            name = slot.name
            mode = slot.mode
            if not name:
                slot.description = ''
                continue
            if mode == 'stock':
                # Block split:
                name = name.upper()    
                slot_part = name.split('.')
                block = len(slot_part)
                
                # Extract part (mandatory):
                col = slot_part[0][:2] # Campata
                row = slot_part[0][2:] # Ripiano
                
                # Extract part (not mandatory):
                drawer = ''
                part = ''
                if block > 1:
                    drawer = slot_part[1]
                    if block > 2:
                        part = slot_part[2]
                
                slot.description = mask % (
                    mapping.get(slot.mode, ''),
                    col, # Campata
                    row_map.get(row, row),
                    drawer[1:2],
                    drawer_map.get(drawer[:1], drawer[:1]),
                    part,
                    )
            elif mode == 'supplier':
                slot.description = ''        
            elif mode == 'pending':
                slot.description = ''
        return True
    
    # -------------------------------------------------------------------------    
    # Columns:
    # -------------------------------------------------------------------------
    name = fields.Char('Name', size=40, required=True,
        help='Slot code')    
    product_ids = fields.One2many(
        'product.template', 'default_slot_id', 'Product')    
    mode = fields.Selection([
        ('stock', 'Stock'), # Load stock
        ('supplier', 'Supplier ready'), # Delivered today (order ready)
        ('pending', 'Supplier pending'), # Delivered tomorrow (order pending)        
        ], string='Mode', default='stock')
    description = fields.Char('Description', size=180,
        compute='_get_slot_description',
        help='Explode description depend on mode and name', 
        )

class StockTableSlotRel(models.Model):
    """ Model name: Table relation
    """
    
    _name = 'stock.table.slot.rel'
    _description = 'Table-slot relation'
    _rec_name = 'slot_id'
    _order = 'sequence'

    # -------------------------------------------------------------------------    
    # Columns:
    # -------------------------------------------------------------------------
    sequence = fields.Integer('Sequence')
    table_id = fields.Many2one(
        'stock.location.table', 'Table', ondelete='cascade')
    slot_id = fields.Many2one('stock.location.slot', 'Pending slot',
        domain='[("mode", "=", "pending")]', ondelete='cascade',
        context='{"default_mode": "pending"}')
    note = fields.Text('Note')
    
    # -------------------------------------------------------------------------
    # SQL Constraints:
    # -------------------------------------------------------------------------
    _sql_constraints = [(
        'slot_id_unique', 
        'UNIQUE(slot_id)', 
        'Slot yet used in another partner!',
        )]

class StockLocationTable(models.Model):
    """ Model name: Res Partner table (pre delivery)
    """
    
    _inherit = 'stock.location.table'
    
    # -------------------------------------------------------------------------    
    # Columns:
    # -------------------------------------------------------------------------
    # Ready slot:
    default_slot_id = fields.Many2one(
        'stock.location.slot', 'Table ready location', 
        domain='[("mode", "=", "supplier")]', 
        context='{"default_mode": "supplier"}'
        )

    # Pending Slots:    
    pending_slot_ids = fields.One2many(
         'stock.table.slot.rel', 'table_id', 'Pending slots')

class ResPartner(models.Model):
    """ Model name: Res Partner
    """

    _inherit = 'res.partner'

    # -------------------------------------------------------------------------    
    # Columns:
    # -------------------------------------------------------------------------
    delivery_table_id = fields.Many2one(
        'stock.location.table', 'Delivery table')        

class ProductTemplate(models.Model):
    """ Model name: Product template
    """
    
    _inherit = 'product.template'

    # -------------------------------------------------------------------------    
    # Columns:
    # -------------------------------------------------------------------------
    default_slot_id = fields.Many2one(
        'stock.location.slot', 'Stock slot')
    slot_needed = fields.Boolean('Slot needed', 
        help='Slot not present but need for position')

class StockMoveIn(models.Model):
    """ Model name: Stock Move
    """
    
    _inherit = 'stock.move'

    # -------------------------------------------------------------------------
    # Utility:
    # -------------------------------------------------------------------------
    @api.multi
    def set_stock_move_position(self):
        ''' Set stock move position:
            Ready order on supplier table
            Pending order on pending supplier table
            Stock product stock position
        '''
        import pdb; pdb.set_trace()
        for move in self:
            # Use stock.move in BF load line:
            line = move.logistic_load_id
            logistic_load_id = line.id
            if logistic_load_id: # With sale order
                supplier = self.picking_id.partner_id
                table = supplier.delivery_table_id
                order = line.order_id

                if order.logistic_state == 'pending':
                    # -------------------------------------------------------------
                    # Ready order position:
                    # -------------------------------------------------------------
                    try:  
                        line.slot_id = table.pending_slot_ids[0].slot_id.id
                    except:
                        _logger.error('No table for supplier: {}'.format(
                            supplier.name))
                            
                elif order.logistic_state == 'ready':
                    # -------------------------------------------------------------
                    # Pending order position (XXX take first pending slot now):
                    # -------------------------------------------------------------
                    # TODO create an assign procedure!
                    try:
                        line.slot_id = table.default_slot_id.id
                    except:
                        _logger.error('No table for supplier: {}'.format(
                            supplier.name))
            else:
                # -----------------------------------------------------------------
                # Stock position
                # -----------------------------------------------------------------
                product = self.product_id
                default_slot_id = product.default_slot_id
                if not default_slot_id and not product.slot_needed:
                    # Mark as needed:
                    product.slot_needed = True

    # -------------------------------------------------------------------------    
    # Columns:
    # -------------------------------------------------------------------------
    slot_id = fields.Many2one(
        'stock.location.slot', 'Stock slot', 
        help='Supplier position, ready for ready order instead of pending')

class SaleOrderLine(models.Model):
    """ Model name: Sale Order Line
    """
    
    _inherit = 'sale.order.line'
    
    @api.multi
    def _get_slot_position(self):
        ''' Text description for position
        '''        
        for line in self:
            res = ''
            
            # -----------------------------------------------------------------
            # Assigned q.:
            # -----------------------------------------------------------------
            for assigned in self.assigned_line_ids: # Assigned quants:
                res += _('ASS.: %s >> %s') % (
                    assigned.quantity,
                    line.product_id.default_slot_id.name or _('(to assign)'),
                    )

            # -----------------------------------------------------------------
            # Loading q.:
            # -----------------------------------------------------------------
            for move in self.load_line_ids: # BF document
                res += _('CONS.: %s >> %s') % (
                    move.product_uom_qty,
                    move.slot_id.name or _('(not loaded)'),
                    )

            line.position_slot = res
        return True
         
    # -------------------------------------------------------------------------    
    # Columns:
    # -------------------------------------------------------------------------
    position_slot = fields.Text(
        #'stock.location.slot', 
        string='Slot position', 
        compute='_get_slot_position')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
