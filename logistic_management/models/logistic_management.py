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

class ResCompany(models.Model):
    """ Model name: Res Company
    """
    
    _inherit = 'res.company'

    # -------------------------------------------------------------------------
    #                                   COLUMNS:
    # -------------------------------------------------------------------------
    # Logistic parameters:
    logistic_assign_mode = fields.Selection([
        ('first_available', 'First available'),
        #('better_available', 'Better available'),
        ], 'Assign stock mode', default='first_available', 
        help='Assign stock mode to order line (first avilable or better)',
        required=True,
        )
    logistic_order_sort = fields.Selection([
        ('create_date', 'Create date'),
        ('validity_date', 'Validity date'),
        ], 'Order sort', default='create_date', 
        help='Sort order to assign stock availability',
        required=True,
        )
    logistic_location_id = fields.Many2one(
        'stock.location', 'Stock Location IN', 
        help='Stock location for q. created',
        required=True,
        )
    logistic_pick_in_type_id = fields.Many2one(
        'stock.picking.type', 'Pick in type', 
        help='Picking in type for load documents',
        required=True,
        )
        

class PurchaseOrder(models.Model):
    """ Model name: Sale Order
    """
    
    _inherit = 'purchase.order'

    @api.model
    def purchase_pool.return_purchase_order_list_view(purchase_ids):
        ''' Return purchase order tree from ids
        '''
        model_pool = self.env['ir.model.data']
        tree_view_id = form_view_id = False
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Purchase order created:'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            #'res_id': 1,
            'res_model': 'purchase.order',
            'view_id': tree_view_id,
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'domain': [('id', 'in', purchase_ids)],
            'context': self.env.context,
            'target': 'current',
            'nodestroy': False,
            }

    logistic_state = fields.Selection([
        ('draft', 'Order draft'), # Draft purchase
        ('confirmed', 'Confirmed'), # Purchase confirmed
        ('done', 'Done'), # All loaded in stock
        ], 'Logistic state', default='draft',
        )

class PurchaseOrderLine(models.Model):
    """ Model name: Purchase Order Line
    """
    
    _inherit = 'purchase.order.line'
    
    # -------------------------------------------------------------------------
    #                                   COLUMNS:
    # -------------------------------------------------------------------------
    # RELATIONAL FIELDS:
    logistic_sale_id = fields.Many2one(
        'sale.order.line', 'Link to generator', 
        help='Link generator sale order line: one customer line=one purchase',
        index=True, ondelete='set null',
        )

class StockMoveIn(models.Model):
    """ Model name: Stock Move
    """
    
    _inherit = 'stock.move'
    
    # -------------------------------------------------------------------------
    #                                   COLUMNS:
    # -------------------------------------------------------------------------
    # TODO Need index?
    # USED STOCK: Linked used
    # Moved in stock.quant:
    #logistic_assigned_id = fields.Many2one(
    #    'sale.order.line', 'Link covered to generator', 
    #    help='Link to sale line the assigned qty', 
    #    index=True, ondelete='cascade', # remove stock move when delete order
    #    )

    # Direct link to sale order line (generated from purchase order):    
    logistic_load_id = fields.Many2one(
        'sale.order.line', 'Link load to sale', 
        help='Link pick in line to original sale line (bypass purchase)',
        index=True, ondelete='set null',
        )
    
    # DELIVER: Pick out
    logistic_unload_id = fields.Many2one(
        'sale.order.line', 'Link unload to sale', 
        help='Link pick out line to sale order',
        index=True, ondelete='set null',
        )

    # SUPPLIER ORDER: Purchase management:
    logistic_purchase_id = fields.Many2one(
        'purchase.order.line', 'Link load to purchase',
        help='Link pick in line to generat purchase line',
        index=True, ondelete='set null',
        )

class PurchaseOrderLine(models.Model):
    """ Model name: Purchase Order Line
    """
    
    _inherit = 'purchase.order.line'
    
    # -------------------------------------------------------------------------
    # Function fields:
    # -------------------------------------------------------------------------
    @api.multi
    @api.depends('load_line_ids')
    def _get_logist_status_field(self):
        ''' Manage all data for logistic situation in sale order:
        '''
        _logger.warning('Update logistic qty fields now')
        for line in self:
            logistic_delivered_qty = 0.0
            for move in line.load_line_ids:
                logistic_delivered_qty += move.product_uom_qty
            # Generate data for fields::
            line.logistic_delivered_qty = logistic_delivered_qty
            line.logistic_undelivered_qty = \
                line.product_qty - logistic_delivered_qty

    # -------------------------------------------------------------------------
    #                                   COLUMNS:
    # -------------------------------------------------------------------------
    # COMPUTED:
    logistic_delivered_qty = fields.Float(
        'Delivered qty', digits=dp.get_precision('Product Price'),
        help='Qty delivered with load documents',
        readonly=True, compute='_get_logist_status_field', multi=True,
        store=False,
        )
    logistic_undelivered_qty = fields.Float(
        'Undelivered qty', digits=dp.get_precision('Product Price'),
        help='Qty undelivered, remain to load',
        readonly=True, compute='_get_logist_status_field', multi=True,
        store=False,
        )

    # RELATIONAL:
    load_line_ids = fields.One2many(
        'stock.move', 'logistic_purchase_id', 'Linked load to purchase', 
        help='Load linked to this purchase line',
        )

class StockQuant(models.Model):
    """ Model name: Stock quant
    """
    
    _inherit = 'stock.quant'
    
    # -------------------------------------------------------------------------
    #                                   COLUMNS:
    # -------------------------------------------------------------------------
    logistic_assigned_id = fields.Many2one(
        'sale.order.line', 'Link covered to generator', 
        help='Link to sale line the assigned qty', 
        index=True, ondelete='cascade', # remove stock move when delete order
        )
    
class SaleOrder(models.Model):
    """ Model name: Sale Order
    """
    
    _inherit = 'sale.order'

    # -------------------------------------------------------------------------
    #                   UTILITY: Extra operation before WF
    # -------------------------------------------------------------------------
    @api.model
    def return_order_view(self):
        ''' Utility for return selected order in tree view
        '''
        tree_view_id = form_view_id = False
        selected_ids = [order.id for order in self]
        return {
            'type': 'ir.actions.act_window',
            'name': _('Order confirmed'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            #'res_id': 1,
            'res_model': 'sale.order',
            'view_id': tree_view_id,
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'domain': [('id', 'in', selected_ids)],
            'context': self.env.context,
            'target': 'current', # 'new'
            'nodestroy': False,
            }
            
    @api.model
    def check_exploded_product_kit(self):
        ''' Check if there's kit in product, launch explode operation
        '''
        log_message = True # TODO change
        line_pool = self.env['sale.order.line']
        template_pool = self.env['product.template']
        
        lines = line_pool.search([
            ('order_id.logistic_state', '=', 'draft'), # Draft order
            ('product_id.default_code', '=ilike', '%#%'), # Kit code
            # TODO replace with: ('is__kit', '=', True),
            ])
        template_ids = [] # ID of template checked
        update_ids = [] # ID of template updated
        for line in lines:
            template = line.product_id.product_tmpl_id
            if template.id in template_ids:
                continue
            template_ids.append(template.id)
            
            code_part = template.default_code.split('#')
            if len(code_part) != len(template.component_ids):
                try:
                    update_ids.append(template.id)
                    template.explode_kit_from_name()
                except:
                    pass    
         
        # Reload product updated:
        templates = template_pool.search([
            ('id', 'in', update_ids), # Updated kit
            ])
        res = ''    
        for template in templates:
            code_part = template.default_code.split('#')
            if len(code_part) != len(template.component_ids):
                res += '%s<br/>' % template.default_code
                
        if log_message and res:
            mail_pool = self.env['mail.thread']
            body = _(
                '''<div class="o_mail_notification">
                    Kit not correct exploded:<br/>
                    %s
                    </div>
                ''') % res

            mail_pool.sudo().message_post(
            #mail_pool.message_post(
                body=body, 
                message_type='notification', 
                subject=_('Kit not found'),
                )
        return True
        
    @api.model
    def check_product_first_supplier(self):
        ''' Update product without first supplier:
        '''
        log_message = True # TODO change
        line_pool = self.env['sale.order.line']
        template_pool = self.env['product.template']
        
        lines = line_pool.search([
            ('order_id.logistic_state', '=', 'draft'), # Draft order
            ('product_id.default_supplier_id', '=', False), # No first supplier
            ('product_id.is_kit', '=', False), # No kit line
            ])
        template_ids = []
        update_ids = []
        for line in lines:
            template = line.product_id.product_tmpl_id            
            if template.id in template_ids:
                continue
            template_ids.append(template.id)
            try:
                update_ids.append(template.id)
                template.get_default_supplier_from_code()
            except:
                pass    
            
        # Check updated record:
        templates = template_pool.search([
            ('id', 'in', update_ids), # Updated lines:
            ('default_supplier_id', '=', False), # Not updated
            ])
        res = ''    
        for template in templates:
            res += '%s<br/>' % template.default_code
            
        if log_message and res:
            mail_pool = self.env['mail.thread']
            body = _(
                '''<div class="o_mail_notification">
                    First supplier not found:<br/>
                    %s
                    </div>
                ''') % res

            mail_pool.sudo().message_post(
            #mail_pool.message_post(
                body=body, 
                message_type='notification', 
                subject=_('Default supplier not found'),
                )
        return True
    
    def check_empty_orders(self):
        ''' Mark empty order as unused
        '''
        orders = self.search([
            ('logistic_state', '=', 'draft'), # Insert order
            ('order_line', '=', False), # Without line
            ])
        return orders.write({
            'logistic_state': 'error',
            })    
    
    def check_product_service(self):
        ''' Update line with service to ready state
        '''
        line_pool = self.env['sale.order.line']
        lines = line_pool.search([
            ('order_id.logistic_state', '=', 'draft'), # Draft order
            ('logistic_state', '=', 'draft'), # Draft line
            ('product_id.type', '=', 'service'), # Direct ready
            ('kit_line_id', '=', False), # Not the kit line (service = mrp)
            ])
        return lines.write({
            'logistic_state': 'ready', # immediately ready
            })
        
    # -------------------------------------------------------------------------
    #                   WORKFLOW: [LOGISTIC OPERATION TRIGGER]
    # -------------------------------------------------------------------------    
    # A. Logistic phase 1: Check secure payment:
    # -------------------------------------------------------------------------    
    @api.model
    def workflow_order_to_payment(self):
        ''' Assign logistic_state to secure order
        '''
        # ---------------------------------------------------------------------
        #                               Pre operations:
        # ---------------------------------------------------------------------
        # Empty orders:
        self.check_empty_orders() # Order without line
        
        # Payment article: 
        self.check_product_service() # Line with service article (not used)
        
        # Explode kit if present (create also product service):
        self.check_exploded_product_kit()
        
        # Update supplier if present:
        self.check_product_first_supplier()
        
        # ---------------------------------------------------------------------
        # Start order payment check:
        # ---------------------------------------------------------------------
        orders = self.search([
            ('logistic_state', '=', 'draft'), # new order
            ])

        # Search new order:
        payment_order = []
        for order in orders:
            # -----------------------------------------------------------------
            # 1. Marked as done (script or in form)
            # -----------------------------------------------------------------
            if order.payment_done:
                payment_order.append(order)
                continue

            # -----------------------------------------------------------------
            # 2. Secure market (sale team):    
            # -----------------------------------------------------------------
            try: # error if not present
                if order.team_id.secure_payment:
                    payment_order.append(order)
                    continue
            except:   
                pass

            # -----------------------------------------------------------------
            # 3. Secure payment in fiscal position     
            # -----------------------------------------------------------------
            try: # problem in not present
                position = order.partner_id.property_account_position_id
                payment = order.payment_term_id
                if payment and payment in [
                        secure.payment_id for secure in position.secure_ids]:
                    payment_order.append(order)
                    continue
            except:   
                pass
        
        # ---------------------------------------------------------------------
        # Update state: order >> payment
        # ---------------------------------------------------------------------
        for order in payment_order:
            order.payment_done = True
            order.logistic_state = 'payment'

        # Return view tree:
        return payment_order.return_order_view()

    # -------------------------------------------------------------------------
    # B. Logistic phase 2: payment > order
    # -------------------------------------------------------------------------
    @api.model
    def workflow_payment_to_order(self):
        ''' Confirm payment order (before expand kit)
        '''
        orders = self.search([
            ('logistic_state', '=', 'payment'),
            ])
        for order in orders:    
            # A. Generate subelements from kit:
            order.explode_kit_in_order_line()

            # C. Became real order:
            order.logistic_state = 'order'

        # Return view:
        return orders.return_order_view()

    # State (sort of workflow):
    # TODO
    #dropshipping = fields.Boolean('Dropshipping', 
    #    help='All order will be managed externally')
        
    logistic_state = fields.Selection([
        ('draft', 'Order draft'), # Draft, new order received
        ('payment', 'Payment confirmed'), # Payment confirmed
        
        # Start automation:
        ('order', 'Order confirmed'), # Quotation transformed in order
        ('pending', 'Pending delivery'), # Waiting for delivery
        ('ready', 'Ready'), # Ready for transfer
        ('done', 'Done'), # Delivered or closed XXX manage partial delivery
        ('error', 'Error order'), # Order without line
        ], 'Logistic state', default='draft',
        )

class SaleOrderLine(models.Model):
    """ Model name: Sale Order Line
    """
    
    _inherit = 'sale.order.line'
    
    # -------------------------------------------------------------------------
    #                           UTILITY:
    # -------------------------------------------------------------------------
    @api.model
    def return_order_line_list_view(self, line_ids):
        ''' Return order line tree view (selected)
        '''
        model_pool = self.env['ir.model.data']
        tree_view_id = model_pool.get_object_reference(
            'logistic_management', 'view_sale_order_line_logistic_tree')[1]
        form_view_id = model_pool.get_object_reference(
            'logistic_management', 'view_sale_order_line_logistic_form')[1]
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Updated lines'),
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

    # -------------------------------------------------------------------------
    #                   WORKFLOW: [LOGISTIC OPERATION TRIGGER]
    # -------------------------------------------------------------------------
    # A. Assign available q.ty in stock assign a stock movement / quants
    @api.model
    def workflok_order_to_uncovered(self):
        ''' Logistic phase 3:
            Assign stock q. available to order product creating a 
            stock.move or stock.quant movement 
            Evaluate also if we can use alternative product
        '''
        now = fields.Datetime.now()

        product_pool = self.env['product.product']
        quant_pool = self.env['stock.quant']
        lines = self.search([
            ('order_id.logistic_state', '=', 'order'), # Logistic state
            ('logistic_state', '=', 'draft'),
            ])

        # ---------------------------------------------------------------------
        # Load parameter from company setup:
        # ---------------------------------------------------------------------
        if lines:
            # Access company parameter from first line
            company = lines[0].order_id.company_id
            
            location_id = company.logistic_location_id.id
            sort = company.logistic_order_sort
            mode = company.logistic_assign_mode
            
            _logger.info(
                'Update order with parameter: '
                'Location: %s, sort: %s, mode: %s' % (
                    location_id, sort, mode))
        else:
            _logger.info('No line ready for assign stock qty')
            return True 

        # ---------------------------------------------------------------------
        # Parameter: Sort options:
        # ---------------------------------------------------------------------
        if sort == 'create_date':
            sorted_line = sorted(lines, key=lambda x:
                x.order_id.create_date)
        else: # validity_date
            sorted_line = sorted(lines, key=lambda x:
                x.order_id.validity_date or x.order_id.create_date)
            
        # ---------------------------------------------------------------------
        #                  Modify sale order line status:
        # ---------------------------------------------------------------------
        update_db = {}
        for line in sorted_line:
            product = line.product_id
            
            # -----------------------------------------------------------------
            # Kit line not used:
            # -----------------------------------------------------------------
            if not product or product.is_kit:
                update_db[line] = {
                    'logistic_state': 'unused',
                    }
                continue # Comment line

            order_qty = line.product_uom_qty
            
            # -----------------------------------------------------------------
            # Similar pool generate:
            # -----------------------------------------------------------------
            product_list = [product] # Start list first with this product
            if product.similar_ids: 
                # Search other product from template list
                template_ids = [
                    template.id for template in product.similar_ids]
                similar_product = product_pool.search([
                    ('product_tmpl_id', 'in', template_ids),
                    ])
                product_list.extend([item for item in similar_product])
            
            # -----------------------------------------------------------------
            # Use stock to cover order:
            # -----------------------------------------------------------------
            state = False # Used for check if used some pool product
            for used_product in product_list:                    
                stock_qty = used_product.qty_available
                assign_quantity = 0.0 # To check is was created

                # -------------------------------------------------------------
                # Manage mode of use stock: (TODO better available)
                # -------------------------------------------------------------
                if mode == 'first_available' and stock_qty:
                    if stock_qty > order_qty:
                        assign_quantity = order_qty
                        state = 'ready'
                    else:    
                        assign_quantity = stock_qty
                        state = 'uncovered'

                    company = line.order_id.company_id # XXX
                    data = {
                        'company_id': company.id,
                        'in_date': now,
                        'location_id': location_id,
                        'product_id': used_product.id,
                        #'product_tmpl_id': used_product.product_tmpl_id.id,
                        #'lot_id' #'package_id'
                        'quantity': - assign_quantity,

                        # Link field:
                        'logistic_assigned_id': line.id,
                        }            
                    quant_pool.create(data)
                    
                    # Update line if quant created                
                    update_db[line] = {
                        'logistic_state': state,
                        }

                # -------------------------------------------------------------
                # TODO manage alternative product here!    
                # -------------------------------------------------------------
                
                # -------------------------------------------------------------
                # Update similar product in order line (if used):
                # -------------------------------------------------------------
                if state and used_product != product:
                    # Update sale line with information:
                    update_db[line]['linked_mode'] = 'similar'
                    update_db[line]['origin_product_id'] = product.id
                    update_db[line]['product_id'] = used_product.id
                    
                if assign_quantity:
                    break # no other product was taken
                    
            # -----------------------------------------------------------------
            # No stock passed in uncovered state:
            # -----------------------------------------------------------------
            if line not in update_db: 
                update_db[line] = {
                    'logistic_state': 'uncovered',
                    }

        # ---------------------------------------------------------------------
        # Update sale line status:
        # ---------------------------------------------------------------------
        selected_ids = [] # ID, to return view list
        selected_order = [] # Obj, to update master order status
        for line in update_db:
            line.write(update_db[line])
            selected_ids.append(line.id)
            if line.order_id not in selected_order:
                selected_order.append(line.order_id)                

        # ---------------------------------------------------------------------
        # Update order to 'ready' status:
        # ---------------------------------------------------------------------
        all_ready = set(['ready'])
        for order in selected_order:
            # Generate list of line state, jump not used:                
            line_logistic_state = [
                line.logistic_state for line in order.order_line \
                    if line.logistic_state != 'unused']
                    
            # -----------------------------------------------------------------        
            # Update order state depend on all line:        
            # -----------------------------------------------------------------        
            if all_ready == set(line_logistic_state):
                order.logistic_state = 'ready'
            else: # All other order stay in pending state:
                order.logistic_state = 'pending'
            # TODO Manage Dropshipping!!    
            
        # Return view:
        return self.return_order_line_list_view(selected_ids)
    
    # A. Assign available q.ty in stock assign a stock movement / quants
    @api.model
    def workflow_uncovered_pending(self):
        ''' Logistic phase 2:            
            Order remain uncovered qty to the default supplier            
            Generate purchase order to supplier linked to product
        '''
        now = fields.Datetime.now()
        
        # ---------------------------------------------------------------------
        # Pool used:
        # ---------------------------------------------------------------------
        purchase_pool = self.env['purchase.order']
        purchase_line_pool = self.env['purchase.order.line']        

        # Update only pending order with uncovered lines
        lines = self.search([
            # Filter logistic state:
            ('order_id.logistic_state', '=', 'pending'),
            
            # Filter line state:
            ('logistic_state', '=', 'uncovered'),
            ])

        # ---------------------------------------------------------------------
        # Parameter from company:
        # ---------------------------------------------------------------------
        if lines:
            # Access company parameter from first line
            company = lines[0].order_id.company_id
        else: # No lines found:
            return True

        # ---------------------------------------------------------------------
        #                 Collect data for purchase order:
        # ---------------------------------------------------------------------
        purchase_db = {} # supplier is the key
        for line in lines:
            product = line.product_id
            supplier = product.default_supplier_id
            if supplier not in purchase_db:
                purchase_db[supplier] = []
            purchase_db[supplier].append(line)

        selected_ids = [] # ID: to return view list
        for supplier in purchase_db:
            # -----------------------------------------------------------------
            # Create header:
            # -----------------------------------------------------------------            
            partner = supplier or company.partner_id # Use company 
            # TODO if order was deleted restore logistic_state to uncovered

            purchase = purchase_pool.create({
                'partner_id': partner.id,
                'date_order': now,
                'date_planned': now,
                #'name': # TODO counter?
                #'partner_ref': '',
                #'logistic_state': 'draft',
                })
            selected_ids.append(purchase.id)

            # -----------------------------------------------------------------
            # Create details:
            # -----------------------------------------------------------------
            for line in purchase_db[supplier]:
                # -------------------------------------------------------------
                # Use stock to cover order:
                # -------------------------------------------------------------
                product = line.product_id
                if not product:
                    continue

                purchase_qty = line.logistic_uncovered_qty
                if purchase_qty <= 0.0:
                    continue # no order negative uncoveder (XXX needed)

                purchase_line_pool.create({
                    'order_id': purchase.id,
                    'product_id': product.id,
                    'name': product.name,
                    'product_qty': purchase_qty,
                    'date_planned': now,
                    'product_uom': product.uom_id.id,
                    'price_unit': 1.0, # TODO change product.0.0,

                    # Link to sale:
                    'logistic_sale_id': line.id,
                    })

                # Update line state:    
                line.logistic_state = 'ordered' # XXX needed?
        
        # Sale order still in pending state so no update of logistic status        
        #`TODO Manage dropshipping here?!?

        # Return view:
        return purchase_pool.return_purchase_order_list_view(selected_ids)


    # -------------------------------------------------------------------------
    #                            COMPUTE FIELDS FUNCTION:
    # -------------------------------------------------------------------------
    @api.multi
    @api.depends('assigned_line_ids', 'purchase_line_ids', 'load_line_ids',
        'delivered_line_ids')
    def _get_logist_status_field(self):
        ''' Manage all data for logistic situation in sale order:
        '''
        _logger.warning('Update logistic qty fields now')
        for line in self:
            if line.product_id.is_kit:
                # -------------------------------------------------------------
                #                           KIT:
                # -------------------------------------------------------------
                # if is kit >> line not used:
                line.logistic_covered_qty = 0.0
                line.logistic_purchase_qty = 0.0
                line.logistic_uncovered_qty = 0.0
                line.logistic_received_qty = 0.0
                line.logistic_remain_qty = 0.0
                line.logistic_delivered_qty = 0.0
                line.logistic_undelivered_qty = 0.0
                #line.logistic_state = 'unused'
            else:
                # -------------------------------------------------------------
                #                       NORMAL PRODUCT:
                # -------------------------------------------------------------
                #state = 'draft'
                # -------------------------------------------------------------
                # OC: Ordered qty:
                # -------------------------------------------------------------
                logistic_order_qty = line.product_uom_qty
                
                # -------------------------------------------------------------
                # ASS: Assigned:
                # -------------------------------------------------------------
                logistic_covered_qty = 0.0
                for quant in line.assigned_line_ids:
                    logistic_covered_qty -= quant.quantity
                line.logistic_covered_qty = logistic_covered_qty
                
                # State valuation:
                #if logistic_order_qty == logistic_covered_qty:
                #    state = 'ready' # All in stock 
                #else:
                #    state = 'uncovered' # To order    

                # -------------------------------------------------------------
                # PUR: Purchase (order done):
                # -------------------------------------------------------------
                logistic_purchase_qty = 0.0
                for purchase in line.purchase_line_ids:
                    logistic_purchase_qty += purchase.product_qty
                line.logistic_purchase_qty = logistic_purchase_qty
                
                # -------------------------------------------------------------
                # UNC: Uncovered (to purchase) [OC - ASS - PUR]:
                # -------------------------------------------------------------
                logistic_uncovered_qty = \
                    logistic_order_qty - logistic_covered_qty - \
                    logistic_purchase_qty
                line.logistic_uncovered_qty = logistic_uncovered_qty

                # State valuation:
                #if state != 'ready' and not logistic_uncovered_qty: # XXX          
                #    state = 'ordered' # A part (or all) is order

                # -------------------------------------------------------------
                # BF: Received (loaded in stock):
                # -------------------------------------------------------------
                logistic_received_qty = 0.0
                for move in line.load_line_ids:
                    logistic_received_qty += move.product_uom_qty # TODO verify
                line.logistic_received_qty = logistic_received_qty
                
                # -------------------------------------------------------------
                # REM: Remain to receive [OC - ASS - BF]:
                # -------------------------------------------------------------
                logistic_remain_qty = \
                    logistic_order_qty - logistic_covered_qty - \
                    logistic_received_qty
                line.logistic_remain_qty = logistic_remain_qty

                # State valuation:
                #if state != 'ready' and not logistic_remain_qty: # XXX
                #    state = 'ready' # All present coveder or in purchase

                # -------------------------------------------------------------
                # BC: Delivered:
                # -------------------------------------------------------------
                logistic_delivered_qty = 0.0
                for move in line.delivered_line_ids:
                    logistic_delivered_qty += move.product_uom_qty # TODO verify
                line.logistic_delivered_qty = logistic_delivered_qty
                
                # -------------------------------------------------------------
                # UND: Undelivered (remain to pick out) [OC - BC]
                # -------------------------------------------------------------
                logistic_undelivered_qty = \
                    logistic_order_qty - logistic_delivered_qty
                line.logistic_undelivered_qty = logistic_undelivered_qty

                # State valuation:
                #if not logistic_undelivered_qty: # XXX
                #    state = 'done' # All delivered to customer
                
                # -------------------------------------------------------------
                # Write data:
                # -------------------------------------------------------------
                #line.logistic_state = state

    # -------------------------------------------------------------------------
    #                                   COLUMNS:
    # -------------------------------------------------------------------------
    # RELATION MANY 2 ONE:

    # A. Assigned stock:
    assigned_line_ids = fields.One2many(
        'stock.quant', 'logistic_assigned_id', 'Assign from stock',
        help='Assign all this q. to this line (usually one2one',
        )

    # B. Purchased:
    purchase_line_ids = fields.One2many(
        'purchase.order.line', 'logistic_sale_id', 'Linked to purchase', 
        help='Supplier ordered line linked to customer\'s one',
        )
    load_line_ids = fields.One2many(
        'stock.move', 'logistic_load_id', 'Linked load to sale', 
        help='Loaded movement in picking in documents',
        )

    # C. Deliver:
    delivered_line_ids = fields.One2many(
        'stock.move', 'logistic_unload_id', 'Linked to deliveder', 
        help='Deliver movement in pick out documents',
        )
    
    # -------------------------------------------------------------------------
    #                               FUNCTION FIELDS:
    # -------------------------------------------------------------------------
    # Computed q.ty data:
    logistic_covered_qty = fields.Float(
        'Covered qty', digits=dp.get_precision('Product Price'),
        help='Qty covered with internal stock',
        readonly=True, compute='_get_logist_status_field', multi=True,
        store=False,
        )
    logistic_uncovered_qty = fields.Float(
        'Uncovered qty', digits=dp.get_precision('Product Price'),
        help='Qty not covered with internal stock (so to be purchased)',
        readonly=True, compute='_get_logist_status_field', multi=True,
        store=False,
        )
    logistic_purchase_qty = fields.Float(
        'Purchase qty', digits=dp.get_precision('Product Price'),
        help='Qty order to supplier',
        readonly=True, compute='_get_logist_status_field', multi=True,
        store=False,
        )
    logistic_received_qty = fields.Float(
        'Received qty', digits=dp.get_precision('Product Price'),
        help='Qty received with pick in delivery',
        readonly=True, compute='_get_logist_status_field', multi=True,
        store=False,
        )
    logistic_remain_qty = fields.Float(
        'Remain qty', digits=dp.get_precision('Product Price'),
        help='Qty remain to receive to complete ordered',
        readonly=True, compute='_get_logist_status_field', multi=True,
        store=False,
        )
    logistic_delivered_qty = fields.Float(
        'Delivered qty', digits=dp.get_precision('Product Price'),
        help='Qty deliverer  to final customer',
        readonly=True, compute='_get_logist_status_field', multi=True,
        store=False,
        )
    logistic_undelivered_qty = fields.Float(
        'Not delivered qty', digits=dp.get_precision('Product Price'),
        help='Qty not deliverer to final customer',
        readonly=True, compute='_get_logist_status_field', multi=True,
        store=False,
        )
    
    # State (sort of workflow):
    logistic_state = fields.Selection([
        ('unused', 'Unused'), # Line not managed
    
        ('draft', 'Custom order'), # Draft, customer order
        ('uncovered', 'Uncovered'), # Not covered with stock
        ('ordered', 'Ordered'), # Supplier order uncovered
        ('ready', 'Ready'), # Order to be picked out (all in stock)
        ('done', 'Done'), # Delivered qty (order will be closed)
        ], 'Logistic state', default='draft',
        #readonly=True, 
        #compute='_get_logist_status_field', multi=True,
        #store=True, # TODO store True # for create columns
        )
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
