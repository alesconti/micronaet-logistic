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

class ProductProduct(models.Model):
    """ Model name: Product Product
    """
    _inherit = 'product.product'

    # -------------------------------------------------------------------------
    #                            Button event:
    # -------------------------------------------------------------------------
    @api.multi
    def explode_kit_from_name(self):
        ''' Launche generator from template object
        '''
        return self.product_tmpl_id.explode_kit_from_name()
    

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
        import pdb; pdb.set_trace()
        # Pool used:
        template_pool = self.env['product.template']
        component_pool = self.env['product.template.kit.bom']

        # ---------------------------------------------------------------------
        # Check if is a kit syntax:
        # ---------------------------------------------------------------------
        if not self.default_code or '#' not in self.default_code:
            raise exceptions.Warning(_('No "#" char present in default code'))

        self.is_kit = True # Always update is_kit if present

        # ---------------------------------------------------------------------
        # Code in default_code of the kit:
        # ---------------------------------------------------------------------
        # Clean extra special char (\t \n ' ')
        default_code = (self.default_code or '').strip()
        code_list = default_code.split('#')

        # ---------------------------------------------------------------------
        # Search product by code (only present):
        # ---------------------------------------------------------------------
        components = self.search([('default_code', 'in', code_list)])
        template_db = {} # ID of template
        for template in components:
            template_db[template.default_code] = template.id
        
        # ---------------------------------------------------------------------
        # Generate all component extracting from default_code
        # ---------------------------------------------------------------------
        # Static fields:
        product_id = self.id
        partner_id = self.company_id.partner_id.id

        # Delete all components:        
        self.component_ids = [(5, False, False)]

        # Re-create all components:
        for default_code in code_list:
            # -----------------------------------------------------------------
            # Get template ID for component:
            # -----------------------------------------------------------------
            if default_code in template_db: 
                # Product yet present:
                template_id = template_db[default_code]
            else:
                # -------------------------------------------------------------
                # Product create as a service:
                # -------------------------------------------------------------
                template_id = template_pool.create({
                    'name': default_code,
                    'default_code': default_code,
                    'default_supplier_id': partner_id,
                    'type': 'service',
                    }).id
                _logger.warning(
                    'Create a new template as a service: %s' % default_code)
                    
            # -----------------------------------------------------------------
            # Create component in this kit:                
            # -----------------------------------------------------------------
            component_pool.create({
                'sequence': 10,
                'product_id': product_id, # parent
                'component_id': template_id, # component
                })

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
