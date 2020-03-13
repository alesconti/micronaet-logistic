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
    from_date = fields.Date('From date >=')
    to_date = fields.Date('To date <')
    from_print_date = fields.Date('From print date >=')
    to_print_date = fields.Date('To print date <')
    only_shippy = fields.Boolean('Shippy only', default=True)
    # -------------------------------------------------------------------------

    @api.multi
    def extract_excel_report(self, ):
        """ Extract Excel report
        """
        line_pool = self.env['sale.order.line']
        excel_pool = self.env['excel.writer']

        from_date = self.from_date
        to_date = self.to_date
        from_print_date = self.from_print_date
        to_print_date = self.to_print_date
        carrier = self.carrier_id
        mode = self.mode_id
        only_shippy = self.only_shippy

        domain = [
            # Header
            ('order_id.logistic_state', '>=', 'done'),  # only done order
            ]

        if from_date:
            domain.append(('order_id.date_order', '>=', from_date))
        if to_date:
            domain.append(('order_id.date_order', '<', to_date))

        if from_print_date:
            domain.append(
                ('order_id.mmac_shippy_print_labels_date', '>=',
                    from_print_date))
        if to_print_date:
            domain.append(
                ('order_id.mmac_shippy_print_labels_date', '<',
                    to_print_date))

        if carrier:
            domain.append(
                ('order_id.carrier_supplier_id', '=', carrier.id),
                )
        if mode:
            domain.append(
                ('order_id.carrier_mode_id', '=', mode.id),
                )
        if only_shippy:
            domain.append(
                ('order_id.carrier_shippy', '=', True),
                )

        # ---------------------------------------------------------------------
        #                          EXTRACT EXCEL:
        # ---------------------------------------------------------------------
        # Excel file configuration: # TODO
        header = (
            'Modo', 'Data', 'Ordine', 'Destinazione',
            'Track ID', 'Shippy', 'Stampa',
            'Peso', 'Colli', 'Costo',

            'Q.', 'Prodotto',
            )
        column_width = (
            16, 10, 20, 55,
            15, 5, 15,
            6, 6, 6,

            6, 65,
            )

        # ---------------------------------------------------------------------
        # Write detail:
        # ---------------------------------------------------------------------
        structure = {}
        lines = line_pool.search(domain)
        for line in lines:
            if line.product_id.is_expence:
                continue

            order = line.order_id
            supplier = order.carrier_supplier_id

            if supplier not in structure:
                structure[supplier] = {}
            if order not in structure[supplier]:
                structure[supplier][order] = []
            structure[supplier][order].append(line)

        if not structure:
            _logger.warning('Order not found!')
            raise exceptions.Warning(_('No order found with this filters!'))
            return True

        # -----------------------------------------------------------------
        #                   Excel sheet creation:
        # -----------------------------------------------------------------
        setup_complete = False
        for supplier in sorted(structure):
            # -----------------------------------------------------------------
            #                   Excel sheet creation:
            # -----------------------------------------------------------------
            ws_name = (supplier.name or 'Non presente').strip()

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
                u'Corriere: %s, Modo: %s, Data [%s, %s] %s' % (
                    carrier.name or 'Tutti',
                    mode.name or 'Tutti',
                    from_date,
                    to_date,
                    'Solo Shippy' if only_shippy else '',
                    )
                ], default_format=format_text['title'])

            row += 2
            excel_pool.write_xls_line(ws_name, row, header,
                default_format=format_text['header'])

            total = {
                'weight': 0.0,
                'parcel': 0.0,
                'cost': 0.0,
                'qty': 0.0,
                }
            for order in sorted(structure[supplier],
                    key=lambda x: (
                        x.carrier_mode_id.name or '',
                        x.date_order or '',
                        )):
                row += 1
                partner = order.partner_shipping_id

                if order.carrier_shippy:
                    parcel = len(order.parcel_ids)
                    weight = sum([item.weight for item in order.parcel_ids])
                else:
                    parcel = order.carrier_manual_parcel
                    weight = order.carrier_manual_weight

                # -------------------------------------------------------------
                # Total:
                # -------------------------------------------------------------
                total['weight'] += weight
                total['parcel'] += parcel
                total['cost'] += order.carrier_cost

                if order.carrier_cost > 0.0:
                    format_color = format_text['white']
                else:
                    format_color = format_text['red']

                order_header = (
                    #order.carrier_supplier_id.name,
                    order.carrier_mode_id.name,
                    order.date_order[:10],
                    order.name,
                    u'%s [%s - %s]' % (
                        partner.name,
                        partner.city or '/',
                        partner.country_id.name or '/',
                        ),

                    order.carrier_track_id,
                    'X' if order.carrier_shippy else '',
                    order.mmac_shippy_print_labels_date,
                    (weight, format_color['number']),
                    (parcel, format_color['number']),
                    (order.carrier_cost, format_color['number']),
                    )
                excel_pool.write_xls_line(ws_name, row, order_header,
                    default_format=format_color['text'])

                first = True
                col = len(order_header)
                for line in structure[supplier][order]:
                    row += 1

                    # Readability:
                    product = line.product_id
                    qty = line.product_uom_qty # Delivered qty
                    total['qty'] += qty

                    # ---------------------------------------------------------
                    # Write data line:
                    # ---------------------------------------------------------
                    if first:
                        first = False # Write in same line
                        row -= 1
                    else:
                        excel_pool.write_xls_line(ws_name, row, (
                            '', '', '', '', '', '', '', '', '', # XXX
                            ), default_format=format_text['white']['text'])

                    excel_pool.write_xls_line(ws_name, row, (
                            (qty, format_text['white']['number']),
                            product.name_extended,
                        ),
                        default_format=format_text['white']['text'],
                        col=col)

            # -----------------------------------------------------------------
            # Write data line:
            # -----------------------------------------------------------------
            # Total
            row += 1
            excel_pool.write_xls_line(ws_name, row, (
                u'Totale:',
                total['weight'],
                total['parcel'],
                total['cost'],
                total['qty'],
                ), default_format=format_text['green']['number'], col=col - 4)

        _logger.warning('Supplier found: %s [Lines: %s]' % (
            len(structure),
            len(lines),
            ))
        # ---------------------------------------------------------------------
        # Save file:
        # ---------------------------------------------------------------------
        return excel_pool.return_attachment('Report_Corrieri')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
