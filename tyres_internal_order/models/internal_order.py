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
        return 

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
        'Unit Price', digits=dp.get_precision('Product Price'))

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
