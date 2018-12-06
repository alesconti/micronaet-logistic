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


class StockPicking(models.Model):
    """ Model name: Stock picking import document
    """
    
    _inherit = 'stock.picking'

    # -------------------------------------------------------------------------
    #                            WORKFLOW ACTION:
    # -------------------------------------------------------------------------
    @api.model
    def workflow_ordered_ready(self):
        ''' Read temp table where temporary order is
        '''
        # ---------------------------------------------------------------------
        # Pool used:
        # ---------------------------------------------------------------------
        # Temp load document:        
        header_pool = self.env['mmac.doca']
        detail_pool = self.env['mmac.doca.line']
        
        # Stock movement:
        move_pool = self.env['stock.move']
        quant_pool = self.env['stock.quant']

        # Sale order detail:
        sale_line_pool = self.env['sale.order.line']
       
        # Purchase order detail:
        #purchase_pool = self.env['purchase.order']
        line_pool = self.env['purchase.order.line']
        
        # Partner:
        partner_pool = self.env['res.partner']
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
        #                          Load order details
        # ---------------------------------------------------------------------
        purchase_lines = line_pool.search([
            ('order_id.logistic_state', '=', 'confirmed'), # draft, done
            ])
            
        # Sorted with create date (first will be linked first!    
        product_line_db = {}
        for line in purchase_lines.sorted(
                key=lambda x: x.order_id.create_date):
                
            logistic_undelivered_qty = line.logistic_undelivered_qty
            if logistic_undelivered_qty <= 0.0:
                continue # line was yet completed!

            product = line.product_id
            if product not in product_line_db:
                product_line_db[product] = []
            product_line_db[product].append(
                [line, line.logistic_undelivered_qty])    

        # ---------------------------------------------------------------------
        #                         DB from order temp:
        # ---------------------------------------------------------------------
        # Read header data:
        headers = header_pool.search([])
        sale_line_ready = [] # ready line after assign load qty to purchase
        move_position = [] # stock move to set supplier position
        pickings = []#self.env['stock.picking']
        for header in headers:
            partner = header.partner_id
            scheduled_date = header.date_order
            name = header.name # same as order_ref
            origin = _('%s [%s]') % (header.order_ref, header.date_order[:10])
            
            picking = self.create({       
                'partner_id': partner.id,
                'scheduled_date': scheduled_date,
                'origin': origin,
                #'move_type': 'direct',
                'picking_type_id': logistic_pick_in_type_id,
                'group_id': False,
                'location_id': location_from,
                'location_dest_id': location_to,
                #'priority': 1,                
                'state': 'done', # XXX done immediately
                })
            pickings.append(picking)
            
            for line in header.doca_line:
                product = line.product_id
                product_qty = line.product_qty
                for purchase_line in product_line_db.get(product, []):
                    load_line, logistic_undelivered_qty = purchase_line
                    if product_qty >= logistic_undelivered_qty:
                        # -----------------------------------------------------
                        # Covered all purchase line:
                        # -----------------------------------------------------
                        select_qty = logistic_undelivered_qty # received
                        # Logistic status for sale order line == ready
                        sale_line_ready.append(load_line.logistic_sale_id)
                    else: 
                        # -----------------------------------------------------
                        # Covered Partially purchase line:
                        # -----------------------------------------------------
                        select_qty = product_qty # all

                    product_qty -= select_qty
                    
                    # ---------------------------------------------------------
                    # Create movement (not load stock):
                    # ---------------------------------------------------------
                    move_position.append(move_pool.create({
                        'company_id': company.id,
                        'partner_id': partner.id,
                        'picking_id': picking.id,
                        'product_id': product.id, 
                        'name': product.name or ' ',
                        'date': scheduled_date,
                        'date_expected': scheduled_date,
                        'location_id': location_from,
                        'location_dest_id': location_to,
                        'product_uom_qty': select_qty,
                        'product_uom': product.uom_id.id,
                        'state': 'done',
                        'origin': origin,
                        # Sale order line link:
                        'logistic_load_id': load_line.logistic_sale_id.id,
                        # Purchase order line line: 
                        'logistic_purchase_id': load_line.id,
                        'purchase_line_id': load_line.id, # XXX needed?
                        #'logistic_quant_id': quant.id, # XXX no quants here

                        # group_id
                        # reference'
                        # sale_line_id
                        # procure_method,
                        #'product_qty': select_qty,
                        }))
                    if product_qty <= 0.0:
                        break    
                
                # -------------------------------------------------------------        
                # Not covered with orders, load stock directly:
                # -------------------------------------------------------------       
                if product_qty > 0.0:
                    # ---------------------------------------------------------
                    # Create stock quants for remain data
                    # ---------------------------------------------------------
                    # TODO link to stock move?
                    quant = quant_pool.create({
                        'company_id': company.id,
                        'product_id': product.id, 
                        'in_date': scheduled_date,
                        'location_id': location_to,
                        'quantity': product_qty,
                        })

                    # ---------------------------------------------------------
                    # Create stock move (load stock with quants):
                    # ---------------------------------------------------------
                    move_position.append(move_pool.create({
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
                        'logistic_quant_id': quant.id, # Link 
                        # XXX Unlinked from purchase and sale order line!
                        # Sale order line link:
                        #'logistic_load_it': load_line.logistic_sale_id.id,
                        # Purchase order line line: 
                        #'logistic_purchase_id': load_line.id,
                        #'purchase_line_id': load_line.id, # XXX needed?

                        # group_id
                        # reference'
                        # sale_line_id
                        # purchase_line_id
                        # procure_method,
                        #'product_qty': select_qty,
                        }))

        # ---------------------------------------------------------------------
        # Update Logistic status:
        # ---------------------------------------------------------------------
        # Mark order line ready:
        _logger.info('Update sale order line as ready:')
        for line in sale_line_ready:
            line.write({
                'logistic_state': 'ready',
                })
                
        # Check ready order with this line set as ready 
        _logger.info('Update sale order as ready:')
        sale_line_pool.logistic_check_ready_order(sale_line_ready)

        # ---------------------------------------------------------------------
        # Update stock position for stock move BF
        # ---------------------------------------------------------------------
        _logger.info('Update stock position loading product:')
        for move in move_position:
            move.set_stock_move_position()

        # ---------------------------------------------------------------------
        # Export on file (report)?
        # ---------------------------------------------------------------------
        _logger.info('Extract report for BF:')
        for picking in pickings:
            picking.export_excel_picking_report()

        # ---------------------------------------------------------------------
        #                          Clean temp data:
        # ---------------------------------------------------------------------
        headers.unlink() # line deleted in cascade!        
        return True        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
