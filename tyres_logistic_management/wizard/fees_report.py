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

class LogisticFeesExtractWizard(models.TransientModel):
    _name = 'logistic.fees.extract.wizard'
    _description = 'Fees extract report'

    # -------------------------------------------------------------------------
    #                               BUTTON EVENT:    
    # -------------------------------------------------------------------------    
    @api.multi
    def fees_extract_button(self):
        """ Account fees report
        """
        stock_pool = self.env['stock.picking']        
        stock_pool.csv_report_extract_accounting_fees(self.evaluation_date)

    # -------------------------------------------------------------------------
    #                               COLUMNS: 
    # -------------------------------------------------------------------------    
    evaluation_date = fields.Date('Date', required=True, 
        default=fields.Datetime.now())

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
