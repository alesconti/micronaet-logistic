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


class StockMoveIn(models.Model):
    """ Model name: Stock Move
    """
    
    _inherit = 'stock.move'
    
    # -------------------------------------------------------------------------
    #                                   COLUMNS:
    # -------------------------------------------------------------------------
    # TODO Need index?
    # USED STOCK: Linked used
    # Moved in stock.quant:
    #logistic_assigned_id = fields.Many2one(
    #    'sale.order.line', 'Link covered to generator', 
    #    help='Link to sale line the assigned qty', 
    #    index=True, ondelete='cascade', # remove stock move when delete order
    #    )

    # Direct link to sale order line (generated from purchase order):    
    logistic_load_id = fields.Many2one(
        'sale.order.line', 'Link load to sale', 
        help='Link pick in line to original sale line (bypass purchase)',
        index=True, ondelete='set null',
        )
    
    # DELIVER: Pick out
    logistic_unload_id = fields.Many2one(
        'sale.order.line', 'Link unload to sale', 
        help='Link pick out line to sale order',
        index=True, ondelete='set null',
        )

    # SUPPLIER ORDER: Purchase management:
    logistic_purchase_id = fields.Many2one(
        'purchase.order.line', 'Link load to purchase',
        help='Link pick in line to generat purchase line',
        index=True, ondelete='set null',
        )

class PurchaseOrderLine(models.Model):
    """ Model name: Purchase Order Line
    """
    
    _inherit = 'purchase.order.line'
    
    # -------------------------------------------------------------------------
    #                                   COLUMNS:
    # -------------------------------------------------------------------------
    # Relation one 2 many:
    load_line_ids = fields.One2many(
        'stock.move', 'logistic_purchase_id', 'Linked load to purchase', 
        help='Load linked to this purchase line',
        )

class StockQuant(models.Model):
    """ Model name: Stock quant
    """
    
    _inherit = 'stock.quant'
    
    # -------------------------------------------------------------------------
    #                                   COLUMNS:
    # -------------------------------------------------------------------------
    logistic_assigned_id = fields.Many2one(
        'sale.order.line', 'Link covered to generator', 
        help='Link to sale line the assigned qty', 
        index=True, ondelete='cascade', # remove stock move when delete order
        )
    
class SaleOrder(models.Model):
    """ Model name: Sale Order
    """
    
    _inherit = 'sale.order'

    # State (sort of workflow):
    # TODO
    #dropshipping = fields.Boolean('Dropshipping', 
    #    help='All order will be managed externally')
        
    logistic_state = fields.Selection([
        ('draft', 'Order draft '), # Draft, new order received
        ('order', 'Order confirmed'), # Quotation transformed
        
        ('dropship', 'Dropship'), # Dropship order XXX to be used?
        ('pending', 'Pending delivery'), # Waiting for delivery
        ('ready', 'Ready'), # Ready for transfer
        ('done', 'Done'), # Delivered or closed XXX manage partial delivery
        ], 'Logistic state', default='draft',
        #readonly=True, 
        #compute='_get_logist_status_field', multi=True,
        #store=True, # TODO store True # for create columns
        )

class SaleOrderLine(models.Model):
    """ Model name: Sale Order Line
    """
    
    _inherit = 'sale.order.line'
    
    # -------------------------------------------------------------------------
    #                    LOGISTIC OPERATION FUNCTION:
    # -------------------------------------------------------------------------
    # A. Assign available q.ty in stock assign a stock movement / quants
    @api.model
    def logistic_assign_stock_to_customer_order(self):
        ''' Logistic phasae 1:
            Assign stock q. available to order product creating a 
            stock.move or stock.quant movement 
            Evaluate also if we can use alternative product
        '''
        import pdb; pdb.set_trace()
        # TODO read paremeter:
        mode = 'first_available' # TODO move management: 'better_available'
        sort = 'create_date' # TODO manage in parameters
        location_id = 12
        now = fields.Datetime.now()

        quant_pool = self.env['stock.quant']
        line_pool = self.env['sale.order.line']
        lines = line_pool.search([
            # TODO manage order status (only confirmed will be searched)
            #('order_id.state', '=', 'sale'),
            ('order_id.state', 'in', ('draft', 'sent')),
            
            ('logistic_state', '=', 'draft'),
            ])

        # ---------------------------------------------------------------------
        # Sort options:
        # ---------------------------------------------------------------------
        if sort == 'create_date':
            sorted_line = sorted(lines, key=lambda x: x.order_id.create_date)
        else: # deadline
            sorted_line = sorted(lines, key=lambda x: x.order_id.validity_date)    
            
        # ---------------------------------------------------------------------
        #                  Modify sale order line status:
        # ---------------------------------------------------------------------
        update_db = {}
        for line in sorted_line:
            product = line.product_id
            
            # Kit line not used:
            if not product or product.is_kit:
                update_db[line] = {
                    'logistic_state': 'unused',
                    }
                continue # Comment line
            
            order_qty = line.product_uom_qty
            
            # Similar pool, product first:
            product_list = [product]
            if product.similar_ids:
                product_list.extend([
                    item for item in product.similar_ids]) # XXX Check data!
            
            # -----------------------------------------------------------------
            # Use stock to cover order:
            # -----------------------------------------------------------------
            state = False # Used for check if used some pool product
            for used_product in product_list:                    
                stock_qty = used_product.qty_available

                # -------------------------------------------------------------
                # Manage mode of use stock: (TODO better available)
                # -------------------------------------------------------------
                if mode == 'first_available' and stock_qty:
                    if stock_qty > order_qty:
                        quantity = order_qty
                        state = 'ready'
                    else:    
                        quantity = stock_qty
                        state = 'uncovered'

                    company = line.order_id.company_id # XXX
                    data = {
                        'company_id': company.id,
                        'in_date': now,
                        'location_id': location_id,
                        #'lot_id' #'package_id'
                        'product_id': used_product.id,
                        'product_tmpl_id': used_product.product_tmpl_id.id,
                        'quantity': quantity,

                        # Link field:
                        'logistic_assigned_id': line.id,
                        }            
                    quant_pool.create(data)
                    
                    # Update line if quant created                
                    update_db[line] = {
                        'logistic_state': state,
                        }

                # -------------------------------------------------------------
                # TODO manage alternative product here!    
                # -------------------------------------------------------------
                
                # -------------------------------------------------------------
                # Update similar product in order line (if used):
                # -------------------------------------------------------------
                if state and used_product != product:
                    # Update sale line with information:
                    update_db[line]['linked_mode'] = 'similar'
                    update_db[line]['origin_product_id'] = product.id
                    update_db[line]['product_id'] = used_product.id
        
            # No stock passed in unvocered state:
            if line not in update_db: 
                update_db[line] = {
                    'logistic_state': 'uncovered',
                    }
                
        # ---------------------------------------------------------------------
        # Update sale line status:
        # ---------------------------------------------------------------------
        selected_line = []
        selected_order = []
        for line in update_db:
            line.write(update_db[line])
            selected_line.append(line.id)
            if line.order_id not in selected_order:
                selected_order.append(line.order_id)                

        # ---------------------------------------------------------------------
        # Update order status:
        # ---------------------------------------------------------------------
        all_ready = set(['ready'])
        all_done = set(['done'])
        for order in selected_order:
            # Jump yet managed order draft and pending:
            if order.logistic_state in ('dropship', 'ready', 'done'):
                continue

            # Generate list of line state, jump not used:                
            state_list = [
                line.logistic_state for line in order.order_line\
                    if line.logistic_state not in ('unused')]
                    
            # -----------------------------------------------------------------        
            # Update order state depend on all line:        
            # -----------------------------------------------------------------        
            if all_ready == set(state_list):
                order.logistic_state = 'ready'
            elif all_done == set(state_list):
                order.logistic_state = 'done'
            else:    
                order.logistic_state = 'pending'
            # TODO Manage Dropshipping!!    
            
        # ---------------------------------------------------------------------
        # Return view:
        # ---------------------------------------------------------------------
        model_pool = self.env['ir.model.data']
        tree_view_id = model_pool.get_object_reference(
            'logistic_management', 'view_sale_order_line_logistic_tree')[1]
        form_view_id = model_pool.get_object_reference(
            'logistic_management', 'view_sale_order_line_logistic_form')[1]
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Updated lines'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            #'res_id': 1,
            'res_model': 'sale.order.line',
            'view_id': tree_view_id,
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'domain': [('id', 'in', selected_line)],
            'context': self.env.context,
            'target': 'current', # 'new'
            'nodestroy': False,
            }
    
    # -------------------------------------------------------------------------
    #                            COMPUTE FIELDS FUNCTION:
    # -------------------------------------------------------------------------
    @api.multi
    @api.depends('assigned_line_ids', 'purchase_line_ids', 'load_line_ids',
        'delivered_line_ids')
    def _get_logist_status_field(self):
        ''' Manage all data for logistic situation in sale order:
        '''
        for line in self:
            if line.product_id.is_kit:
                # -------------------------------------------------------------
                #                           KIT:
                # -------------------------------------------------------------
                # if is kit >> line not used:
                line.logistic_covered_qty = 0.0
                line.logistic_purchase_qty = 0.0
                line.logistic_uncovered_qty = 0.0
                line.logistic_received_qty = 0.0
                line.logistic_remain_qty = 0.0
                line.logistic_delivered_qty = 0.0
                line.logistic_undelivered_qty = 0.0
                #line.logistic_state = 'unused'
            else:
                # -------------------------------------------------------------
                #                       NORMAL PRODUCT:
                # -------------------------------------------------------------
                #state = 'draft'
                # -------------------------------------------------------------
                # OC: Ordered qty:
                # -------------------------------------------------------------
                logistic_order_qty = line.product_uom_qty
                
                # -------------------------------------------------------------
                # ASS: Assigned:
                # -------------------------------------------------------------
                logistic_covered_qty = 0.0
                for quant in line.assigned_line_ids:
                    logistic_covered_qty += quant.quantity
                line.logistic_covered_qty = logistic_covered_qty
                
                # State valuation:
                #if logistic_order_qty == logistic_covered_qty:
                #    state = 'ready' # All in stock 
                #else:
                #    state = 'uncovered' # To order    

                # -------------------------------------------------------------
                # PUR: Purchase (order done):
                # -------------------------------------------------------------
                logistic_purchase_qty = 0.0
                for purchase in line.purchase_line_ids:
                    logistic_purchase_qty += purchase.product_uom_qty # TODO verify
                line.logistic_purchase_qty = logistic_purchase_qty
                
                # -------------------------------------------------------------
                # UNC: Uncovered (to purchase) [OC - ASS - PUR]:
                # -------------------------------------------------------------
                logistic_uncovered_qty = \
                    logistic_order_qty - logistic_covered_qty - \
                    logistic_purchase_qty
                line.logistic_uncovered_qty = logistic_uncovered_qty

                # State valuation:
                #if state != 'ready' and not logistic_uncovered_qty: # XXX          
                #    state = 'ordered' # A part (or all) is order

                # -------------------------------------------------------------
                # BF: Received (loaded in stock):
                # -------------------------------------------------------------
                logistic_received_qty = 0.0
                for move in line.load_line_ids:
                    logistic_received_qty += move.product_uom_qty # TODO verify
                line.logistic_received_qty = logistic_received_qty
                
                # -------------------------------------------------------------
                # REM: Remain to receive [OC - ASS - BF]:
                # -------------------------------------------------------------
                logistic_remain_qty = \
                    logistic_order_qty - logistic_covered_qty - \
                    logistic_received_qty
                line.logistic_remain_qty = logistic_remain_qty    

                # State valuation:
                #if state != 'ready' and not logistic_remain_qty: # XXX
                #    state = 'ready' # All present coveder or in purchase

                # -------------------------------------------------------------
                # BC: Delivered:
                # -------------------------------------------------------------
                logistic_delivered_qty = 0.0
                for move in line.delivered_line_ids:
                    logistic_delivered_qty += move.product_uom_qty # TODO verify
                line.logistic_delivered_qty = logistic_delivered_qty
                
                # -------------------------------------------------------------
                # UND: Undelivered (remain to pick out) [OC - BC]
                # -------------------------------------------------------------
                logistic_undelivered_qty = \
                    logistic_order_qty - logistic_delivered_qty
                line.logistic_undelivered_qty = logistic_undelivered_qty

                # State valuation:
                #if not logistic_undelivered_qty: # XXX
                #    state = 'done' # All delivered to customer
                
                # -------------------------------------------------------------
                # Write data:
                # -------------------------------------------------------------
                #line.logistic_state = state

    # -------------------------------------------------------------------------
    #                                   COLUMNS:
    # -------------------------------------------------------------------------
    #                              RELATION MANY 2 ONE
    # -------------------------------------------------------------------------
    # A. Assigned stock:
    #assigned_line_ids = fields.One2many(
    #    'stock.move', 'logistic_assigned_id', 'Assign from stock',
    #    help='Assign all this q. to this line (usually one2one',
    #    )
    assigned_line_ids = fields.One2many(
        'stock.quant', 'logistic_assigned_id', 'Assign from stock',
        help='Assign all this q. to this line (usually one2one',
        )

    # B. Purchased:
    purchase_line_ids = fields.One2many(
        'purchase.order.line', 'logistic_sale_id', 'Linked to purchase', 
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
        'Covered qty', digits=dp.get_precision('Product Price'),
        help='Qty covered with internal stock',
        readonly=True, compute='_get_logist_status_field', multi=True,
        store=False,
        )
    logistic_uncovered_qty = fields.Float(
        'Uncovered qty', digits=dp.get_precision('Product Price'),
        help='Qty not covered with internal stock (so to be purchased)',
        readonly=True, compute='_get_logist_status_field', multi=True,
        store=False,
        )
    logistic_purchase_qty = fields.Float(
        'Purchase qty', digits=dp.get_precision('Product Price'),
        help='Qty order to supplier',
        readonly=True, compute='_get_logist_status_field', multi=True,
        store=False,
        )
    logistic_received_qty = fields.Float(
        'Received qty', digits=dp.get_precision('Product Price'),
        help='Qty received with pick in delivery',
        readonly=True, compute='_get_logist_status_field', multi=True,
        store=False,
        )
    logistic_remain_qty = fields.Float(
        'Remain qty', digits=dp.get_precision('Product Price'),
        help='Qty remain to receive to complete ordered',
        readonly=True, compute='_get_logist_status_field', multi=True,
        store=False,
        )
    logistic_delivered_qty = fields.Float(
        'Delivered qty', digits=dp.get_precision('Product Price'),
        help='Qty deliverer  to final customer',
        readonly=True, compute='_get_logist_status_field', multi=True,
        store=False,
        )
    logistic_undelivered_qty = fields.Float(
        'Not delivered qty', digits=dp.get_precision('Product Price'),
        help='Qty not deliverer to final customer',
        readonly=True, compute='_get_logist_status_field', multi=True,
        store=False,
        )
    
    # State (sort of workflow):
    logistic_state = fields.Selection([
        ('unused', 'Unused'), # Line not managed
    
        ('draft', 'Custom order'), # Draft, order is received now
        ('uncovered', 'Uncovered'), # Not coveder to be ordered
        ('ordered', 'Ordered'), # Supplier order defined
        ('ready', 'Ready'), # Order to be picked out (all in stock)
        ('done', 'Done'), # Delivered qty (order will be closed)
        ], 'Logistic state', default='draft',
        #readonly=True, 
        #compute='_get_logist_status_field', multi=True,
        #store=True, # TODO store True # for create columns
        )
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
