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

class StockPickingInReportWizard(models.TransientModel):
    """ Model name: Delivered in report
    """
    _name = 'stock.picking.in.report.wizard'
    _description = 'Delivered report'
    
    # -------------------------------------------------------------------------
    #                            COLUMNS:
    # -------------------------------------------------------------------------    
    supplier_id = fields.Many2one('res.partner', 'Supplier')
    from_date = fields.Date('From date >=', required=True)
    to_date = fields.Date('To date <', required=True)
    # -------------------------------------------------------------------------    

    @api.multi
    def extract_load_report(self):
        ''' Extract Excel report
        '''        
        move_pool = self.env['stock.move']
        excel_pool = self.env['excel.writer']
        
        from_date = self.from_date
        to_date = self.to_date
        supplier = self.supplier_id
        
        domain = [
            # Header
            ('create_date', '>=', from_date),
            ('create_date', '<', to_date),
            ]

        if supplier:
            domain.append(
                ('partner_id', '=', supplier.id),
                )

        # ---------------------------------------------------------------------
        #                          EXTRACT EXCEL:
        # ---------------------------------------------------------------------
        # Excel file configuration: # TODO
        header = (
            'Fornitore', 'Data', 'Documento', 'Tipo',            
            'Codice', 'Prodotto', 
            'Q.', 'Prezzo', 'Subtotal',
            )
        column_width = (
            30, 10, 20, 10,            
            15, 40, 
            10, 10, 15,
            )

        # ---------------------------------------------------------------------
        # Write detail:
        # ---------------------------------------------------------------------        
        structure = {}
        moves = move_pool.search(domain)
        for move in moves:
            if move.product_id.is_expence:
                continue

            supplier = move.partner_id
            
            if supplier not in structure:
                structure[supplier] = []
            structure[supplier].append(move)    
        
        if not structure:
            _logger.warning('Delivery not found!')
            raise exceptions.Warning(_('No document found with this filters!'))

        # -----------------------------------------------------------------
        #                   Excel sheet creation:
        # -----------------------------------------------------------------
        setup_complete = False
        for supplier in sorted(structure):
            # -----------------------------------------------------------------
            #                   Excel sheet creation:
            # -----------------------------------------------------------------
            ws_name = '%s %s' % (
                (supplier.name or 'Non presente').strip(),
                '' if not supplier else supplier.id,
                )

            excel_pool.create_worksheet(ws_name)
            excel_pool.column_width(ws_name, column_width)
            if not setup_complete: # First page only:
                setup_complete = True
                excel_pool.set_format()
                format_text = {                
                    'title': excel_pool.get_format('title'),
                    'header': excel_pool.get_format('header'),
                    'white': {
                        'text': excel_pool.get_format('text'),
                        'number': excel_pool.get_format('number'),
                        },
                    'red': {
                        'text': excel_pool.get_format('bg_normal_red'),
                        'number': excel_pool.get_format(
                            'bg_normal_red_number'),                        
                        },
                    'green': {
                        'text': excel_pool.get_format('bg_green'),
                        'number': excel_pool.get_format(
                            'bg_green_number'),                        
                        },
                    }

            # -----------------------------------------------------------------
            # Header of sheet:
            # -----------------------------------------------------------------
            row = 0
            excel_pool.write_xls_line(ws_name, row, [
                u'Fornitore: %s, Data [%s, %s]' % (
                    supplier.name or 'Tutti',
                    from_date,
                    to_date,
                    )
                ], default_format=format_text['title'])
                
            row += 2
            excel_pool.write_xls_line(ws_name, row, header, 
                default_format=format_text['header'])

            total = {
                'subtotal': 0.0,                
                'quantity': 0.0,                
                }            
            for line in sorted(structure[supplier], 
                    key=lambda x: x.create_date):
                row += 1
                partner = line.partner_id   
                product = line.product_id             
                logistic_purchase = line.logistic_purchase_id
                logistic_load = line.logistic_load_id
                order = logistic_load.order_id
                
                # -------------------------------------------------------------
                # Total:    
                # -------------------------------------------------------------
                product_uom_qty = move.product_uom_qty
                price_unit = move.price_unit
                subtotal = product_uom_qty * price_unit
                total['subtotal'] += subtotal
                total['quantity'] += product_uom_qty
                
                if subtotal > 0.0:
                    format_color = format_text['white']
                else:    
                    format_color = format_text['red']

                excel_pool.write_xls_line(ws_name, row, [
                    partner.name,
                    move.create_date[:10],
                    order.name,
                    order.logistic_source,
                    product.default_code,
                    product.name_extended,
                    (product_uom_qty, format_color['number']),
                    (price_unit, format_color['number']),
                    (subtotal,  format_color['number']),
                    ], default_format=format_color['text'])
                    
            # -----------------------------------------------------------------
            # Write data line:
            # -----------------------------------------------------------------
            # Total
            row += 1
            excel_pool.write_xls_line(ws_name, row, (
                u'Totale:', 
                total['quantity'],
                '/',
                total['subtotal'],
                ), default_format=format_text['green']['number'], col=5)
                    
        _logger.warning('Supplier found: %s [Moves: %s]' % (
            len(structure),
            len(moves),
            ))
        # ---------------------------------------------------------------------
        # Save file:
        # ---------------------------------------------------------------------
        return excel_pool.return_attachment('Report_Corrieri')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
