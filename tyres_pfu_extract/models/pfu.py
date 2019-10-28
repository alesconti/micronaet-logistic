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
from odoo.addons import decimal_precision as dp
from odoo.tools.translate import _


_logger = logging.getLogger(__name__)

class AccountFiscalPosition(models.Model):
    """ Model name: AccountFiscalPosition
    """
    _inherit = 'account.fiscal.position'
    
    is_pfu = fields.Boolean('PFU refund', 
        help='If checked all sale with this position go in report')

class StockPickingPfuExtractWizard(models.TransientModel):
    """ Model name: StockPicking
    """
    _name = 'stock.picking.pfu.extract.wizard'
    _description = 'Logistic manual operation'
    
    # -------------------------------------------------------------------------
    #                            COLUMNS:
    # -------------------------------------------------------------------------    
    partner_id = fields.Many2one('res.partner', 'Supplier', required=True,
        domain="[('supplier', '=', True)]")
    from_date = fields.Date('From date', required=True)
    to_date = fields.Date('To date', required=True)
    # -------------------------------------------------------------------------    

    @api.multi
    def extract_excel_pfu_report(self, ):
        ''' Extract Excel PFU report
        '''
        move_pool = self.env['stock.move']
        order_line_pool = self.env['sale.order.line']
        excel_pool = self.env['excel.writer']
        
        from_date = self.from_date
        to_date = self.to_date
        supplier = self.partner_id
        
        domain = [
            # Header
            ('delivery_id.date', '>=', from_date),
            ('delivery_id.date', '<', to_date),
            ('delivery_id.supplier_id', '=', supplier.id),

            ('logistic_load_id', '!=', False), # Linked to order
            #('logistic_load_id.order_id.partner_invoice_id.property_account_position_id.is_pfu', '!=', False), # Linked to order
            # NOT USED: ('product_id.mmac_pfu', '!=', False), # PFU category
            ]

        # ---------------------------------------------------------------------
        #                           Collect data:
        # ---------------------------------------------------------------------
        supplier_moves = {}
        pfu_line_ids = [] # list of all sale order line (to check PFU)
        
        # ---------------------------------------------------------------------
        # A. All stock move sale
        # ---------------------------------------------------------------------
        for move in move_pool.search(domain):
            sale_line = move.logistic_load_id
            pfu_line_ids.append(sale_line.id)
            
            product_uom_qty = move.product_uom_qty
            customer = sale_line.order_id.partner_invoice_id
            fiscal_position = customer.property_account_position_id
            
            # TODO used domain filter:
            if not fiscal_position.is_pfu: # not refund!
                continue # Jump movement not PFU report

            supplier_moves.append(move)

        # ---------------------------------------------------------------------
        # B. PFU product linked
        # ---------------------------------------------------------------------
        if not supplier_moves:
            raise exceptions.Warning('No PFU movement with this selection!')

        # Search sale line linked to sold product:
        pfu_lines = order_line_pool.search([
            ('mmac_pfu_line_id', 'in', pfu_line_ids),
            #('product_id.mmac_pfu', '!=', False), # PFU category present
            ])
        pfu_products = {}
        for line in pfu_lines:
            pfu_products[line.mmac_pfu_line_id] = line # product > PFU

        # ---------------------------------------------------------------------
        #                          EXTRACT EXCEL:
        # ---------------------------------------------------------------------
        # Header setup:
        ws_name = supplier.name
        excel_pool.create_worksheet(ws_name)
        excel_pool.set_format()
        format_text = {                
            'title': excel_pool.get_format('title'),
            'header': excel_pool.get_format('header'),
            'text': excel_pool.get_format('text'),
            'number': excel_pool.get_format('number'),
            }            
        excel_pool.columns_width(ws_name, column_width)

        # Excel file configuration:
        header = ('RAEE', 'Cod. Articolo', 'Descrizione', u'Q.tà', 
            'Doc Fornitore', 'Data Doc.', 'N. Fattura', 'N. Nostra fattura', 
            'Data Doc.', 'ISO stato')
            
        column_width = (
            5, 15, 25, 5, 
            5, 6, 10, 10, 
            6, 6,
            )    

        # Header write:
        row = 0
        excel_pool.write_xls_line(ws_name, row, [
            'Fornitore:',
            supplier.sql_supplier_code,
            supplier.name,
            '',
            'Dalla data: %s' % from_date,
            'Alla data: %s' % to_date,
            ], default_format=format_text['title'])
            
        row += 2
        excel_pool.write_xls_line(ws_name, row, header, 
            default_format=format_text['header'])
        
        
        format_text = False # Setup first page
        
        # ---------------------------------------------------------------------
        # Write detail:
        # ---------------------------------------------------------------------        
        total = 0
        subtotal = 0
        last = False # Break level PFU code
        for move in sorted(supplier_moves, key=lambda m: (
                m.product_id.mmac_pfu.name, m.date)):

            # First check:
            sale_line = move.logistic_load_id                
            if sale_line not in pfu_products:
                # Line dont' have PFU linked
                continue
            
            # Readability:
            pfu_line = pfu_products[sale_line] # change in pfu move line
            product = pfu_line.product_id
            pfu = product.mmac_pfu
            qty = pfu_line.product_uom_qty # XXX use order line not move!

            if last != pfu:
                if last != False:
                    excel_pool.write_xls_line(ws_name, row, (
                        subtotal,
                        ), default_format=format_text['number'], col=3)                    
                subtotal = 0
                row += 1

            # -----------------------------------------------------------------
            #                    Excel writing:
            # -----------------------------------------------------------------
            row += 1
            # Total operation:
            total += qty
            subtotal += qty
            
            # -----------------------------------------------------------------
            # Write data line:
            # -----------------------------------------------------------------
            excel_pool.write_xls_line(ws_name, row, (
                product.mmac_pfu.name,
                product.default_code,
                product.name,
                (qty, format_text['number']), # TODO check if it's all!!
                move.delivery_id.name, # Delivery ref.
                move.delivery_id.date,
                '?', # Number supplier invoice
                '', # Our invoice
                '', # Date doc,
                '', # ISO country
                ), default_format=format_text['text'])

        # ---------------------------------------------------------------------
        # Write data line:
        # ---------------------------------------------------------------------
        if last != False:
            # Subtotal
            row += 1
            excel_pool.write_xls_line(ws_name, row, (
                subtotal,
                ), default_format=format_text['number'], col=3)

            # Total
            row += 1
            excel_pool.write_xls_line(ws_name, row, (
                'Totale:', total,
                ), default_format=format_text['number'], col=2)
            
        # ---------------------------------------------------------------------
        # Save file:
        # ---------------------------------------------------------------------
        return excel_pool.return_attachment('Report_PFU')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
