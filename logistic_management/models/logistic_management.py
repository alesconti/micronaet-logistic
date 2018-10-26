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
from odoo import api, fields, models, tools, exceptions, SUPERUSER_ID
from odoo.addons import decimal_precision as dp
from odoo.tools.translate import _


_logger = logging.getLogger(__name__)


class StockMoveIn(models.Model):
    """ Model name: Stock Move
    """
    
    _inherit = 'stock.move'
    
    # -------------------------------------------------------------------------
    #                                   COLUMNS:
    # -------------------------------------------------------------------------
    # TODO Need index?
    # USED STOCK: Linked used
    logistic_assigned_id = fields.Many2one(
        'sale.order.line', 'Link covered to generator', 
        help='Link to sale line the assigned qty', 
        index=True, ondelete='cascade', # remove stock move when delete order
        )

    # SUPPLIER ORDER: Purchase management:
    logistic_purchase_id = fields.many2one(
        'purchase.order.line', 'Link load to purchase', 
        help='Link pick in line to generat purchase line',
        index=True, ondelete='set null',
        )
    # Direct link to sale order line (generated from purchase order):    
    logistic_load_id = fields.many2one(
        'sale.order.line', 'Link load to sale', 
        help='Link pick in line to original sale line (bypass purchase)',
        index=True, ondelete='set null',
        )
    
    # DELIVER: Pick out
    logistic_unload_id = fields.many2one(
        'sale.order.line', 'Link unload to sale', 
        help='Link pick out line to sale order',
        index=True, ondelete='set null',
        )
    
    
class PurchaseOrderLine(models.Model):
    """ Model name: Purchase Order Line
    """
    
    _inherit = 'purchase.order.line'
    
    # -------------------------------------------------------------------------
    #                                   COLUMNS:
    # -------------------------------------------------------------------------
    #                             RELATIONAL FIELDS:
    # -------------------------------------------------------------------------    
    # Relation many 2 one:
    logistic_sale_id = fields.Many2one(
        'sale.order.line', 'Link to generator', 
        help='Link generator sale order line: one customer line=one purchase',
        index=True, ondelete='set null',
        )

    # Relation one 2 many:
    load_line_ids = fields.One2many(
        'stock.move', 'logistic_load_id', 'Linked load to purchase', 
        help='Load linked to this purchase line',
        )

class SaleOrderLine(models.Model):
    """ Model name: Sale Order Line
    """
    
    _inherit = 'sale.order.line'
    
    # -------------------------------------------------------------------------
    #                            COMPUTE FIELDS FUNCTION:
    # -------------------------------------------------------------------------
    @api.multi
    @api.depends('assigned_line_ids', 'purchase_line_ids', 'load_line_ids')
    def _get_logist_status_field(self):
        ''' Manage all data for logistic situation in sale order:
        '''
        for line in self:
            state = 'draft'

            # -----------------------------------------------------------------
            # OC: Ordered qty: 
            # -----------------------------------------------------------------
            logistic_order_qty = line.product_qty # TODO Verify
            
            # -----------------------------------------------------------------
            # ASS: Assigned:
            # -----------------------------------------------------------------
            logistic_covered_qty = 0.0
            for move in assigned_line_ids:
                logistic_covered_qty += move.product_uom_qty # TODO verify
            line.logistic_covered_qty = logistic_covered_qty
            
            # State valuation:
            if logistic_order_qty = logistic_covered_qty:
                state = 'ready' # All in stock 
            else:
                state = 'uncovered' # To order    

            # -----------------------------------------------------------------
            # PUR: Purchase (order done):
            # -----------------------------------------------------------------
            logistic_purchase_qty = 0.0
            for purchase in line.purchase_line_ids:
                logistic_purchase_qty += purchase.product_uom_qty # TODO verify
            line.logistic_purchase_qty = logistic_purchase_qty
            
            # -----------------------------------------------------------------
            # UNC: Uncovered (to purchase) [OC - ASS - PUR]:
            # -----------------------------------------------------------------
            logistic_uncovered_qty = \
                logistic_order_qty - logistic_covered_qty - \
                logistic_purchase_qty
            line.logistic_uncovered_qty = logistic_uncovered_qty

            # State valuation:
            if state != 'ready' and not logistic_uncovered_qty: # XXX          
                state = 'ordered' # A part (or all) is order

            # -----------------------------------------------------------------
            # BF: Received (loaded in stock):
            # -----------------------------------------------------------------
            logistic_received_qty = 0.0
            for move in line.received_line_ids:
                logistic_received_qty += move.product_uom_qty # TODO verify
            line.logistic_received_qty = logistic_received_qty
            
            # -----------------------------------------------------------------
            # REM: Remain to receive [OC - ASS - BF]:
            # -----------------------------------------------------------------
            logistic_remain_qty = \
                logistic_order_qty - logistic_covered_qty - \
                logistic_received_qty
            line.logistic_remain_qty = logistic_remain_qty    

            # State valuation:
            if state != 'ready' and not logistic_remain_qty: # XXX
                state = 'ready' # All present coveder or in purchase

            # -----------------------------------------------------------------
            # BC: Delivered:
            # -----------------------------------------------------------------
            logistic_delivered_qty = 0.0
            for move in line.delivered_line_ids:
                logistic_delivered_qty += move.product_uom_qty # TODO verify
            line.logistic_delivered_qty = logistic_delivered_qty
            
            # -----------------------------------------------------------------
            # UND: Undelivered (remain to pick out) [OC - BC]
            # -----------------------------------------------------------------
            logistic_undelivered_qty = \
                logistic_order_qty - logistic_delivered_qty
            line.logistic_undelivered_qty = logistic_undelivered_qty

            # State valuation:
            if not logistic_undelivered_qty: # XXX
                state = 'done' # All delivered to customer
            
            # -----------------------------------------------------------------
            # Write data:
            # -----------------------------------------------------------------
            line.logistic_state = state

    # -------------------------------------------------------------------------
    #                                   COLUMNS:
    # -------------------------------------------------------------------------
    #                              RELATION MANY 2 ONE
    # -------------------------------------------------------------------------
    # A. Assigned stock:
    assigned_line_ids = fields.One2many(
        'stock.move', 'logistic_used_generator_id', 'Assign from stock',
        help='Assign all this q. to this line (usually one2one',
        )

    # B. Purchased:
    purchase_line_ids = fields.One2many(
        'purchase.order.line', 'logistic_purchase_id', 'Linked to purchase', 
        help='Supplier ordered line linked to customer\'s one',
        )
    load_line_ids = fields.One2many(
        'stock.move', 'logistic_load_id', 'Linked load to sale', 
        help='Loaded movement in picking in documents',
        )

    # C. Deliver:
    delivered_line_ids = fields.One2many(
        'stock.move', 'logistic_unload_id', 'Linked to deliveder', 
        help='Deliver movement in pick out documents',
        )
    
    # -------------------------------------------------------------------------
    #                               FUNCTION FIELDS:
    # -------------------------------------------------------------------------
    # Computed q.ty data:
    logistic_covered_qty = fields.Float(
        'Covered qty', digits=(16, config(int['price_accuracy'])),
        help='Qty covered with internal stock',
        readonly=True, compute='_get_logist_status_field', multi=True,
        store=False,
        )
    logistic_uncovered_qty = fields.Float(
        'Uncovered qty', digits=(16, config(int['price_accuracy'])),
        help='Qty not covered with internal stock (so to be purchased)',
        readonly=True, compute='_get_logist_status_field', multi=True,
        store=False,
        )
    logistic_purchase_qty = fields.Float(
        'Purchae qty', digits=(16, config(int['price_accuracy'])),
        help='Qty order to supplier',
        readonly=True, compute='_get_logist_status_field', multi=True,
        store=False,
        )
    logistic_received_qty = fields.Float(
        'Received qty', digits=(16, config(int['price_accuracy'])),
        help='Qty received with pick in delivery',
        readonly=True, compute='_get_logist_status_field', multi=True,
        store=False,
        )
    logistic_remain_qty = fields.Float(
        'Remain qty', digits=(16, config(int['price_accuracy'])),
        help='Qty remain to receive to complete ordered',
        readonly=True, compute='_get_logist_status_field', multi=True,
        store=False,
        )
    logistic_delivered_qty = fields.Float(
        'Delivered qty', digits=(16, config(int['price_accuracy'])),
        help='Qty deliverer  to final customer',
        readonly=True, compute='_get_logist_status_field', multi=True,
        store=False,
        )
    logistic_undelivered_qty = fields.Float(
        'Not delivered qty', digits=(16, config(int['price_accuracy'])),
        help='Qty not deliverer to final customer',
        readonly=True, compute='_get_logist_status_field', multi=True,
        store=False,
        )
    
    # State (sort of workflow):
    logistic_state = fields.Selection([
        ('draft', 'Custom order'), # Draft, order is received now
        ('uncovered', 'Uncovered'), # Not coveder to be ordered
        ('ordered', 'Ordered'), # Supplier order defined
        ('ready', 'Ready'), # Order to be picked out (all in stock)
        ('done', 'Done'), # Delivered qty (order will be closed)
        ], 'Logistic state', default='draft',
        readonly=True, compute='_get_logist_status_field', multi=True,
        store=True, # for create columns
        ),
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
