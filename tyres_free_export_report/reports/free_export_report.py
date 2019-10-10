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
from odoo import fields, api, models
from odoo import tools
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    ''' Stock picking extract
    '''
    _inherit = 'sale.order'
    
    @api.multi
    def get_report_header_company(self, ):
        ''' Get partner extra info data (for address print)
            self: res.partner obj
        '''
        self.ensure_one()
        
        return u'''
            COMMERCIO INGROSSO E DETTAGLIO PNEUMATICI E CERCHI
            Sede Legale e Amministrativa:
            %s%s
            %s - %s (%s)
            Email: %s
            Cod. Fisc. e P.I. %s
            CAPITALE SOCIALE i.v. € %s''' % (
                o.street or '',
                o.street2 or '',
                
                o.zip or '', 
                o.city or '',
                o.state_id.name if o.state_id else '',
                
                o.email or '',
                o.phone or '',
                o.vat or '',
                )

    """@api.multi
    def get_partner_extra_info(self, ):
        ''' Get partner extra info data (for address print)
            self: res.partner obj
        '''
        for o in self:
            if o:
                mask = u'''
                    COMMERCIO INGROSSO E DETTAGLIO PNEUMATICI E CERCHI
                    Sede Legale e Amministrativa:
                    %s%s
                    %s - %s (%s)
                    Email: %s
                    Cod. Fisc. e P.I. %s
                    CAPITALE SOCIALE i.v. € %s'''

                o.contact_info = mask % (
                    o.street or '',
                    o.street2 or '',
                    
                    o.zip or '', 
                    o.city or '',
                    o.state_id.name if o.state_id else '',
                    
                    o.email or '',
                    o.phone or '',
                    o.vat or '',
                    )
            else:    
                o.contact_info = ''
    
    contact_info = fields.Text('Extra info', compute='get_partner_extra_info')        
    """
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
