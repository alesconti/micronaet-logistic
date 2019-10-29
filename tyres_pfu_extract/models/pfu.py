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
        #order_line_pool = self.env['sale.order.line']
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
            ('logistic_load_id.order_id.partner_invoice_id.property_account_position_id.is_pfu', '=', True), # Linked to order
            ]

        # ---------------------------------------------------------------------
        #                           Collect data:
        # ---------------------------------------------------------------------
        # A. All stock move sale
        category_move = {}
        for move in move_pool.search(domain):            
            category = move.product_id.mmac_pfu.name or ''
            if category not in category_move:
                category_move[category] = []
            category_move[category].append(move)

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

        # Excel file configuration:
        header = ('RAEE', 'Cod. Articolo', 'Descrizione', u'Q.tà', 
            'Doc Fornitore', 'Data Doc.', 'N. Fattura', 'N. Nostra fattura', 
            'Data Doc.', 'ISO stato')
            
        column_width = (
            5, 15, 35, 5, 
            15, 10, 10, 15, 
            10, 8,
            )    
        excel_pool.column_width(ws_name, column_width)

        # Header write:
        row = 0
        excel_pool.write_xls_line(ws_name, row, [
            u'Fornitore:',
            u'',
            supplier.sql_supplier_code or '',
            supplier.name or '',
            u'',
            u'Dalla data: %s' % from_date,
            u'',
            u'Alla data: %s' % to_date,
            ], default_format=format_text['title'])
            
        row += 2
        excel_pool.write_xls_line(ws_name, row, header, 
            default_format=format_text['header'])
        
        # ---------------------------------------------------------------------
        # Write detail:
        # ---------------------------------------------------------------------        
        total = 0
        for category in sorted(category_move):
            subtotal = 0
            for move in sorted(category_move[category],
                    key=lambda x: x.date):
                row += 1

                # Readability:
                order = move.logistic_load_id.order_id
                partner = order.partner_invoice_id
                product = move.product_id
                qty = move.product_uom_qty # Delivered qty
                
                # Get invoice reference:
                try:
                    invoice = order.logistic_picking_ids[0]
                    invoice_date = invoice.invoice_date or ''
                    invoice_number = invoice.invoice_number or '?'
                except:
                    _logger.error('No invoice for order %s' % order.name)
                    invoice_date = ''
                    invoice_number = '?'
                    
                # TODO check more than one error

                # -------------------------------------------------------------
                #                    Excel writing:
                # -------------------------------------------------------------
                # Total operation:
                total += qty
                subtotal += qty
                
                # -------------------------------------------------------------
                # Write data line:
                # -------------------------------------------------------------
                excel_pool.write_xls_line(ws_name, row, (
                    category, #product.mmac_pfu.name,
                    product.default_code,
                    product.name,
                    (qty, format_text['number']), # TODO check if it's all!!
                    move.delivery_id.name, # Delivery ref.
                    move.delivery_id.date,
                    '', # Number supplier invoice
                    invoice_number, # Our invoice
                    invoice_date[:10], # Date doc,
                    partner.country_id.code or '??', # ISO country
                    #order.partner_invoice_id.property_account_position_id.name, # TODO remove
                    ), default_format=format_text['text'])
            row += 1
            excel_pool.write_xls_line(ws_name, row, (
                subtotal,
                ), default_format=format_text['number'], col=3)                    

        # ---------------------------------------------------------------------
        # Write data line:
        # ---------------------------------------------------------------------
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
