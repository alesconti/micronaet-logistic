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
from odoo import api, fields, models, tools, exceptions, SUPERUSER_ID
from odoo import exceptions
from odoo.addons import decimal_precision as dp
from odoo.tools.translate import _


_logger = logging.getLogger(__name__)

class ResCompany(models.Model):
    """ Model name: Res Company
    """
    
    _inherit = 'res.company'

    # -------------------------------------------------------------------------
    # Parameters:
    # -------------------------------------------------------------------------
    # Database structure:
    _logistic_folder_db = {
            'ddt': {
                'default': ('DDT', 'Originali'),
                'history': ('DDT', 'Storico'),
                'supplier': ('DDT', 'Fornitori'),
                },

            'invoice': {
                'default': ('Invoice', 'Originali'),
                'history': ('Invoice', 'Storico'),
                'xml': ('Invoice', 'XML'),
                },

            'bf': {
                'default': 'BF',
                },

            'images': {
                'default': 'images',
                },
            }

    # Get path name:
    @api.model
    def _logistic_folder(self, document, mode='default'):
        ''' Return full path of folder request:
        '''
        folder_block = self._logistic_folder_db[document][mode]    
        return self.get_subfolder_from_root(folder_block)
        

    @api.model
    def get_subfolder_from_root(self, name):
        ''' Get subfolder from root
            if str only one folder, instead multipath
        '''
        try:
            if type(name) == str:
                name = (name, )                
            folder = os.path.expanduser(
                os.path.join(self.logistic_root_folder, *name))

            # Create in not present
            os.system('mkdir -p %s' % folder)
        except:
            raise odoo.exceptions.Warning(
                _('Error creating output folder (check param)'))
        return folder
        
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
        
    # Pick type for load / unload:
    logistic_pick_in_type_id = fields.Many2one(
        'stock.picking.type', 'Pick in type', 
        help='Picking in type for load documents',
        required=True,
        )
    logistic_pick_out_type_id = fields.Many2one(
        'stock.picking.type', 'Pick out type', 
        help='Picking in type for unload documents',
        required=True,
        )
    logistic_root_folder = fields.Text(
        'Output root folder', 
        help='Master root folder for output',
        required=True,
        )    

class ProductTemplate(models.Model):
    ''' Template add fields
    '''
    _inherit = 'product.template'

    @api.model
    def _get_root_image_folder(self):
        ''' Use filestrore folder and subfolder images
        '''
        company_pool = self.env['res.company']
        companys = company_pool.search([])
        return companys[0]._logistic_folder('images')

    # -------------------------------------------------------------------------
    # Columns:
    # -------------------------------------------------------------------------
    is_expence = fields.Boolean('Expense product', 
        help='Expense product is not order and produced')
    
class PurchaseOrder(models.Model):
    """ Model name: Sale Order
    """
    
    _inherit = 'purchase.order'

    # -------------------------------------------------------------------------
    #                           UTILITY:
    # -------------------------------------------------------------------------
    @api.model
    def return_purchase_order_list_view(self, purchase_ids):
        ''' Return purchase order tree from ids
        '''
        model_pool = self.env['ir.model.data']
        tree_view_id = form_view_id = False
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Purchase order selected:'),
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

    @api.model
    def check_order_confirmed_done(self, purchase_ids=None):
        ''' Check passed purchase IDs passed or all confirmed order
            if not present
        '''
        if purchase_ids: 
            purchases = self.search([('id', 'in', purchase_ids)])
        else:
            purchases = self.search([('logistic_state', '=', 'confirmed')])
        
        for purchase in purchases:
            done = True
            
            for line in purchase.order_line:
                if line.logistic_undelivered_qty > 0:
                    done = False
                    break
            # Update if all line hasn't undelivered qty        
            if done:
                purchase.logistic_state = 'done'
        return True        
                
    # -------------------------------------------------------------------------
    #                            BUTTON:
    # -------------------------------------------------------------------------
    @api.multi
    def open_purchase_line(self):
        ''' Open purchase line detail view:
        '''
        model_pool = self.env['ir.model.data']
        tree_view_id = model_pool.get_object_reference(
            'logistic_management', 'view_purchase_order_line_tree')[1]
        form_view_id = model_pool.get_object_reference(
            'logistic_management', 'view_purchase_order_line_form')[1]

        line_ids = [item.id for item in self.order_line]
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Purchase line'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            #'res_id': 1,
            'res_model': 'purchase.order.line',
            'view_id': tree_view_id,
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'domain': [('id', '=', line_ids)],
            'context': self.env.context,
            'target': 'current', # 'new'
            'nodestroy': False,
            }
        
    # Workflow button:
    @api.multi
    def set_logistic_state_confirmed(self):
        ''' Set order as confirmed
        '''
        # Export if needed the purchase order:
        self.export_purchase_order()
        now = fields.Datetime.now()
        
        return self.write({
            'logistic_state': 'confirmed',
            'date_planned': now,
            })

    # -------------------------------------------------------------------------
    #                                COLUMNS: 
    # -------------------------------------------------------------------------
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

    # LOAD WITHOUT SUPPLIER: Load management:
    logistic_quant_id = fields.Many2one(
        'stock.quant', 'Stock quant', 
        help='Link to stock quant generated (load / unoad data).', 
        index=True, ondelete='cascade',
        )

class PurchaseOrderLine(models.Model):
    """ Model name: Purchase Order Line
    """
    
    _inherit = 'purchase.order.line'

    # -------------------------------------------------------------------------
    # Function fields:
    # -------------------------------------------------------------------------
    @api.multi
    @api.depends('load_line_ids', )
    def _get_logistic_status_field(self):
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
        readonly=True, compute='_get_logistic_status_field', multi=True,
        store=False,
        )
    logistic_undelivered_qty = fields.Float(
        'Undelivered qty', digits=dp.get_precision('Product Price'),
        help='Qty undelivered, remain to load',
        readonly=True, compute='_get_logistic_status_field', multi=True,
        store=False,
        )

    # TODO logistic state?
    
    # RELATIONAL:
    load_line_ids = fields.One2many(
        'stock.move', 'logistic_purchase_id', 'Linked load to purchase', 
        help='Load linked to this purchase line',
        )

class StockPicking(models.Model):
    """ Model name: Stock picking
    """
    
    _inherit = 'stock.picking'
    
    # -------------------------------------------------------------------------
    # Override path function:
    # -------------------------------------------------------------------------
    # Path: DDT, Invoice (module: logistic_account_report)
    @api.multi
    def get_default_folder_path(self):
        ''' Override default extract DDT function:
        '''        
        companys = self.env['res.company'].search([])
        return companys[0]._logistic_folder('ddt')

    @api.multi
    def get_default_folder_invoice_path(self):
        ''' Override default extract Invoice function:
        '''        
        companys = self.env['res.company'].search([])
        return companys[0]._logistic_folder('invoice')

    # Path: XML Invoice
    @api.multi
    def get_default_folder_xml_invoice(self):
        ''' Override default extract XML Invoice
        '''
        companys = self.env['res.company'].search([])
        return companys[0]._logistic_folder('invoice', 'xml')
    
    # -------------------------------------------------------------------------
    #                                   UTILITY:
    # -------------------------------------------------------------------------
    # TODO remove!!!
    @api.model
    def workflow_ready_to_done_all_done_picking(self):
        ''' Confirm draft picking documents
        '''
        pickings = self.search([
            ('state', '=', 'draft'),
            # TODO out document! (),
            ])
        return pickings.workflow_ready_to_done_done_picking()

    # Export Excel file with loaded picking:
    @api.multi
    def export_excel_picking_report(self):
        """ Export excel picking data
            line
        """
        self.ensure_one()
        companys = self.env['res.company'].search([])
        folder = companys[0]._logistic_folder('bf')
        excel_pool = self.env['excel.writer']

        ws_name = 'Carichi'
        excel_pool.create_worksheet(ws_name)
        
        # ---------------------------------------------------------------------
        # Format:
        # ---------------------------------------------------------------------
        excel_pool.set_format()
        f_title = excel_pool.get_format('title')
        f_header = excel_pool.get_format('header')

        f_white_text = excel_pool.get_format('text')
        f_green_text = excel_pool.get_format('bg_green')
        f_yellow_text = excel_pool.get_format('bg_yellow')
        
        f_white_number = excel_pool.get_format('number')
        f_green_number = excel_pool.get_format('bg_green_number')
        f_yellow_number = excel_pool.get_format('bg_yellow_number')
        
        # ---------------------------------------------------------------------
        # Setup page:
        # ---------------------------------------------------------------------
        excel_pool.column_width(ws_name, [
            20, 20, 20, 25, 10, 10, 20,
            ])
        
        # ---------------------------------------------------------------------
        # Extra data:
        # ---------------------------------------------------------------------
        now = fields.Datetime.now()
        
        #for picking in self:
        picking = self
        partner = picking.partner_id.name
        origin = picking.origin
        row = 0
        excel_pool.write_xls_line(ws_name, row, [
            'Fornitore: %s Documento di origine: %s [%s]' % (
                partner,
                origin,    
                now,
                )], default_format=f_title)
        row += 1
        excel_pool.write_xls_line(ws_name, row, [
             'Foto', 'Codice', 'Nome', 'Ordine', 'Stato', 'Q.', 'Posizione'
             ], default_format=f_header)
        for move in picking.move_lines:
            row +=1 
            product = move.product_id
            template = product.product_tmpl_id
            sale_line = move.logistic_load_id
            order = sale_line.order_id
            if order:
                if order.logistic_state == 'pending':
                    f_text = f_yellow_text
                    f_number = f_yellow_number
                else: # done
                    f_text = f_green_text
                    f_number = f_green_number
                slot_name = move.slot_id.name    
                         
            else:
                f_text = f_white_text
                f_number = f_white_number
                slot_name = product.default_slot_id.name \
                    if product.default_slot_id else 'Manca per il prodotto'
                        
            
            excel_pool.write_xls_line(ws_name, row, [
                 '', 
                 template.default_code,
                 template.name,
                 
                 order.name if order else _('MAGAZZINO'),
                 order.logistic_state if order else '',

                 (move.product_uom_qty, f_number),                     
                 slot_name,
                 ], default_format=f_text)
             
        # ---------------------------------------------------------------------
        # Save file:
        # ---------------------------------------------------------------------
        filename = 'BF_%s_%s.xlsx' % (
                partner,
                origin
                )
        filename = filename.replace(
            ':', '_').replace(' ', '').replace('[', '_').replace(']', '')
        #now = now.replace(':', '_').replace('-', '_')
        fullname = os.path.join(folder, filename)

        excel_pool.save_file_as(fullname)
        return True

    # -------------------------------------------------------------------------
    #                                   BUTTON:
    # -------------------------------------------------------------------------
    @api.multi
    def workflow_ready_to_done_done_picking(self):
        ''' Confirm draft picking documents
        '''
        # ---------------------------------------------------------------------
        # Confirm pickign for DDT and Invoice:
        # ---------------------------------------------------------------------
        ddt_ids = [] # For extra operation after
        invoice_ids = [] # For extra operation after
        for picking in self:
            # Assign always DDT number:
            picking.assign_ddt_number()
            ddt_ids.append(picking.id)
            
            # Invoice procedure (check rules):
            if picking.partner_id.need_invoice:
                picking.assign_invoice_number()
                invoice_ids.append(picking.id)
            
            picking.write({
                'state': 'done', # TODO needed?
                })
                
        # ---------------------------------------------------------------------
        # DDT extra operations: (require reload)        
        # ---------------------------------------------------------------------
        companys = self.env['res.company'].search([])
        folder = companys[0]._logistic_folder('ddt')
        history_folder = companys[0]._logistic_folder('ddt', 'history')

        for picking in self.search([('id', 'in', ddt_ids)]):
            # -----------------------------------------------------------------
            #                 DDT Extract:
            # -----------------------------------------------------------------        
            # 1. DDT Extract procedure:
            original_fullname = picking.extract_account_ddt_report()
            
            # 2. DDT Symlink procedure:
            original_base = os.path.basename(original_fullname)
            date = picking.scheduled_date
            month_path = os.path.join(history_folder, date[:4], date[5:7])
            os.system('mkdir -p %s' % month_path)
            symlink = os.system('ln -s "%s" "%s"' % (
                original_fullname,
                os.path.join(month_path, original_base)
                ))
            
            # 3. DDT Print procedure:
            # TODO 

        # ---------------------------------------------------------------------
        # Invoice extra operations: (require reload)        
        # ---------------------------------------------------------------------
        folder = companys[0]._logistic_folder('invoice')
        history_folder = companys[0]._logistic_folder('invoice', 'history')

        for picking in self.search([('id', 'in', invoice_ids)]):
            # -----------------------------------------------------------------
            #                 Invoice Extract:
            # -----------------------------------------------------------------        
            # 1. Invoice Extract procedure:
            original_fullname = picking.extract_account_invoice_report()
            
            # 2. Invoice Symlink procedure:
            original_base = os.path.basename(original_fullname)
            date = picking.scheduled_date
            month_path = os.path.join(history_folder, date[:4], date[5:7])
            os.system('mkdir -p %s' % month_path)
            symlink = os.system('ln -s "%s" "%s"' % (
                original_fullname,
                os.path.join(month_path, original_base)
                ))
            
            # 3. Invoice Print procedure:
            # TODO 

            # 4. Extract electronic invoice:
            picking.extract_account_electronic_invoice()

    @api.multi
    def assign_invoice_number(self):
        ''' Assign invoice number depend on fiscal position and parameter in
            partner configuration
        '''
        for picking in self:
            # Load partner sequence (depend on fiscal position)
            partner = picking.partner_id
            sequence = partner.property_account_position_id.sequence_id
            picking.write({
                'invoice_number': sequence.next_by_id()
                })
        return True
                
    @api.multi
    def assign_ddt_number(self):
        ''' Assign DDt number depend on fiscal position and parameter in
            partner configuration
        '''
        # TODO Manage sequence from fiscal position
        for picking in self:
            picking.write({
                'ddt_number': self.env['ir.sequence'].next_by_code(
                    'stock.picking.ddt.sequence')
                })
        return True
        
    # -------------------------------------------------------------------------
    #                                   COLUMNS:
    # -------------------------------------------------------------------------
    sale_order_id = fields.Many2one(
        'sale.order', 'Sale order', help='Sale order generator')
        
    # Fiscal number:    
    invoice_number = fields.Char('Invoice number') 
    ddt_number = fields.Char('DDT number') 
    
    
class AccountFiscalPosition(models.Model):
    """ Model name: Stock quant
    """
    
    _inherit = 'account.fiscal.position'
    
    # -------------------------------------------------------------------------
    #                                   COLUMNS:
    # -------------------------------------------------------------------------
    invoice_id = fields.Many2one(
        'ir.sequence', 'Invoice sequence', help='Invoice sequence default')        
    ddt_id = fields.Many2one(
        'ir.sequence', 'DDT sequence', help='DDT sequence default')
        
class ResPartner(models.Model):
    """ Model name: Res Partner
    """
    
    _inherit = 'res.partner'
    
    # -------------------------------------------------------------------------
    #                                   COLUMNS:
    # -------------------------------------------------------------------------
    need_invoice = fields.Boolean('Always invoice')


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
    #                           BUTTON EVENTS:
    # -------------------------------------------------------------------------
    # Extra operation before WF
    @api.multi
    def return_order_line_list_view(self):
        ''' Return order line in a tree view
        '''
        line_ids = self[0].order_line.mapped('id')
        return self.env['sale.order.line'].return_order_line_list_view(
            line_ids)

    # -------------------------------------------------------------------------
    #                           UTILITY:
    # -------------------------------------------------------------------------
    @api.multi # XXX not api.one?!?
    def logistic_check_and_set_ready(self):
        ''' Check if all line are in ready state (excluding unused)
        '''
        for order in self:
            line_state = set(order.order_line.mapped('logistic_state'))
            line_state.discard('unused') # remove kit line (exploded)
            line_state.discard('done') # if some line are in done (multidelivery)
            if tuple(line_state) == ('ready', ): # All ready
                order.write({
                    'logistic_state': 'ready',
                    })
        return True

    @api.multi
    def logistic_check_and_set_delivering(self):
        ''' Check if all line are in done state (excluding unused)
        '''
        for order in self:
            line_state = set(order.order_line.mapped('logistic_state'))
            line_state.discard('unused') # remove kit line (exploded)
            if tuple(line_state) == ('done', ): # All done
                order.write({
                    'logistic_state': 'delivering', # XXX ex done
                    })
        return True

    # Extra operation before WF
    @api.model
    def return_order_list_view(self, order_ids):
        ''' Utility for return selected order in tree view
        '''
        tree_view_id = form_view_id = False
        _logger.info('Return order tree view [# %s]' % len(order_ids))
        return {
            'type': 'ir.actions.act_window',
            'name': _('Order confirmed'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            #'res_id': 1,
            'res_model': 'sale.order',
            'view_id': tree_view_id,
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'domain': [('id', 'in', order_ids)],
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
            #'|', ('product_id.default_code', '=ilike', '%#%'),
            ('product_id.product_tmpl_id.default_code', '=ilike', '%#%'), # Kit code
            # TODO replace with: ('is__kit', '=', True),
            ])
        _logger.info('New order: check explode kit [# %s]' % len(lines))

        template_ids = [] # ID of template checked
        update_ids = [] # ID of template updated
        for line in lines:
            template = line.product_id.product_tmpl_id
            if template.id in template_ids:
                continue
            template_ids.append(template.id)
            
            if '#' not in template.default_code: # Not a kit
                continue
                
            code_part = template.default_code.split('#')
            if len(code_part) != len(template.component_ids):
                try:
                    update_ids.append(template.id)
                    template.explode_kit_from_name()
                except:
                    pass    
            else:
                template.is_kit = True

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
            ('product_id.type', '!=', 'service'), # No service product
            ])
        _logger.info('New order: generate first supplier [# %s]' % len(lines))
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
                    </div>''') % res

            mail_pool.sudo().message_post(
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
        _logger.info('New order: Empty order [# %s]' % len(orders))

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
        _logger.info('New order: Check product-service [# %s]' % len(lines))
        return lines.write({
            'logistic_state': 'ready', # immediately ready
            })
        
    # -------------------------------------------------------------------------
    #                   WORKFLOW: [LOGISTIC OPERATION TRIGGER]
    # -------------------------------------------------------------------------    
    # A. Logistic phase 1: Check secure payment:
    # -------------------------------------------------------------------------    
    @api.model
    def workflow_draft_to_payment(self):
        ''' Assign logistic_state to secure order
        '''
        _logger.info('New order: Start analysis')
        # ---------------------------------------------------------------------
        #                               Pre operations:
        # ---------------------------------------------------------------------
        # Empty orders:
        self.check_empty_orders() # Order without line
        
        # Payment article (not kit now):
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
        _logger.info('New order: Selection [# %s]' % len(orders))

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
        select_ids = []
        for order in payment_order:
            select_ids.append(order.id)
            order.payment_done = True
            order.logistic_state = 'payment'

        # Return view tree:
        return self.return_order_list_view(select_ids)

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
        selected_ids = []
        for order in orders:    
            selected_ids.append(order.id)
            # A. Generate subelements from kit:
            order.explode_kit_in_order_line()

            # C. Became real order:
            order.logistic_state = 'order'

        # Update default supplier for exploded component:
        
        # Return view:
        return self.return_order_list_view(selected_ids)

    # State (sort of workflow):
    # TODO
    #dropshipping = fields.Boolean('Dropshipping', 
    #    help='All order will be managed externally')

    # -------------------------------------------------------------------------
    # B. Logistic delivery phase: ready > done
    # -------------------------------------------------------------------------
    @api.model
    def workflow_ready_to_done_draft_picking(self):
        ''' Confirm payment order (before expand kit)
        '''
        now = fields.Datetime.now()
        
        # Pool used:
        picking_pool = self.env['stock.picking']
        move_pool = self.env['stock.move']
        company_pool = self.env['res.company']

        # ---------------------------------------------------------------------
        # Parameters:
        # ---------------------------------------------------------------------
        company = company_pool.search([])[0]
        logistic_pick_out_type = company.logistic_pick_out_type_id

        logistic_pick_out_type_id = logistic_pick_out_type.id
        location_from = logistic_pick_out_type.default_location_src_id.id
        location_to = logistic_pick_out_type.default_location_dest_id.id

        # ---------------------------------------------------------------------
        # Select order to prepare:
        # ---------------------------------------------------------------------
        orders = self.search([
            ('logistic_state', '=', 'ready'),
            ])
            
        #ddt_list = []
        #invoice_list = []    
        picking_ids = [] # return value
        for order in orders:
            # Create picking document:
            partner = order.partner_id
            name = order.name # same as order_ref
            origin = _('%s [%s]') % (order.name, order.create_date[:10])
            
            picking = picking_pool.create({                
                'sale_order_id': order.id, # Link to order
                'partner_id': partner.id,
                'scheduled_date': now,
                'origin': origin,
                #'move_type': 'direct',
                'picking_type_id': logistic_pick_out_type_id,
                'group_id': False,
                'location_id': location_from,
                'location_dest_id': location_to,
                #'priority': 1,                
                'state': 'draft', # XXX To do manage done phase (for invoice)!!
                })
            picking_ids.append(picking.id)    
                
            for line in order.order_line:
                product = line.product_id
                product_qty = line.logistic_undelivered_qty
                
                # Update line status:
                line.write({'logistic_state': 'done', })

                # ---------------------------------------------------------
                # Create movement (not load stock):
                # ---------------------------------------------------------
                # TODO Check kit!!
                move_pool.create({
                    'company_id': company.id,
                    'partner_id': partner.id,
                    'picking_id': picking.id,
                    'product_id': product.id, 
                    'name': product.name or ' ',
                    'date': now,
                    'date_expected': now,
                    'location_id': location_from,
                    'location_dest_id': location_to,
                    'product_uom_qty': product_qty,
                    'product_uom': product.uom_id.id,
                    'state': 'done',
                    'origin': origin,
                    'price_unit': product.standard_price,
                    
                    # Sale order line link:
                    'logistic_unload_id': line.id,

                    # group_id
                    # reference'
                    # sale_line_id
                    # procure_method,
                    #'product_qty': select_qty,
                    })
            # TODO check if DDT / INVOICE document:

        # ---------------------------------------------------------------------
        # Confirm picking (DDT and INVOICE)
        # ---------------------------------------------------------------------
        picking_pool.search([
            ('id', 'in', picking_ids),
            ]).workflow_ready_to_done_done_picking()

        # ---------------------------------------------------------------------
        # Order status:    
        # ---------------------------------------------------------------------
        # Change status order ready > done
        orders.logistic_check_and_set_delivering()
        return picking_ids    

    # -------------------------------------------------------------------------
    # C. delivering > done
    # -------------------------------------------------------------------------
    @api.multi
    def wf_set_order_as_done(self):
        ''' Set order as done (from delivering)
        '''
        self.ensure_one()
        self.logistic_state = 'done'
            
    # -------------------------------------------------------------------------
    # Columns:
    # -------------------------------------------------------------------------
    logistic_picking_ids = fields.One2many(
        'stock.picking', 'sale_order_id', 'Picking')

    logistic_state = fields.Selection([
        ('draft', 'Order draft'), # Draft, new order received
        ('payment', 'Payment confirmed'), # Payment confirmed
        
        # Start automation:
        ('order', 'Order confirmed'), # Quotation transformed in order
        ('pending', 'Pending delivery'), # Waiting for delivery
        ('ready', 'Ready'), # Ready for transfer
        ('delivering', 'Delivering'), # In delivering phase
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
    def logistic_check_ready_order(self, sale_lines=None):
        ''' Mask as done sale order with all ready lines
            if not present find all order in pending state
        '''        
        order_pool = self.env['sale.order']
        if sale_lines:
            # Start from sale order line:
            order_checked = []
            for line in sale_lines:
                order = line.order_id
                if order in order_checked:
                    continue
                # Check sale.order logistic status (once):    
                order.logistic_check_and_set_ready()
                order_checked.append(order)    
        else:
            # Check pending order:
            orders = order_pool.search([('logistic_state', '=', 'pending')])            
            orders.logistic_check_and_set_ready()
        return True
            
    @api.model
    def return_order_line_list_view(self, line_ids):
        ''' Return order line tree view (selected)
        '''
        # Gef view
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
    #                   WORKFLOW: [LAVORATION OPERATION TRIGGER]
    # -------------------------------------------------------------------------    
    # A. Draft > Progress
    @api.multi
    def workflow_mrp_draft_to_progress(self):
        ''' Update mrp_state
        '''
        for line in self:
            self.mrp_state = 'progress'
        
    # B. Progress > Done
    def workflow_mrp_progress_to_done(self):
        ''' Update mrp_state
        '''
        line_pool = self.env['sale.order.line']
        
        #line_ids = []
        for line in self:
            #line_ids.append(line.id)
            line.mrp_state = 'done'
            
            # Update also logistic state to ready:
            line.logistic_state = 'ready'
            
        # Check master order (reload lines for updated status):
        #sale_lines = line_pool.search([('id', 'in', line_ids)])
        line_pool.logistic_check_ready_order(self)#sale_lines)

    # -------------------------------------------------------------------------    

    # -------------------------------------------------------------------------
    #                   WORKFLOW: [LOGISTIC OPERATION TRIGGER]
    # -------------------------------------------------------------------------
    # A. Assign available q.ty in stock assign a stock movement / quants
    @api.model
    def workflow_order_to_uncovered(self):
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
        update_db = {} # Line to be updated
        #sale_line_ready = [] # To check if order also is ready

        # This fix a bug because stock status don't update immediately
        quant_used = {} # product quant used during process
        
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
                # XXX Remove used qty during assign process:
                stock_qty = used_product.qty_available - \
                    quant_used.get(product, 0.0)

                # -------------------------------------------------------------
                # Manage mode of use stock: (TODO better available)
                # -------------------------------------------------------------
                assign_quantity = 0.0 # To check is was created
                if mode == 'first_available' and stock_qty:
                    if stock_qty > order_qty:
                        assign_quantity = order_qty
                        state = 'ready'
                        #sale_line_ready.append(line)
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
                    
                    # ---------------------------------------------------------
                    # Save used stock for next elements:
                    # ---------------------------------------------------------
                    if product not in quant_used:
                        quant_used[product] = assign_quantity
                    else:    
                        quant_used[product] += assign_quantity
                    
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
        # Update order to ready / pending status:
        # ---------------------------------------------------------------------
        # TODO line_pool.logistic_check_ready_order(sale_line_ready)        
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

        # Update only pending order with uncovworkflow_ered lines
        lines = self.search([
            # Filter logistic state:
            ('order_id.logistic_state', '=', 'pending'),
            
            # Filter line state:
            ('logistic_state', '=', 'uncovered'),

            # Not select lavoration line:
            ('mrp_state', '=', False),
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
        #                 Check if order are present:
        # ---------------------------------------------------------------------
        purchase_pending = {}
        for purchase in purchase_pool.search([
                ('logistic_state', '=', 'draft'),
                ]):
            supplier_id = purchase.partner_id.id
            if supplier_id not in purchase_pending:
                purchase_pending[supplier_id] = purchase # link order

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
            # Lavoration order
            # -----------------------------------------------------------------
            if supplier == company.partner_id:
                for line in purchase_db[supplier]:
                    line.mrp_state = 'draft'
                continue

            # -----------------------------------------------------------------
            # Create header:
            # -----------------------------------------------------------------            
            partner = supplier or company.partner_id # Use company 
            # TODO if order was deleted restore logistic_state to uncovered

            if partner.id in purchase_pending:
                purchase = purchase_pending[partner.id]
            else:    
                purchase = purchase_pool.create({
                    'partner_id': partner.id,
                    'date_order': now,
                    'date_planned': now,
                    #'name': # TODO counter?
                    #'partner_ref': '',
                    #'logistic_state': 'draft',
                    })
                # TODO create if theres' some purchase.order.line?
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
        # ---------------------------------------------------------------------
        # ---------------------------------------------------------------------
        
        # Return view:
        return purchase_pool.return_purchase_order_list_view(selected_ids)

    # -------------------------------------------------------------------------
    #                            COMPUTE FIELDS FUNCTION:
    # -------------------------------------------------------------------------
    @api.multi
    @api.depends('assigned_line_ids', 'purchase_line_ids', 'load_line_ids',
        'delivered_line_ids', 'mrp_state')
    def _get_logistic_status_field(self):
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
                line.logistic_position = '' # TODO explode component?
            else:
                # -------------------------------------------------------------
                #                       NORMAL PRODUCT:
                # -------------------------------------------------------------
                #state = 'draft'
                product = line.product_id
                logistic_position = ''
                
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
                    logistic_position += _('[MAG] Q. %s > %s\n') % (
                        -quant.quantity,
                        product.default_slot_id.name or ''
                        )
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
                
                if line.mrp_state in ('draft', 'progress'):
                    # Lavoration product (internal):
                    logistic_purchase_qty = logistic_order_qty
                else:
                    # Purchase product:
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
                if line.mrp_state == 'done':
                    # Lavoration product (internal):
                    logistic_received_qty = logistic_order_qty
                    logistic_position += _('[PROD] Q. %s > %s\n') % (
                        logistic_order_qty,
                        '',
                        )
                else:
                    # Purchase product:
                    for move in line.load_line_ids:
                        logistic_received_qty += move.product_uom_qty # TODO verify
                        logistic_position += _('[TAV] Q. %s > %s\n') % (
                            move.product_uom_qty,
                            move.slot_id.name or ''
                            )
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
                    logistic_delivered_qty += move.product_uom_qty #TODO verify
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
                line.logistic_position = logistic_position

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
        readonly=True, compute='_get_logistic_status_field', multi=True,
        store=False,
        )
    logistic_uncovered_qty = fields.Float(
        'Uncovered qty', digits=dp.get_precision('Product Price'),
        help='Qty not covered with internal stock (so to be purchased)',
        readonly=True, compute='_get_logistic_status_field', multi=True,
        store=False,
        )
    logistic_purchase_qty = fields.Float(
        'Purchase qty', digits=dp.get_precision('Product Price'),
        help='Qty order to supplier',
        readonly=True, compute='_get_logistic_status_field', multi=True,
        store=False,
        )
    logistic_received_qty = fields.Float(
        'Received qty', digits=dp.get_precision('Product Price'),
        help='Qty received with pick in delivery',
        readonly=True, compute='_get_logistic_status_field', multi=True,
        store=False,
        )
    logistic_remain_qty = fields.Float(
        'Remain qty', digits=dp.get_precision('Product Price'),
        help='Qty remain to receive to complete ordered',
        readonly=True, compute='_get_logistic_status_field', multi=True,
        store=False,
        )
    logistic_delivered_qty = fields.Float(
        'Delivered qty', digits=dp.get_precision('Product Price'),
        help='Qty deliverer  to final customer',
        readonly=True, compute='_get_logistic_status_field', multi=True,
        store=False,
        )
    logistic_undelivered_qty = fields.Float(
        'Not delivered qty', digits=dp.get_precision('Product Price'),
        help='Qty not deliverer to final customer',
        readonly=True, compute='_get_logistic_status_field', multi=True,
        store=False,
        )
    
    # Position:
    logistic_position = fields.Text(
        'Position', help='Stock position',
        readonly=True, compute='_get_logistic_status_field', multi=True,
        store=False,
        )

    # MRP state:
    mrp_state = fields.Selection([
        ('draft', 'Internal lavoration'),
        ('progress', 'In progress'),
        ('done', 'Done'),
        ], 'Lavoration state',
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
        #compute='_get_logistic_status_field', multi=True,
        #store=True, # TODO store True # for create columns
        )
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
