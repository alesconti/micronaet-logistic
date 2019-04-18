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
from odoo import exceptions 


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
        # Selected sale line:
        stock = self
        line = self.get_context_sale_order_id()
        supplier_id = self.supplier_id.id
        product_uom_qty = line.product_uom_qty
        stock_qty = stock.stock_qty 
        if stock_qty >= product_uom_qty:
            used_qty = product_uom_qty
        else:
            used_qty = stock_qty
            # TODO create row with partial load:

            # If previously all saved:
            #line.clean_auto_splitted_reference()
            #line.splitted = True
            
            # Create partial load
            #self.create({
            #    'splitted_parent_id': line.id,
            #    'splitted': False,
            #    'purchase_price': stock.quotation,
            #    'supplier_id': stock.supplier_id.id,
            #    'product_uom_qty': stock_qty
            #    })
            

        # Remove all splitted line except this:
        for splitted in line.splitted_child_ids:
            if splitted != line: # Remove all splitted (without current line)
                splitted.unlink()

        # Create assigned for purchase:
        line.splitted_parent_id = line.id
        line.supplier_id = supplier_id
        line.purchase_price = self.quotation
        line.splitted = False # All line for this supplier!
        # XXX quantity was yet correct

        # TODO update line status and order status
        return True

    @api.multi
    def assign_to_purchase_none(self):
        ''' Remove this supplier
        '''
        stock = self # Readability:
        
        # Selected sale line:
        line = stock.get_context_sale_order_id()

        # Remove all splitted line except this:
        for splitted in line.splitted_child_ids:
            if stock.supplier_id == splitted.supplier_id:              
                if splitted == line: # Clean
                    line.clean_auto_splitted_reference()
                else: # Remove
                    splitted.unlink()

        # TODO update line status and order status
        return True

    @api.multi
    def assign_to_purchase_this(self):
        ''' Assign max stock from this supplier (or remain)
        '''
        stock = self # Readability:
        
        # Selected sale line:
        line = stock.get_context_sale_order_id()

        product_uom_qty = line.product_uom_qty
        stock_qty = stock.stock_qty

        # Remove all splitted line except this:
        selected_purchase = False
        current_total = 0.0        
        for splitted in line.splitted_child_ids:            
            if stock.supplier_id == splitted.supplier_id:
                selected_purchase = splitted
            else:
                current_total += splitted.product_uom_qty
        uncovered_qty = product_uom_qty - current_total
        if stock_qty >= uncovered_qty:
            select_qty = uncovered_qty
        else:
            select_qty = stock_qty
        
        if selected_purchase: # found
            if splitted == line:
                
        
        else:    
            # If previously all saved:
            line.clean_auto_splitted_reference()
            line.splitted = True
            # Create partial load
            self.create({
                'splitted_parent_id': line.id,
                'splitted': False,
                'purchase_price': stock.quotation,
                'supplier_id': stock.supplier_id.id,
                'product_uom_qty': stock_qty
                })

        # TODO update line status and order status
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
    
    @api.model
    def clean_auto_splitted_reference(self):
        ''' Clean reference for splitted himself
        '''
        self.splitted = False
        self.supplier_id = False
        self.purchase_price = 0.0        
        self.splitted_parent_id = False
    
    @api.multi
    def clean_all_purchase_selected(self):
        ''' Clean all selected elements
        '''
        for splitted in self.splitted_child_ids:
            if splitted != self:
                splitted.unlink()
        
        # Update information:
        self.clean_auto_splitted_reference()
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

    # -------------------------------------------------------------------------
    #                                   COLUMNS:
    # -------------------------------------------------------------------------
    splitted_child_ids = fields.One2many(
        'sale.order.line', 'splitted_parent_id', 'Splitted child',
        help='List of splitted child')
    product_supplier_ids = fields.One2many(
        'product.template.supplier.stock', 
        related='product_id.supplier_stock_ids',
        )
    

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
