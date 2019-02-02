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

class StockDdtcancel(models.Model):
    """ Model name: Stock Ddt Cancel
    """
    
    _name = 'stock.ddt.cancel'
    _description = 'Stock DDT cancel'
    _rec_name = 'picking_id'
    _order = 'date'
    
    # -------------------------------------------------------------------------
    # COLUMNS:
    # -------------------------------------------------------------------------
    date = fields.Date('Date', readonly=1)
    picking_id = fields.Many2one('stock.picking', 'DDT', readonly=1)
    order_id = fields.Many2one('sale.order', 'Origin: Sale order', readonly=1)
    
    ddt_date = fields.Date('DDT Date', readonly=1)
    ddt_number = fields.Char('DDT Number', size=20, readonly=1)
    
    date = fields.Date('Date', readonly=1)
    reason = fields.Text('Reason', readonly=1)
    detail = fields.Text('Detail', widget='html', readonly=1)
    # -------------------------------------------------------------------------

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
