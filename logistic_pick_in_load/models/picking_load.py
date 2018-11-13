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

    @api.model
    def generate_bf_picking_document(self):
        ''' Read temp table where temporary order is
        '''
        # ---------------------------------------------------------------------
        # Pool used:
        # ---------------------------------------------------------------------
        # Temp load document:        
        header_pool = self.env['mmac_ardo']
        detail_pool = self.env['mmac_ardoline']
        
        # Stock movement:
        move_pool = self.env['stock.move']
        quant_pool = self.env['stock.quant']
       
        # Purchase order detail:
        #purchase_pool = self.env['purchase.order']
        line_pool = self.env['purchase.order.line']
        
        # Partner:
        partner_pool = self.env['res.partner']
        company_pool = self.env['res.company']
        
        # ---------------------------------------------------------------------
        #                         DB from order temp:
        # ---------------------------------------------------------------------
        # Read header data:
        header_db = {}
        headers = header_pool.search([])
        for header in headers:
            header_db[header] = []
        
        details = detail_pool.search([])
        for detail in details:
            header_db[detail.header_id].append(detail)


        # ---------------------------------------------------------------------
        #                          Load parameters
        # ---------------------------------------------------------------------
        company = company.search([])[0]
        logistic_pick_in_type_id = company.logistic_pick_in_type_id.id
        
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
        #                   Create documents depend on loaded data
        # ---------------------------------------------------------------------
        for header in header_db:
            details = header_db[header]
            
            partner = partner_pool.search([]) # TODO search partner field
            scheduled_date = '2018-01-01' # TODO get data
            origin = False # TODO
            
            picking = self.create({                
                # TODO
                'partner_id': partner[0].id,
                'scheduled_date': scheduled_date,
                'origin': origin,
                #'move_type': 'direct',
                'pickin_type_id': logistic_pick_in_type_id,
                'group_id': False,
                #'priority': 1,                
                'state': 'done', # XXX done immediately
                })

            for detail in details:
                product = detail.
                product_qty = detail.product_qty# TODO    
                loop_again = product_qty > 0.0 # First test
                while loop_again:
                    for purchase in product_line_db.get(
                    move = move.create({
                        # TODO
                        'picking_id': picking.id,
                        'product_id': 
                        })
                    # TODO loop_again    
        
        # ---------------------------------------------------------------------
        #                          Clean temp data:
        # ---------------------------------------------------------------------
        # Delete detail line:
        details.unlink()
        headers.unlink()
        
        return True
        
    # -------------------------------------------------------------------------
    # COLUMNS:
    # -------------------------------------------------------------------------
    #product_suffix = fields.Char('Product suffix', size=10)
    # -------------------------------------------------------------------------
    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
