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
    _order = 'quotation'

    @api.model
    def get_context_sale_order_id(self):
        ''' Return browseable sale line reference:
        '''
        line_pool = self.env['sale.order.line']
        context = self.env.context
        sale_order_id = context.get('sale_order_id')
        return line_pool.browse(sale_order_id)
            
    @api.multi
    def assign_to_purchase_minus(self):
        ''' Assign -1 to this supplier
        '''
        line = self.get_context_sale_order_id()
        return True

    @api.multi
    def assign_to_purchase_plus(self):
        ''' Assign +1 to this supplier
        '''
        line = self.get_context_sale_order_id()
        return True

    @api.multi
    def assign_to_purchase_all(self):
        ''' Assign all order to this supplier
        '''
        import pdb; pdb.set_trace()
        line = self.get_context_sale_order_id()
        product_uom_qty = line.product_uom_qty
        supplier_id = self.supplier_id.id
        
        # Remove all splitted line except this:
        for splitted in line.splitted_child_ids:
            if splitted != self:
                splitted.unlink()

        # Assign all quantity to this line:
        line.splitted_parent_id = self.id
        line.supplier_id = supplier_id
        line.purchase_price = self.quotation
        line.splitted = False # All line for this supplier!
        
        # TODO update line status and order status
        return True

    @api.multi
    def assign_to_purchase_none(self):
        ''' Remove this supplier
        '''
        line = self.get_context_sale_order_id()
        return True

    @api.multi
    def assign_to_purchase_this(self):
        ''' Assign max stock from this supplier
        '''
        line = self.get_context_sale_order_id()
        return True

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
        'Price', digits=dp.get_precision('Product Price'))
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

class SaleOrderLine(models.Model):
    """ Model name: Sale order line
    """
    
    _inherit = 'sale.order.line'
    
    @api.multi
    def clean_all_purchase_selected(self):
        ''' Clean all selected elements
        '''
        import pdb; pdb.set_trace()
        for splitted in self.splitted_child_ids:
            if splitted != self:
                splitted.unlink()
        
        # Reset information:
        self.splitted = False
        self.supplier_id = False
        self.purchase_price = 0.0        
        return True

    # -------------------------------------------------------------------------
    #                                   COLUMNS:
    # -------------------------------------------------------------------------
    splitted = fields.Boolean('Splitted')
    splitted_parent_id = fields.Many2one(
        'sale.order.line', 'Purchase', 
        help='Splitted reference for purchase')

    # Purchase reference:
    purchase_price = fields.Float(
        'Purchase Price', digits=dp.get_precision('Product Price'))
    supplier_id = fields.Many2one(
        'res.partner', 'Partner', index=True, ondelete='cascade',
        domain="[('supplier', '=', True)]",
        )
    
    # TODO field for state of purchase 
    # TODO field for purchase supplier present    
        

class SaleOrderLine(models.Model):
    """ Model name: Sale order line relations
    """
    
    _inherit = 'sale.order.line'

    @api.multi
    def _get_product_supplier_stock_info(self):
        ''' List of product supplier available
        '''
        self.ensure_one()
        res = [
            item.id for item in self.product_id.supplier_stock_ids]
        self.product_supplier_ids = res

    # -------------------------------------------------------------------------
    #                                   COLUMNS:
    # -------------------------------------------------------------------------
    splitted_child_ids = fields.One2many(
        'sale.order.line', 'splitted_parent_id', 'Splitted child',
        help='List of splitted child')
    product_supplier_ids = fields.Many2many(
        'product.template.supplier.stock', 
        compute='_get_product_supplier_stock_info', 
        string='Supplier info', store=False,
        column1='line_id', column2='stock_id')
    

class SaleOrder(models.Model):
    """ Model name: Sale order line relations
    """
    
    _inherit = 'sale.order'
    
    @api.multi
    def purchase_management_button(self):
        ''' Open view for purchase management
        '''
        
        model_pool = self.env['ir.model.data']
        tree_view_id = model_pool.get_object_reference(
            'logistic_product_supplier', 
            'view_sale_order_line_purchase_management_tree')[1]
        form_view_id = model_pool.get_object_reference(
            'logistic_product_supplier', 
            'view_sale_order_line_purchase_management_form')[1]

        line_ids = [item.id for item in self.order_line \
            if not item.splitted]
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Purchase line management'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            #'res_id': 1,
            'res_model': 'sale.order.line',
            'view_id': tree_view_id,
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'domain': [('id', 'in', line_ids)],
            'context': self.env.context,
            'target': 'current', # 'new'
            'nodestroy': False,
            }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
