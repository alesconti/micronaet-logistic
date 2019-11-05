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

class SaleOrderCarrierCheckWizard(models.TransientModel):
    """ Model name: Order carrier check
    """
    _name = 'sale.order.carrier.check.wizard'
    _description = 'Carrier check wizard'
    
    # -------------------------------------------------------------------------
    #                            COLUMNS:
    # -------------------------------------------------------------------------    
    carrier_id = fields.Many2one('carrier.supplier', 'Carrier Supplier')
    mode_id = fields.Many2one('carrier.supplier.mode', 'Mode')
    from_date = fields.Date('From date >=', required=True)
    to_date = fields.Date('To date <', required=True)
    only_shippy = fields.Boolean('Shippy only', default=True)
    # -------------------------------------------------------------------------    

    @api.multi
    def extract_excel_report(self, ):
        ''' Extract Excel report
        '''
        line_pool = self.env['sale.order.line']
        excel_pool = self.env['excel.writer']
        
        from_date = self.from_date
        to_date = self.to_date
        carrier = self.carrier_id
        mode = self.mode_id
        
        domain = [
            # Header
            ('order_id.date_order', '>=', from_date),
            ('order_id.date_order', '>=', to_date),
            ('order_id.logistic_state', '>=', 'done'), # only done order
            ]

        if carrier:
            domain.append(
                ('order.carrier_supplier_id', '=', carrier.id),
                )
        if mode:
            domain.append(
                ('order.carrier_mode_id', '=', mode.id),
                )
        if only_shippy:
            domain.append(
                ('order.carrier_shippy', '=', True),
                )

        # ---------------------------------------------------------------------
        #                          EXTRACT EXCEL:
        # ---------------------------------------------------------------------
        # Excel file configuration: # TODO
        header = (
            'Corriere', 'Modo', 'Data', 'Ordine', 'Destinazione',
            'Colli', 'Track ID',
            'Q.', 'Prodotto',
            )
        column_width = (
            15, 10, 10, 15, 35,
            5, 10, 
            6, 30,
            )

        # ---------------------------------------------------------------------
        # Write detail:
        # ---------------------------------------------------------------------        
        orders = {}
        for line in line_pool.search(domain):
            order = line.order_id
            if order not in orders:
                orders[order] = []
            orders[order].append(line)    
        
        setup_complete = False
        for order in sorted(orders, 
                key=lambda o: (
                    o.carrier_supplier_id.name,
                    o.carrier_mode_id.name,
                    o.date_order,
                    )):
            ws_name = 'Consegne' #supplier.name.strip()
            
            # -----------------------------------------------------------------
            # Excel sheet creation:
            # -----------------------------------------------------------------
            excel_pool.create_worksheet(ws_name)
            excel_pool.column_width(ws_name, column_width)
            if not setup_complete: # First page only:
                setup_complete = True
                excel_pool.set_format()
                format_text = {                
                    'title': excel_pool.get_format('title'),
                    'header': excel_pool.get_format('header'),
                    'text': excel_pool.get_format('text'),
                    'number': excel_pool.get_format('number'),
                    }
                
            # Header write:
            row = 0
            order = line.order_id
            partner = order.partner_shipping_id
            
            excel_pool.write_xls_line(ws_name, row, [
                u'Corriere: %s, Modo: %s, Data [%s, %s] %s' % (
                    order.carrier_supplier_id.name,
                    order.carrier_mode_id.name,                    
                    from_date,
                    to_date,
                    'Solo Shippy' if only_shippy else '',
                ], default_format=format_text['title'])
                
            row += 2
            excel_pool.write_xls_line(ws_name, row, header, 
                default_format=format_text['header'])
                
            total = 0
            row += 1
            excel_pool.write_xls_line(ws_name, row, (
                order.carrier_supplier_id.name,
                order.carrier_mode_id.name,
                order.date_order,
                order.name
                partner.name,

                len(order.parcel_ids),
                order.carrier_track_id,
                ), default_format=format_text['text'])
            for line in orders[order]:
                # Readability:
                product = move.product_id
                qty = move.product_uom_qty # Delivered qty                
                total += qty
                
                # ---------------------------------------------------------
                # Write data line:
                # ---------------------------------------------------------
                excel_pool.write_xls_line(ws_name, row, (                
                    (qty, format_text['number']), # TODO check if it's all!
                    product.name_extended,
                    ), default_format=format_text['text'], col=7)
                row += 1

            # -----------------------------------------------------------------
            # Write data line:
            # -----------------------------------------------------------------
            # Total
            #row += 1
            excel_pool.write_xls_line(ws_name, row, (
                'Totale:', total,
                ), default_format=format_text['number'], col=7)
                
        # ---------------------------------------------------------------------
        # Save file:
        # ---------------------------------------------------------------------
        return excel_pool.return_attachment('Report_Corrieri')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
