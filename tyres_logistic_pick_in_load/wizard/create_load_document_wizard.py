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
import shutil
from odoo import api, fields, models, tools, exceptions, SUPERUSER_ID
from odoo.addons import decimal_precision as dp
from odoo.tools.translate import _


_logger = logging.getLogger(__name__)

class PickingLoadDocumentGeneratorWizard(models.TransientModel):
    """ Model name: Wizard for create documents for load
    """
    
    _name = 'picking.load.document.generator.wizard'
    _description = 'Create delivery document'

    @api.multi
    def generate_delivery_orders_from_line(self):
        ''' Create the list of all order received splitted for supplier        
        '''

        line_pool = self.env['purchase.order.line']
        delivery_pool = self.env['stock.picking.delivery']

        # ---------------------------------------------------------------------
        # Search selection line for this user:
        # ---------------------------------------------------------------------
        active_ids = self.env.context.get('active_ids')
        if not active_ids:
            raise UserError(_('Select before launch the wizard!'))
        lines = line_pool.browse(active_ids)
        
        # ---------------------------------------------------------------------
        # Extract supplier line list:
        # ---------------------------------------------------------------------
        suppliers = {} # TODO also with carrier?
        for line in lines:
            supplier = line.order_id.partner_id
            if supplier not in suppliers:
                suppliers[supplier] = []
            suppliers[supplier].append(line)            
        
        # ---------------------------------------------------------------------
        # Create purchase order:
        # ---------------------------------------------------------------------
        delivery_ids = []
        for supplier in suppliers:
            # -----------------------------------------------------------------
            # Create header:
            # -----------------------------------------------------------------
            delivery_id = delivery_pool.create({
                'supplier_id': supplier.id,
                #'carrier_id': carrier.id,
                #'create_uid': self.env.uid,                
                }).id
            delivery_ids.append(delivery_id)
            for line in suppliers[supplier]: # TODO better
                line.delivery_id = delivery_id # Link to delivery order!
                
        # ---------------------------------------------------------------------
        # Return created order:
        # ---------------------------------------------------------------------
        tree_view_id = form_view_id = False
        if len(delivery_ids) == 1:
            res_id = delivery_ids[0]
            views = [(tree_view_id, 'form'), (tree_view_id, 'tree')]
        else:
            res_id = False    
            views = [(tree_view_id, 'tree'), (tree_view_id, 'form')]
            
        return {
            'type': 'ir.actions.act_window',
            'name': _('Delivery created:'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_id': res_id,
            'res_model': 'stock.picking.delivery',
            'view_id': tree_view_id,
            #'search_view_id': search_view_id,
            'views': views,
            'domain': [('id', 'in', delivery_ids)],
            'context': self.env.context,
            'target': 'current', # 'new'
            'nodestroy': False,
            }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
