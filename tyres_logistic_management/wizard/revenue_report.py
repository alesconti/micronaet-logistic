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

class LogisticRevenueReportWizard(models.TransientModel):
    ''' Report wizard for revenue stats for period
    '''
    _name = 'logistic.revenue.report.wizard'
    _description = 'Revenue report'

    # -------------------------------------------------------------------------
    #                               BUTTON EVENT:    
    # -------------------------------------------------------------------------    
    @api.multi
    def revenue_report_button(self):
        """ Account fees report
        """
        picking_pool = self.env['stock.picking'] 
        excel_pool = self.env['excel.writer']

        filename = 'statistiche_vendita'

        # ---------------------------------------------------------------------
        # Delivery data:
        # ---------------------------------------------------------------------
        from_date = self.from_date
        to_date = self.to_date
        fiscal = self.fiscal_id
        team = self.team_id
        mode = self.mode

        domain = [
            ('sale_order_id', '!=', False), # Linked to order
            ('sale_order_id.logistic_source', '!=', 'internal'), # No internal
            
            ('scheduled_date', '>=', from_date),
            ('scheduled_date', '<', to_date),
            ]

        title = 'Statistiche consegne del periodo: [%s - %s], ' % (
            from_date, to_date)
        title += 'esclusi ordini interni' 
            
        if fiscal:
            domain.append(
                ('sale_order_id.fiscal_position_id', '=', fiscal.id),
                )    
            title += ', posizione fiscale: %s' % fiscal.name,
        else:    
            title += ', posizione fiscale: Tutte'

        if team:
            domain.append(
                ('sale_order_id.team_id', '=', team.id),
                )    
            title += ', Team: %s' % team.name,
        else:    
            title += ', Team: Tutti'

        if mode:
            domain.append(
                ('sale_order_id.team_id.team_code_ref', '=', mode.id),
                )    
            title += ', Mercato: %s' % mode,
        else:    
            title += ', Mercato: Tutti'
            
        picking_data = picking_pool.search(domain)
        
        
        # ---------------------------------------------------------------------
        #                               EXCEL:
        # ---------------------------------------------------------------------
        ws_name = 'Statistiche consegne'
        excel_pool.create_worksheet(ws_name)

        excel_pool.set_format()
        format_text = {                
            'title': excel_pool.get_format('title'),
            'header': excel_pool.get_format('header'),
            'text': excel_pool.get_format('text'),
            'number': excel_pool.get_format('number'),
            'total': excel_pool.get_format('text_total'),

            'red': excel_pool.get_format('text_red'),
            }

        header = [
            'Cliente',
            'Rif.', # Fattura o consegna
            'Data',   
            'Ordine',
            'Tipo',
            'Picking',
            'Posizione fiscale',
            'Team',
            'Mercato',
            
            'Codice',
            'Nome',
            'Q.',
            'Prezzo un.',
            'Subtotal',
            ]

        width = [
            30, 15, 15, 17, 10, 10, 18, 12, 7,
            15, 40, 5, 10, 10,
            ]    

        excel_pool.column_width(ws_name, width)

        row = 0
        excel_pool.write_xls_line(ws_name, row, [
            title,
            ], default_format=format_text['title'])

        row += 2
        excel_pool.write_xls_line(ws_name, row, header,             
            default_format=format_text['header'])            

        total = 0.0
        for picking in sorted(picking_data, key=lambda x: x.partner_id.name):
            order = picking.sale_order_id
            partner = order.partner_invoice_id   
            header = [
                partner.name,
                picking.invoice_number or 'Non presente',
                picking.scheduled_date,
                order.name,
                order.logistic_source,                
                picking.name,
                order.fiscal_position_id.name or '?',
                order.team_id.name,
                order.team_id.team_code_ref,
                ]
            
            # -----------------------------------------------------------------
            # Row linked to customer order:    
            # -----------------------------------------------------------------
            internal = ''
            for move in picking.move_lines:                
                row += 1
                
                # Header:
                excel_pool.write_xls_line(ws_name, row, header,             
                    default_format=format_text['text'])
                    
                # Moves: 
                #sale_line = move.sale_line_id # TODO
                subtotal = 0.0 #sale_line.product_uom_qty * sale_line.price_unit
                total += subtotal

                # TODO remove VAT!!!
                line = [
                    move.default_code,
                    move.name_extended,
                    # TODO change:
                    (move.product_uom_qty, format_text['number']),
                    (move.price_unit, format_text['number']),
                    (subtotal, format_text['number']),
                    ]
                excel_pool.write_xls_line(ws_name, row, line,             
                    default_format=format_text['text'], col=9)
            
        row += 1
        # Write formatted with color        
        excel_pool.write_xls_line(ws_name, row, [
            'Totale', 
            (total, format_text['number']),
            ], default_format=format_text['text'], col=12)        
        return excel_pool.return_attachment(filename)

    # -------------------------------------------------------------------------
    #                               COLUMNS: 
    # -------------------------------------------------------------------------    
    from_date = fields.Date('From date >=', required=True)
    to_date = fields.Date('To date <', required=True)
    
    fiscal_id = fields.Many2one('account.fiscal.position', 'Fiscal position')
    team_id = fields.Many2one('crm.team', 'Team')
    
    mode = fields.Selection([
        ('b2b', 'B2B'),
        ('b2c', 'B2C'),
        ], 'Mode')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
