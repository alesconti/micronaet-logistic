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

    #@api.depends('name', 'mode')
    @api.multi
    def _get_slot_description(self, ):
        ''' Update description
        '''        
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
                slot.description = mask % (
                    mapping.get(slot.mode, ''),
                    name[:1],
                    name[1:2],
                    name[2:3],
                    name[3:4],
                    name[4:5],
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

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
