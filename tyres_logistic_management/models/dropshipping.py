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
import odoo
import logging
from odoo import models, fields, api
from odoo.tools.translate import _


_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    """ Model name: Partner for dropshipping
    """
    
    _inherit = 'res.partner'
    
    # -------------------------------------------------------------------------
    # Columns:
    # -------------------------------------------------------------------------
    dropship_manage = fields.Boolean('Dropship manage')

class ProductTemplateSupplierStock(models.Model):
    """ Model name: ProductTemplateSupplierStock
    """
    
    _inherit = 'product.template.supplier.stock'
    
    # -------------------------------------------------------------------------
    # Columns:
    # -------------------------------------------------------------------------
    partner_dropship_manage = fields.Boolean(
        'Partner dropship', related='supplier_id.dropship_manage')    
    
class SaleOrderLinePurchase(models.Model):
    """ Model name: SaleOrderLinePurchase
    """
    
    _inherit = 'sale.order.line.purchase'

    # -------------------------------------------------------------------------
    # Button event:
    # -------------------------------------------------------------------------
    @api.multi
    def set_dropship_on(self):
        ''' Set dropship on
        '''
        self.dropship_manage = True

    @api.multi
    def set_dropship_off(self):
        ''' Set dropship off
        '''
        self.dropship_manage = False

    # -------------------------------------------------------------------------
    # Columns:
    # -------------------------------------------------------------------------
    dropship_manage = fields.Boolean('Dropship manage')
    partner_dropship_manage = fields.Boolean(
        'Partner dropship', related='supplier_id.dropship_manage')    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
