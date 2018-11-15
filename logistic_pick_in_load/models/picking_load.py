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
        header_pool = self.env['mmac_doca']
        detail_pool = self.env['mmac_doca_line']
        
        # Stock movement:
        move_pool = self.env['stock.move']
        quant_pool = self.env['stock.quant']
       
        # Purchase order detail:
        #purchase_pool = self.env['purchase.order']
        line_pool = self.env['purchase.order.line']
        
        # Partner:
        partner_pool = self.env['res.partner']
        company_pool = self.env['res.company']
        import pdb; pdb.set_trace()
        
        # ---------------------------------------------------------------------
        #                          Load parameters
        # ---------------------------------------------------------------------
        company = company.search([])[0]
        logistic_pick_in_type_id = company.logistic_pick_in_type_id.id
        location_from = logistic_pick_in_type_id.default_location_src_id.id
        location_to = logistic_pick_in_type_id.default_location_dest_id.id

        # ---------------------------------------------------------------------
        #                          Load order details
        # ---------------------------------------------------------------------
        purchase_lines = line_pool.search([
            ('purchase_id.logistic_state', '=', 'confirmed'), # draft, done
            ])
            
        # Sorted with create date (first will be linked first!    
        product_line_db = {}
        for line in purchase_lines.sorted(
                key=lambda x: x.purchase_id.create_date):
                
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
        for header in headers:
            partner = header.partner
            scheduled_date = header.date_order
            name = header.name, # same as order_ref
            origin = _('%s - %s') % (header.order_ref, order.date_order)
            
            picking = self.create({                
                'partner_id': partner.id,
                'scheduled_date': scheduled_date,
                'origin': origin,
                #'move_type': 'direct',
                'picking_type_id': logistic_pick_in_type_id,
                'group_id': False,
                #'priority': 1,                
                'state': 'done', # XXX done immediately
                })
            
            for line in header.line_ids:
                product = line.product_id
                product_qty = line.product_qty
                for purchase in product_line_db.get(product, []):
                    load_line, logistic_undelivered_qty = purchase
                    if product_qty > logistic_undelivered_qty:
                        # Partially covered:
                        select_qty = logistic_undelivered_qty
                    else: # covered all
                        select_qty = product_qty    
                    product_qty -= select_qty
                    
                    # Create movement:
                    move.create({
                        'company_id': company.id,
                        'partner_id': partner.id,
                        'picking_id': picking.id,
                        'product_id': product.id, 
                        'date': scheduled_date,
                        'date_expected': scheduled_date,
                        'location_id': location_from,
                        'location_dest_id': location_to,
                        'logistic_purchase_id': purchase.id,
                        'product_qty': select_qty,
                        'product_uom_qty': select_qty,
                        'product_uom': product.uom_id.id,
                        'state': 'done',
                        #'origin': 
                        # group_id
                        # reference'
                        # sale_line_id
                        # purchase_line_id
                        # procure_method,
                        # 
                        })
                    if product_qty <= 0.0:
                        break    
                
                # -------------------------------------------------------------        
                # Not covered with orders, load stock directly:
                # -------------------------------------------------------------        
                if product_qty > 0.0:
                    # ---------------------------------------------------------
                    # Create stock move:
                    # ---------------------------------------------------------
                    move.create({
                        'company_id': company.id,
                        'partner_id': partner.id,
                        'picking_id': picking.id,
                        'product_id': product.id, 
                        'date': scheduled_date,
                        'date_expected': scheduled_date,
                        'location_id': location_from,
                        'location_dest_id': location_to,
                        #'logistic_purchase_id': purchase.id,
                        'product_qty': product_qty,
                        'product_uom_qty': product_qty,
                        'product_uom': product.uom_id.id,
                        'state': 'done',
                        #'origin': 
                        # group_id
                        # reference'
                        # sale_line_id
                        # purchase_line_id
                        # procure_method,
                        })
                    
                    # ---------------------------------------------------------
                    # Create stock quants for remain data
                    # ---------------------------------------------------------
                    # TODO link to stock move?
                    data_pool.create({
                        'company_id': company.id,
                        'product_id': product.id, 
                        'in_date': scheduled_date,
                        'location_id': location_to,
                        'quantity': product_qty,
                        })

        # ---------------------------------------------------------------------
        #                          Clean temp data:
        # ---------------------------------------------------------------------
        # Delete detail line:
        headers.unlink() # line deleted in cascade!
        return True
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
