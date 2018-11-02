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
    @api.multi
    def confirm_payment(self):
        ''' A. Confirm draft order if payment is secure
        '''
        order_pool = self.env['sale.order']
        
        secure_order = order_pool.check_secure_payment_draft_order()
        tree_view_id = form_view_id = False
        selected_order = [order.id for order in secure_order]
        return {
            'type': 'ir.actions.act_window',
            'name': _('Order confirmed'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            #'res_id': 1,
            'res_model': 'sale.order',
            'view_id': tree_view_id,
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'domain': [('id', 'in', selected_order)],
            'context': self.env.context,
            'target': 'current', # 'new'
            'nodestroy': False,
            }

    @api.multi
    def confirm_order(self):
        ''' B. Confirm quotation in order (explode kit)
        '''
        order_pool = self.env['sale.order']
        
        # Call procedure:
        orders = order_pool.search([
            ('logistic_state', '=', 'payment'),
            ])
        for order in orders:    
            order.explode_kit_in_order_line()
            order.logistic_state = 'order'

        # ---------------------------------------------------------------------
        # Return view:
        # ---------------------------------------------------------------------
        #model_pool = self.env['ir.model.data']
        #tree_view_id = model_pool.get_object_reference(
        #    'logistic_management', 'view_sale_order_line_logistic_tree')[1]
        #form_view_id = model_pool.get_object_reference(
        #    'logistic_management', 'view_sale_order_line_logistic_form')[1]
        tree_view_id = False
        form_view_id = False
        selected_order = [order.id for order in orders]
        return {
            'type': 'ir.actions.act_window',
            'name': _('Order confirmed'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            #'res_id': 1,
            'res_model': 'sale.order',
            'view_id': tree_view_id,
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'domain': [('id', 'in', selected_order)],
            'context': self.env.context,
            'target': 'current', # 'new'
            'nodestroy': False,
            }

    @api.multi
    def assign_stock(self):
        ''' C. Assign stock product to open orders
        '''
        line_pool = self.env['sale.order.line']
        
        # Call assign stock procedure:
        return line_pool.logistic_assign_stock_to_customer_order()       
        
    @api.multi
    def generate_purchase(self):
        ''' D. Generate purchase order for not cover qty
        '''
        line_pool = self.env['sale.order.line']

        # Call purchase order generator procedure:        
        return line_pool.logistic_order_uncovered_supplier_order()
        
    @api.multi
    def update_ready(self):
        ''' E. Update order ready with stock or load
        '''
        return True

    @api.multi
    def generate_delivery(self):
        ''' F. Generate delivery order in draft mode
        '''
        return True

    @api.multi
    def closed_delivered(self):
        ''' G. Close delivery order
        '''
        return True
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
