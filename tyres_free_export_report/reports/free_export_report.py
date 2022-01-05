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
import pdb
import sys
import logging
from odoo import fields, api, models, exceptions
from odoo import tools
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    """ Stock picking extract
    """
    _inherit = 'sale.order'

    @api.multi
    def qweb_get_invoice_text(self, ):
        """ Get partner extra info data (for address print)
            self: res.partner obj
        """
        self.ensure_one()
        try:
            picking = self.logistic_picking_ids[0]
            invoice_number = picking.invoice_number
            if not picking.invoice_number:
                raise exceptions.Warning(_('Invoice number not yet present!'))
            if invoice_number == 'DA ASSEGNARE':
                invoice_number = self.name  # Use order number not invoice!

            return '''
                n. %s del %s intestata a %s 
                destinazione %s %s''' % (
                    invoice_number,
                    picking.invoice_date[:10],
                    self.partner_invoice_id.name,

                    self.partner_shipping_id.city.upper(),
                    self.partner_shipping_id.country_id.name.upper(),
                    )

        except:
            raise exceptions.Warning(_('Invoice not present!'))

    @api.multi
    def get_report_footer_stamp(self, ):
        """ Get partner extra info data (for address print)
            self: res.partner obj
        """
        self.ensure_one()
        company = self.company_id

        text = u'''%s
            %s%s
            %s - %s (%s)
            %s - Tel. %s
            Cod. Fisc. e P.I. %s
            ''' % (
                (company.name or '').upper(),

                company.street or '',
                company.street2 or '',

                company.zip or '',
                company.city or '',
                company.state_id.name if company.state_id else '',

                (company.country_id.name if company.country_id else ''
                 ).upper(),
                company.phone or '',

                company.vat or '',
                )
        return text.split('\n')

    @api.multi
    def get_report_header_company(self, ):
        """ Get partner extra info data (for address print)
            self: res.partner obj
        """
        self.ensure_one()
        company = self.company_id
        return u'''
            COMMERCIO INGROSSO E DETTAGLIO PNEUMATICI E CERCHI
            Sede Legale e Amministrativa:
            %s%s
            %s - %s (%s)
            Email: %s
            Cod. Fisc. e P.I. %s
            CAPITALE SOCIALE i.v. € %s
            ''' % (
                company.street or '',
                company.street2 or '',

                company.zip or '',
                company.city or '',
                company.state_id.name if company.state_id else '',

                company.email or '',
                company.phone or '',
                company.vat or '',
                )

    @api.multi
    def get_brand_document(self, ):
        """ Get brand document part
        """
        self.ensure_one()
        order = self
        pdb.set_trace()
        result = {}
        for line in order.order_line:
            brand = line.product_id.brand
            if not brand:
                _logger.error('Line without brand (Extra report)')
                continue
            if brand not in result:
                result[brand] = []
            result[brand].append(line)
        return result

    @api.multi
    def get_brand_detail(self, brand):
        """ Get brand document part
        """
        self.ensure_one()
        return '{}, {} {} - {} [{}]'.format(
            brand.name.upper(),
            brand.owner or '',
            brand.street or '',
            brand.zipcode or '',
            brand.country_id.name or '',
        )


