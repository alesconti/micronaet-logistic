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
    
    # -------------------------------------------------------------------------
    #                                   BUTTON:
    # -------------------------------------------------------------------------
    @api.multi
    def add_product_in_pool(self):
        ''' Add selected product in pool
        '''
        product = self.product_id
        if not product:
            return True
        
        # Update product with this pool reference:
        product.similar_id = self.id

        # Clean product selection in pool:
        self.product_id = False

        #view_id = model_pool.get_object_reference(
        #    'module_name', 'view_name')[1]
        target = self.env.context.get('open_mode', 'current')
        return {
            'type': 'ir.actions.act_window',
            'name': _('Pool management'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': self.id,
            'res_model': 'product.template.pool.similar',
            #'view_id': view_id, # False
            'views': [(False, 'form')], #, (False, 'tree')
            'domain': [],
            'context': self.env.context,
            'target': target,
            'nodestroy': False,
            }

    # -------------------------------------------------------------------------
    #                             FUNCTION FIELD:
    # -------------------------------------------------------------------------
    @api.multi
    def _get_product_pool_text(self):
        ''' Better list of product for tree view
        '''
        for pool in self:
            res = []
            for similar in sorted(pool.similar_ids, 
                    key=lambda x: x.name):
                res.append(similar.default_code)
            pool.pool_text = ', '.join(res)

    # -------------------------------------------------------------------------
    #                                   COLUMNS:
    # -------------------------------------------------------------------------
    product_id = fields.Many2one('product.template', 'Add similar')
    pool_text = fields.Text(
        'Similar product', compute='_get_product_pool_text', store=False)
    note = fields.Text('Note')

class ProductTemplate(models.Model):
    """ Model name: ProductTemplate
    """
    
    _inherit = 'product.template'
    
    # -------------------------------------------------------------------------
    #                                   COLUMNS:
    # -------------------------------------------------------------------------
    similar_id = fields.Many2one(
        'product.template.pool.similar', 'Similar', ondelete='set null')
    
class ProductTemplatePoolSimilar(models.Model):
    """ Model name: ProductTemplatePoolSimilar
    """
    
    _inherit = 'product.template.pool.similar'

    # -------------------------------------------------------------------------
    #                                   COLUMNS:
    # -------------------------------------------------------------------------    
    similar_ids = fields.One2many('product.template', 'similar_id', 'Pool')
    #similar_ids = fields.Many2many('product.template', string='Similar')

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
        similar_pool = self.env['product.template.pool.similar']
        model_pool = self.env['ir.model.data']
        
        if self.similar_id:
            similar_id = self.similar_id.id
        else:
            # Create new pool and attach this product
            similar = similar_pool.create({
                'similar_ids': [(6, 0, (self.id, ))],
                })
            similar_id = similar.id
        #self.similar_id = similar.id
            
        #view_id = model_pool.get_object_reference(
        #    'module_name', 'view_name')[1]
        return {
            'type': 'ir.actions.act_window',
            'name': _('New similar pool'),
            'view_type': 'form',
            'view_mode': 'form', # tree
            'res_id': similar_id,
            'res_model': 'product.template.pool.similar',
            #'view_id': view_id, # False
            'views': [(False, 'form')], #, (False, 'tree')
            'domain': [],
            'context': self.env.context,
            'target': 'new',
            'nodestroy': False,
            }
            
    @api.multi
    def unlink_similar_pool(self):
        ''' Unlink from the pool, delete also pool if is the last
        '''
        similar = self.similar_id
        # Delete pool if only 1 or 2 record (no similar product)
        if len(similar.similar_ids) in (1, 2): 
            similar.unlink()
        else:    
            self.similar_id = False
        
        return True
        
    # -------------------------------------------------------------------------
    #                          Related fields function
    # -------------------------------------------------------------------------
    # Only in form mode (not depends):
    @api.one
    def _compute_product_template_similar_ids(self):
        ''' Return pool of product present in similar pool:
            It's a related field but maybe modified in the future
        '''
        res = []
        for similar in sorted(self.similar_id.similar_ids, 
                key=lambda x: x.name):
            if similar != self:
                res.append(similar.id)
        self.similar_ids = res        
    
    # -------------------------------------------------------------------------
    #                                   COLUMNS:
    # -------------------------------------------------------------------------
    similar_ids = fields.One2many(
        'product.template', 
        compute='_compute_product_template_similar_ids',
        #related='similar_id.similar_ids',
        string='Similar pool')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: