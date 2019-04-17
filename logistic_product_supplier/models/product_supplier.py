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

class ProductTemplateSupplierStock(models.Model):
    """ Model name: ProductTemplateSupplierStock
    """
    
    _name = 'product.template.supplier.stock'
    _description = 'Supplier stock'
    _rec_name = 'supplier_id'
    _order = 'supplier_id'
    
    # -------------------------------------------------------------------------
    #                                   COLUMNS:
    # -------------------------------------------------------------------------    
    product_id = fields.Many2one(
        'product.template', 'Product', index=True, ondelete='cascade',
        )
    supplier_id = fields.Many2one(
        'res.partner', 'Partner', index=True, ondelete='cascade',
        domain="[('supplier', '=', True)]",
        )
    stock_qty = fields.Float(
        'Quantity', required=True, default=1.0,
        digits=dp.get_precision('Product Unit of Measure'))
    quotation = fields.Float(
        'Price', digits=dp.get_precision('Product Unit of Measure'))
    best_price = fields.Boolean('Best price')    
    ipcode = fields.Char('Supplier code', size=24)

class ProductTemplate(models.Model):
    """ Model name: ProductTemplate
    """
    
    _inherit = 'product.template'
    
    # -------------------------------------------------------------------------
    #                                   COLUMNS:
    # -------------------------------------------------------------------------
    supplier_stock_ids = fields.One2many(
        'product.template.supplier.stock', 'product_id', 'Supplier stock')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
