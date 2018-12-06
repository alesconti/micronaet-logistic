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

class SaleOrder(models.Model):
    """ Model name: Sale Order
    """
    
    _inherit = 'sale.order'

    # -------------------------------------------------------------------------
    #                            Button event:
    # -------------------------------------------------------------------------
    @api.multi
    def explode_kit_in_order_line(self):
        ''' Explode kit in order line
        '''
        product_pool = self.env['product.product']
        line_pool = self.env['sale.order.line']
        delete_line = []
        component_new = {} # Creation after read data
        for line in self.order_line:
            # Component line will be deleted (after):
            if line.kit_line_id:
                delete_line.append(line)
                continue

            # Not kit line jumped:
            if not line.is_kit:
                continue
            
            # Save data for creation:    
            component_new[line] = line.product_id

        # Post: Delete line of component:
        for line in delete_line:
            line.unlink()    
        
        # Post: Create Extra line for kit
        order_id = self.id
        for line in component_new:
            product = component_new[line]
            product_qty = line.product_uom_qty
            
            for bom in product.component_ids:                
                template_id = bom.component_id.id
                product_ids = product_pool.search([
                    ('product_tmpl_id', '=', template_id)])
                product_id = product_ids[0].id
                line_pool.create({
                    'order_id': order_id,
                    'product_id': product_id,
                    'product_uom_qty': product_qty * bom.product_qty,
                    'price_unit': 0.0, # TODO used price?
                    'tax_id': False, # No Tax (not used in delivery)                    
                    'kit_line_id': line.id, # back reference to kit line        
                    })
        return True            

class SaleOrderLine(models.Model):
    """ Model name: Sale Order Line
    """
    
    _inherit = 'sale.order.line'

    # -------------------------------------------------------------------------
    #                                COLUMNS: 
    # -------------------------------------------------------------------------
    kit_line_id = fields.Many2one('sale.order.line', 'Kit line', 
        ondelete='cascade')
    kit_product_id = fields.Many2one('product.product', 'Kit reference', 
        related='kit_line_id.product_id', readonly=True)
        
    is_kit = fields.Boolean('Is kit', related='product_id.is_kit', 
        readonly=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
