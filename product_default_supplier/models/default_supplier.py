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

class ResPartner(models.Model):
    """ Model name: Res Partner
    """
    
    _inherit = 'res.partner'

    _sql_constraints = [(
        'product_suffix_uniq', 
        'unique(product_suffix)', 
        'Product suffix must be unique!'
        )]    
        
    # -------------------------------------------------------------------------
    # COLUMNS:
    # -------------------------------------------------------------------------
    product_suffix = fields.Char('Product suffix', size=10)
    # -------------------------------------------------------------------------

class ProductTemplate(models.Model):
    """ Model name: ProductTemplate
    """
    
    _inherit = 'product.template'
    
    # -------------------------------------------------------------------------
    #                              BUTTON:
    # -------------------------------------------------------------------------
    @api.multi
    def get_default_supplier_from_code(self):
        ''' Generate default partner from code if start with partner suffix
        '''
        if not self.default_code:
            raise exceptions.Warning(_('No default code present'))

        # Clean extra special char (\t \n ' ')
        default_code = (self.default_code or '').strip()
        # TODO Get info about current code
    
    # -------------------------------------------------------------------------
    # COLUMNS:
    # -------------------------------------------------------------------------
    default_supplier_id = fields.Many2one(
        'res.partner', 'Default supplier', domain="[('supplier', '=', True)]",
        context="{'default_supplier': True}")
    # -------------------------------------------------------------------------

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
