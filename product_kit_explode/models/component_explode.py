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

class ProductTemplate(models.Model):
    """ Model name: ProductTemplate
    """
    
    _inherit = 'product.template'

    # -------------------------------------------------------------------------
    #                            Button event:
    # -------------------------------------------------------------------------
    @api.multi
    def explode_kit_from_name(self):
        ''' Explode kit product from name (raise error)
        '''
        if '#' not in self.default_code:
            raise exceptions.Warning(_('No "#" char present in default code'))

        code_list = self.default_code.split('#')
        components = self.search([('default_code', 'in', code_list)])
        if len(code_list) != len(components):
            raise exceptions.Warning(
                _('Not all code found: \nSearch: %s\nFind only: %s') % (
                    code_list,
                    list([item.default_code for item in components]),
                    ))
                    
        # Remove all:
        self.component_ids = [(5, False, False)] 
        
        # Create all record:
        component_pool = self.env['product.template.kit.bom']
        for component in components:
            component_pool.create({
                'sequence': 10,
                'product_id': self.id,
                'component_id': component.id,
                })

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
