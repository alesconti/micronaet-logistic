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

class StockChangeStandardPrice(models.TransientModel):
    _name = 'logistic.manual.operation.wizard'
    _description = 'Logistic manual operation'

    # -------------------------------------------------------------------------
    #                               BUTTON EVENT:    
    # -------------------------------------------------------------------------    
    # ORder phase:
    @api.multi
    def confirm_payment(self):
        ''' A. Confirm draft order if payment is secure
        '''
        order_pool = self.env['sale.order']
        return order_pool.workflow_draft_to_payment()

    @api.multi
    def confirm_order(self):
        ''' B. Confirm quotation in order (explode kit)
        '''
        order_pool = self.env['sale.order']
        return order_pool.workflow_payment_to_order()

    @api.multi
    def assign_stock(self):
        ''' C. Assign stock product to open orders
        '''
        line_pool = self.env['sale.order.line']
        return line_pool.workflok_order_to_uncovered()

    # Purchase phase:
    @api.multi
    def generate_purchase(self):
        ''' D. Generate purchase order for not cover qty
        '''
        line_pool = self.env['sale.order.line']       
        return line_pool.workflow_uncovered_pending()

    @api.multi
    def confirm_generated_purchase(self):
        ''' D2. Confirm purchase order created
        '''
        purchase_pool = self.env['purchase.order']       
        purchases = purchase_pool.search([
            ('logistic_state', '=', 'draft'),
            ])
        return purchases.write({
            'logistic_state': 'confirmed',
            })    

    # BF Load pchase:        
    @api.multi
    def update_ready(self):
        ''' E. Update order ready with stock or load
        '''
        picking_pool = self.env['stock.picking']        
        return picking_pool.workflow_ordered_ready()

    # DDT Unload phase:
    @api.multi
    def generate_delivery(self):
        ''' F. Generate delivery order in draft mode
        '''
        order_pool = self.env['sale.order']
        return order_pool.workflow_ready_to_done_draft_picking()

    @api.multi
    def confirm_delivery(self):
        ''' F. Generate delivery order in draft mode
        '''
        picking_pool = self.env['stock.picking']        
        return picking_pool.workflow_ready_to_done_all_done_picking()

    @api.multi
    def closed_delivered(self):
        ''' G. Close delivery order
        '''
        return True
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
