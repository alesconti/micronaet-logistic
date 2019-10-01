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
from odoo import fields, api, models
from odoo import tools
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    ''' Sale order line update model
    '''
    _inherit = 'sale.order.line'

    # -------------------------------------------------------------------------
    # Columns:
    # -------------------------------------------------------------------------
    unification_origin_id = fields.Many2one(
        'sale.order', 'Origin order', help='Order line comes from this order')

class SaleOrder(models.Model):
    ''' Sale order update model
    '''
    _inherit = 'sale.order'

    """@api.multi
    def check_unificable_order(self):
        ''' Check if there's order with unificable characteristic
        '''
        self.ensure_one()
        
        return """
    
    @api.multi
    def migrate_to_destination_button(self):
        ''' Migrate button:
        '''
        self.ensure_one()
        line_pool = self.env['sale.order.line']
        
        # Read linked destination (written before):
        destination_id = self.order_destination_id.id
        origin_id = self.id
        
        # Move line and keep origin reference:
        lines = line_pool.search([
            ('order_id', '=', origin_id)])
            
        lines.write({
            'order_id': destination_id, # Change parent header
            'unification_origin_id': origin_id,            
            })    
        return True
        
    # -------------------------------------------------------------------------
    # Columns:
    # -------------------------------------------------------------------------
    order_destination_id = fields.Many2one(
        'sale.order', 'Destination', help='Destination order for unification')
    unificated_order_ids = fields.One2many(
        'sale.order', 'order_destination_id', 'Unificated order', 
        help='List of order unificated here')
    unificated_line_ids = fields.One2many(
        'sale.order.line', 'unification_origin_id', 'Unificated line', 
        help='List of unificared line previous in order')
    
    #unificable_order_ids = fields.Many2many('Unificable orders', )    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
