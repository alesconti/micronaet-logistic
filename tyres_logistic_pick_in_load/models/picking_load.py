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

class StockPickingDelivery(models.Model):
    """ Model name: Stock picking import document
    """
    
    _name = 'stock.picking.delivery'
    _description = 'Generator of delivery'
    _rec_name = 'create_date'

    # -------------------------------------------------------------------------
    #                            WORKFLOW ACTION:
    # -------------------------------------------------------------------------
    @api.multi
    def confirm_stock_load(self):
        ''' Create new picking unloading the selected material
        '''
        # ---------------------------------------------------------------------
        # Pool used:
        # ---------------------------------------------------------------------
        # Stock:
        picking_pool = self.env['stock.picking']
        move_pool = self.env['stock.move']
        quant_pool = self.env['stock.picking.delivery.quant']

        # Sale order detail:
        sale_line_pool = self.env['sale.order.line']
       
        # Purchase order detail:
        purchase_pool = self.env['purchase.order']
        
        # Partner:
        company_pool = self.env['res.company']
        
        # ---------------------------------------------------------------------
        #                          Load parameters
        # ---------------------------------------------------------------------
        company = company_pool.search([])[0]
        logistic_pick_in_type = company.logistic_pick_in_type_id

        logistic_pick_in_type_id = logistic_pick_in_type.id
        location_from = logistic_pick_in_type.default_location_src_id.id
        location_to = logistic_pick_in_type.default_location_dest_id.id

        # ---------------------------------------------------------------------
        # Create picking:
        # ---------------------------------------------------------------------
        sale_line_ready = [] # ready line after assign load qty to purchase

        partner = self.supplier_id
        scheduled_date = self.create_date
        name = self.name or _('Not assigned')
        origin = _('%s [%s]') % (name, scheduled_date)

        picking = picking_pool.create({       
            'partner_id': partner.id,
            'scheduled_date': scheduled_date,
            'origin': origin,
            #'move_type': 'direct',
            'picking_type_id': logistic_pick_in_type_id,
            'group_id': False,
            'location_id': location_from,
            'location_dest_id': location_to,
            #'priority': 1,                
            'state': 'done', # immediately!
            })
        self.picking_id = picking.id

        # ---------------------------------------------------------------------
        # Append stock.move detail (or quants if in stock)
        # ---------------------------------------------------------------------           
        sale_line_ready = []
        for line in self.purchase_line_ids: # purchase.order.line
            product = line.product_id
            product_qty = line.logistic_delivered_manual
            remain_qty = line.logistic_undelivered_qty
            logistic_sale_id = line.logistic_sale_id
            
            if product_qty >= remain_qty:
                sale_line_ready.append(logistic_sale_id)
                if product_qty > remain_qty:
                    quant_pool.create({
                        # date and uid are default
                        'order_id': self.id,
                        'product_id': product.id, 
                        'product_qty': product_qty - remain_qty,
                        'price': line.price_unit,                    
                        })
                product_qty = remain_qty # For stock movement

            # ---------------------------------------------------------
            # Create movement (not load stock):
            # ---------------------------------------------------------
            move_pool.create({
                'company_id': company.id,
                'partner_id': partner.id,
                'picking_id': picking.id,
                'product_id': product.id, 
                'name': product.name or ' ',
                'date': scheduled_date,
                'date_expected': scheduled_date,
                'location_id': location_from,
                'location_dest_id': location_to,
                'product_uom_qty': product_qty,
                'product_uom': product.uom_id.id,
                'state': 'done',
                'origin': origin,
                
                # Sale order line link:
                'logistic_load_id': logistic_sale_id.id,
                
                # Purchase order line line: 
                'logistic_purchase_id': line.id,
                
                #'purchase_line_id': load_line.id, # XXX needed?
                #'logistic_quant_id': quant.id, # XXX no quants here

                # group_id
                # reference'
                # sale_line_id
                # procure_method,
                #'product_qty': select_qty,
                })
            
        # Reset manual selection and link to pre-picking doc:    
        self.purchase_line_ids.write({
            'delivery_id': False,
            'logistic_delivered_manual': 0.0,
            })

        # ---------------------------------------------------------------------
        # TODO: Load stock picking for extra
        # ---------------------------------------------------------------------
        quants = quant_pool.search([('order_id', '=', self.id)])
        for quant in quants:
            # TODO Extract to account and get the resuls file:
            
            quant.account_sync = True # XXX If corrected improted

        # ---------------------------------------------------------------------
        # Sale order: Update Logistic status:
        # ---------------------------------------------------------------------
        # Mark Sale Order Line ready:
        _logger.info('Update sale order line as ready:')
        for line in sale_line_ready:
            line.write({
                'logistic_state': 'ready',
                })
                
        # Check Sale Order with all line ready:
        _logger.info('Update sale order as ready:')
        sale_line_pool.logistic_check_ready_order(sale_line_ready)

        # ---------------------------------------------------------------------
        # Check Purchase order ready
        # ---------------------------------------------------------------------
        # TODO debug:
        _logger.info('Check purchase order closed (this):')
        return purchase_pool.check_order_confirmed_done([self.id])

    # -------------------------------------------------------------------------
    # Button event:
    # -------------------------------------------------------------------------
    @api.multi
    def open_purchase_line(self):
        ''' Open current opened line
        '''
        tree_view_id = self.env.ref(
            'tyres_logistic_pick_in_load.view_delivery_selection_tree').id
        search_view_id = self.env.ref(
            'tyres_logistic_pick_in_load.view_delivery_selection_search').id
            
        # Select record to show 
        # TODO filter active!
        purchase_pool = self.env['purchase.order.line']
        purchases = purchase_pool.search([
            ('order_id.partner_id', '=', self.supplier_id.id),
            #('logistic_undelivered_qty', '>', 0.0), # TODO change with logistic_status
            ])
        purchase_ids = []    
        for purchase in purchases:
            if purchase.logistic_undelivered_qty:
                purchase_ids.append(purchase.id)

        return {
            'type': 'ir.actions.act_window',
            'name': _('Purcase line:'),
            'view_type': 'form',
            'view_mode': 'tree',
            #'res_id': 1,
            'res_model': 'purchase.order.line',
            'view_id': tree_view_id,
            'search_view_id': search_view_id,
            'views': [(tree_view_id, 'tree')],
            'domain': [('id', 'in', purchase_ids)],
            'context': self.env.context,
            'target': 'current', # 'new'
            'nodestroy': False,
            }
    
    # -------------------------------------------------------------------------
    # Columns:
    # -------------------------------------------------------------------------
    name = fields.Char('Ref.', size=64)
    create_date = fields.Datetime(
        'Create date', required=True, default=fields.Datetime.now())
    create_uid = fields.Many2one(
        'res.users', 'Create user', required=True, default=lambda s: s.env.user)
    supplier_id = fields.Many2one(
        'res.partner', 'Supplier', required=True, 
        domain='[("supplier", "=", True)]',
        )
    carrier_id = fields.Many2one('carrier.supplier', 'Carrier')
    picking_id = fields.Many2one('stock.picking', 'Picking')
    move_ids = fields.One2many('stock.move', related='picking_id.move_lines')

class StockPickingDeliveryQuant(models.Model):
    """ Model name: Stock line that create real load of stock
    """
    
    _name = 'stock.picking.delivery.quant'
    _description = 'Extra purchase line'
    _rec_name = 'product_id'
    
    # -------------------------------------------------------------------------
    # Columns:
    # -------------------------------------------------------------------------
    order_id = fields.Many2one(
        'stock.picking.delivery', 'Order')
    create_date = fields.Datetime(
        'Create date', default=fields.Datetime.now())
    create_uid = fields.Many2one(
        'res.users', 'Create user', default=lambda s: s.env.user)
    product_id = fields.Many2one(
        'product.product', 'Product', required=True)
    product_qty = fields.Float('Q.', digits=(16, 2), required=True)
    price = fields.Float('Price', digits=(16, 2))
    account_sync = fields.Boolean('Account sync')
    

class PurchaseOrderLine(models.Model):
    """ Model name: Purchase Order Line
    """
    _inherit = 'purchase.order.line'
    
    @api.multi
    def delivery_0(self):
        ''' Add +1 to manual arrived qty
        '''
        active_id = self.env.context.get('active_id')
        if not active_id:
            raise exceptions.Warning('Cannot link purchase delivery!') 
            
        return self.write({
            'logistic_delivered_manual': 0,
            'delivery_id': False,
            })        

    @api.multi
    def delivery_more_1(self):
        ''' Add +1 to manual arrived qty
        '''
        active_id = self.env.context.get('active_id')
        if not active_id:
            raise exceptions.Warning('Cannot link purchase delivery!') 
            
        return self.write({
            'logistic_delivered_manual': self.logistic_delivered_manual + 1.0,
            'delivery_id': active_id,
            })        

    @api.multi
    def delivery_less_1(self):
        ''' Add +1 to manual arrived qty
        '''
        active_id = self.env.context.get('active_id')
        if not active_id:
            raise exceptions.Warning('Cannot link purchase delivery!') 
            
        logistic_delivered_manual = self.logistic_delivered_manual
        if logistic_delivered_manual < 1.0:
            raise exceptions.Warning('Nothing to remove!') 
            
        if logistic_delivered_manual <= 1.0:
            active_id = False
        return self.write({
            'logistic_delivered_manual': logistic_delivered_manual - 1.0,
            'delivery_id': active_id,
            })        

    @api.multi
    def delivery_all(self):
        ''' Add +1 to manual arrived qty
        '''
        active_id = self.env.context.get('active_id')
        if not active_id:
            raise exceptions.Warning('Cannot link purchase delivery!') 
        
        logistic_undelivered_qty = self.logistic_undelivered_qty
        if logistic_undelivered_qty <= 0.0:
            raise exceptions.Warning('No more q. to deliver!') 
        
        return self.write({
            'logistic_delivered_manual': self.logistic_undelivered_qty,
            'delivery_id': active_id,
            })        

    # -------------------------------------------------------------------------
    # Columns:
    # -------------------------------------------------------------------------
    delivery_id = fields.Many2one('stock.picking.delivery', 'Delivery')
    logistic_delivered_manual = fields.Float('Manual', digits=(16, 2))

class StockPickingDelivery(models.Model):
    """ Model name: Stock picking import document: add relations
    """
    
    # -------------------------------------------------------------------------
    # Columns:
    # -------------------------------------------------------------------------
    _inherit = 'stock.picking.delivery'

    purchase_line_ids = fields.One2many(
        'purchase.order.line', 'delivery_id', 'Purchase line')
    quant_ids = fields.One2many(
        'stock.picking.delivery.quant', 'order_id', 'Stock quant:')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
