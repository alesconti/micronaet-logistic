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

class ProductTemplateKitBom(models.Model):
    """ Model name: ProductTemplateKitBom
    """
    
    _name = 'product.template.kit.bom'
    _description = 'Kit BOM'
    _rec_name = 'product_id'
    _order = 'sequence'
    
    # -------------------------------------------------------------------------
    #                                   COLUMNS:
    # -------------------------------------------------------------------------
    sequence = fields.Integer(
        'Sequence', default=10)
    product_id = fields.Many2one(
        'product.template', 'Product', index=True, 
        #ondelete='cascade', # TODO correct
        )
    component_id = fields.Many2one(
        'product.template', 'Component', index=True, 
        domain=[('is_kit', '=', False)], required=True,
        #ondelete='set null', # TODO correct?
        )
    product_qty = fields.Float(
        'Quantity', required=True, default=1.0,
        digits=dp.get_precision('Product Unit of Measure'))
    uom_id = fields.Many2one(
        'product.uom', 'Unit of Measure', readonly=True, 
        related='component_id.uom_id')
    product_type = fields.Selection(
        string='Type', related='component_id.type', readonly=True)
    

class ProductTemplate(models.Model):
    """ Model name: ProductTemplate
    """
    
    _inherit = 'product.template'
    
    # -------------------------------------------------------------------------
    #                                   COLUMNS:
    # -------------------------------------------------------------------------
    is_kit = fields.Boolean('Is Kit')
    component_ids = fields.One2many(
        'product.template.kit.bom', 'product_id', 'Kit Component')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
