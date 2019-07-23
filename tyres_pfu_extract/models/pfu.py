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
    partner_id = fields.Many2one('res.partner', 'Supplier')
    from_date = fields.Date('From date', required=True)
    to_date = fields.Date('To date', required=True)
    # -------------------------------------------------------------------------    

    @api.multi
    def extract_excel_pfu_report(self, ):
        ''' Extract Excel PFU report
        '''
        move_pool = self.env['stock.move']
        excel_pool = self.env['excel.writer']
        
        from_date = self.from_date
        to_date = self.to_date
        partner_id = self.partner_id.id
        
        moves = move_pool.search([
            # Date filter:
            ('picking_id.scheduled_date', '>=', from_date),
            ('picking_id.scheduled_date', '<=', to_date),

            # Selection filter:
            ('logistic_unload_id', '!=', False), # Linked to Sale line
            ('product_id.mmac_pfu', '!=', False), # PFU category present
            ])
            
        supplier_moves = {}    
        for move in moves:   
            # TODO is invoice filter???  is_invoiced?!?
            product_uom_qty = move.product_uom_qty
            sale_line = move.logistic_unload_id
            customer = sale_line.order_id.partner_id
            fiscal_position = customer.property_account_position_id

            if not fiscal_position.is_pfu:
                continue # Jump movement not PFU report
            
            for load in sale_line.load_line_ids:
                supplier = load.picking_id.partner_id
                if partner_id and supplier_id.id != partner_id:
                    continue
                    
                if supplier not in supplier_moves:
                    supplier_moves[supplier] = []
                supplier_moves[partner].append(load) # load movement
                
                # TODO check no extra quantity!!!
        
        if not supplier_moves:
            _logger.error('No moves to write file')
            return False
            
        # ---------------------------------------------------------------------
        #                          EXTRACT EXCEL:
        # ---------------------------------------------------------------------
        # Excel file configuration:
        header = ('RAEE', 'Cod. Articolo', 'Descrizione', u'Q.tà', 
            'Doc Fornitore', 'Data Doc.', 'N. Fattura', 'N. Nostra fattura', 
            'Data Doc.', 'ISO stato')
            
        column_width = (
            5, 15, 25, 5, 
            5, 6, 10, 10, 
            6, 6,
            )    
        
        format_text = False # Setup first page
        for supplier in supplier_moves:
        
            # Readability:
            supplier_name = supplier.name

            # -----------------------------------------------------------------
            # Header setup:
            # -----------------------------------------------------------------
            ws_name = supplier_name
            excel_pool.create_worksheet(ws_name)
            if not format_text:
                excel_pool.set_format()
                format_text = {                
                    'title': excel_pool.get_format('title'),
                    'header': excel_pool.get_format('header'),
                    'text': excel_pool.get_format('text'),
                    'number': excel_pool.get_format('number'),
                    }            
            excel_pool.columns_width(ws_name, column_width)
            
            # -----------------------------------------------------------------
            # Header write:
            # -----------------------------------------------------------------
            row = 0
            excel_pool.write_xls_line(ws_name, row, [
                'Fornitore:',
                supplier.sql_supplier_code,
                supplier_name,
                '',
                'Dalla data: %s' % from_date,
                'Alla data: %s' % to_date,
                ], default_format=format_text['title'])
                
            row += 2    
            excel_pool.write_xls_line(ws_name, row, header, 
                default_format=format_text['header'])
            
            # -----------------------------------------------------------------
            # Write detail:
            # -----------------------------------------------------------------            
            total = 0
            subtotal = 0
            last = False # Break level PFU code
            for move in sorted(supplier_moves[supplier], key=lambda m: (
                    m.product_id.mmac_pfu.name, m.date)):                    
                row += 1
                
                # Readability:
                product = move.product_id
                pfu = product.mmac_pfu
                qty = move.product_uom_qty

                if last != pfu:
                    if last != False:
                        excel_pool.write_xls_line(ws_name, row, (
                            subtotal,
                            ), default_format=format_text['number'], col=3)                    
                    subtotal = 0
                    row += 1

                # Total operation:
                total += qty
                subtotal += qty
                
                # -------------------------------------------------------------
                # Write data line:
                # -------------------------------------------------------------
                excel_pool.write_xls_line(ws_name, row, (
                    product.mmac_pfu.name,
                    product.default_code,
                    product.name,
                    (qty, number), # TODO check if it's all!!
                    '', # TODO supplier document number
                    move.picking_id.scheduled_date,
                    '', # Number supplier invoice
                    '', # Our invoice
                    '', # Date doc,
                    '', # ISO country
                    ), default_format=format_text['text'])

            # -----------------------------------------------------------------
            # Write data line:
            # -----------------------------------------------------------------
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
        return excel_pool.return_attachment('Stato_righe_ordini')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
