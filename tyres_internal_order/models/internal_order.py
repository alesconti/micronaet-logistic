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
import odoo
import shutil
from odoo import api, fields, models, tools, exceptions, SUPERUSER_ID
from odoo.addons import decimal_precision as dp
from odoo.tools.translate import _

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


_logger = logging.getLogger(__name__)

class SaleOrderInternal(models.Model):
    """ Model name: Internal sale order
    """
    
    _name = 'sale.order.internal'
    _rec_name = 'date'
    _order = 'date desc'

    @api.multi
    def confirm_internal_order(self):
        ''' Create Sale order
            Create purchase order from sale order
        '''
        sale_pool = self.env['sale.order']
        line_pool = self.env['sale.order.line']
        purchase_pool = self.env['sale.order.line.purchase']
        
        # ---------------------------------------------------------------------
        # Search company partner:
        # ---------------------------------------------------------------------
        partner_id = self.env.user.company_id.partner_id.id
                
        # ---------------------------------------------------------------------
        # Create sale order header:
        # ---------------------------------------------------------------------
        order = sale_pool.create({
            'partner_id': partner_id,
            'partner_invoice_id': partner_id,
            'partner_shipping_id': partner_id,
            'date_order': self.date,
            'validity_date': self.date,
            'note': _('Ordine interno'),
            'team_id': False,
            
            'logistic_source': 'internal',
            'logistic_state': 'order',
            })
        order_id = order.id

        # ---------------------------------------------------------------------
        # Create sale order line:
        # ---------------------------------------------------------------------
        for line in self.line_ids:
            # Create line:
            line_id = line_pool.create({
                'order_id': order_id,
                'product_id': line.product_id.id,
                'product_uom_qty': line.product_uom_qty,
                'price_unit': line.price_unit,
                }).id

            # -----------------------------------------------------------------
            # Link sale order line to supplier:
            # -----------------------------------------------------------------
            purchase_pool.create({
                'line_id': line_id,
                'supplier_id': line.supplier_id.id,
                'product_uom_qty': line.product_uom_qty,
                'purchase_price': line.price_unit,                
                })

        # ---------------------------------------------------------------------
        # Create purchase order and confirm:
        # ---------------------------------------------------------------------
        order.workflow_manual_order_pending()        
        self.confirmed = True
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Internal order'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': order_id,
            'res_model': 'sale.order',
            'view_id': False,#view_id, # False
            'views': [(False, 'form'), (False, 'tree')],
            'domain': [],
            'context': self.env.context,
            'target': 'current', # 'new'
            'nodestroy': False,
            }

    # -------------------------------------------------------------------------    
    # Columns:
    # -------------------------------------------------------------------------    
    date = fields.Date('Date', default=fields.Date.context_today)
    note = fields.Text('Note')
    confirmed = fields.Boolean('Confirmed')
    
class SaleOrderLineInternal(models.Model):
    """ Model name: Internal sale order line
    """
    
    _name = 'sale.order.line.internal'

    @api.onchange('product_id', 'supplier_id')
    def onchange_product_supplier(self, ):
        ''' Find price
        '''
        product = self.product_id
        supplier = self.supplier_id
        
        if product and supplier:
            for price in product.supplier_stock_ids:
                if price.supplier_id == supplier:
                    self.price_unit = price.quotation
                    return
                    
    # -------------------------------------------------------------------------    
    # Columns:
    # -------------------------------------------------------------------------    
    order_id = fields.Many2one('sale.order.internal', 'Order')
    product_id = fields.Many2one('product.product', 'Product', required=True)
    supplier_id = fields.Many2one('res.partner', 'Supplier', required=True, 
        domain="[('supplier', '=', True), ('hide_supplier', '=', False)]")
    product_uom_qty = fields.Float(
        string='Quantity', digits=dp.get_precision('Product Unit of Measure'), 
        required=True, default=1.0)
    price_unit = fields.Float(
        'Unit Price', digits=dp.get_precision('Product Price'), required=True)

class SaleOrderInternal(models.Model):
    """ Model name: Internal sale order
    """
    
    _inherit = 'sale.order.internal'

    # -------------------------------------------------------------------------    
    # Columns:
    # -------------------------------------------------------------------------    
    line_ids = fields.One2many(
        'sale.order.line.internal', 'order_id', 'Detail')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
