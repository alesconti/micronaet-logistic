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
from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.addons import decimal_precision as dp
from odoo.tools.translate import _


_logger = logging.getLogger(__name__)

class ProductTemplatePoolSimilar(models.Model):
    """ Model name: ProductTemplatePoolSimilar
    """
    
    _name = 'product.template.pool.similar'
    _description = 'Pool of similar product'
    _rec_name = 'id'
    _order = 'id'
    
    # XXX Has only pool of product

class ProductTemplate(models.Model):
    """ Model name: ProductTemplate
    """
    
    _inherit = 'product.template'
    
    # -------------------------------------------------------------------------
    #                                   COLUMNS:
    # -------------------------------------------------------------------------
    similar_id = fields.Many2one('product.template.pool.similar', 'Similar')
    
class ProductTemplatePoolSimilar(models.Model):
    """ Model name: ProductTemplatePoolSimilar
    """
    
    _inherit = 'product.template.pool.similar'

    # -------------------------------------------------------------------------
    #                                   COLUMNS:
    # -------------------------------------------------------------------------    
    pool_ids = fields.One2many('product.template', 'similar_id', 'Pool')

class ProductTemplate(models.Model):
    """ Model name: ProductTemplate
    """
    
    _inherit = 'product.template'

    # -------------------------------------------------------------------------
    #                            Button event:
    # -------------------------------------------------------------------------
    @api.multi
    def create_similar_pool(self):
        ''' Create a new pool of similar product, start adding this product
            in it
        '''
        return True
        
    # -------------------------------------------------------------------------
    #                          Related fields function
    # -------------------------------------------------------------------------
    @api.one
    def _compute_pricelist_ids(self):
        ''' Return pool of product present in similar pool:
            It's a related field but maybe modified in the future
        '''
        self.pool_ids = []
        for similar in sorted(self.similar_id.pool_ids, 
                key=lambda x: x.default_code):
            if similar != self:
                self.pool_ids.append(similar)
    
    # -------------------------------------------------------------------------
    #                                   COLUMNS:
    # -------------------------------------------------------------------------
    similar_ids = fields.One2many(
        'product.template', compute='_compute_product_template_similar_ids', 
        string='Default Pricelist')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
