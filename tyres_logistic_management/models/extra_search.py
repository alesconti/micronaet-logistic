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
import odoo
import logging
from odoo import models, fields, api
from odoo.tools.translate import _


_logger = logging.getLogger(__name__)

class SaleOrderExtra(models.Model):
    """ Model name: Sale order extra search
    """
    
    _inherit = 'sale.order'

    # -------------------------------------------------------------------------
    # Compute Search fields:
    # -------------------------------------------------------------------------
    @api.multi
    def _extra_search_product(self, operator, value):
        ''' Search product SKU in order header
        '''
        import pdb; pdb.set_trace()
        line_pool = self.env['sale.order.line']
        line_ids = line_pool.search([
            ('product_id.default_code', 'ilike', value),
            ])
        if line_ids:
            order_ids = { # Set of order
                line.order_id.id for line in line_pool.browse(line_ids)
                }
        return [('id', 'in', order_ids)]
        
    # -------------------------------------------------------------------------
    # Columns:
    # -------------------------------------------------------------------------
    search_product = fields.Many2one(
        'product.product', 'Extra Search product', 
        search='_extra_search_product')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
