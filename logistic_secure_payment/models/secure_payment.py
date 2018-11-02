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
from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.addons import decimal_precision as dp
from odoo.tools.translate import _


_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    """ Model name: Sale Order
    """
    
    _inherit = 'sale.order'

    # -------------------------------------------------------------------------    
    #                          COLUMNS:
    # -------------------------------------------------------------------------    
    secure_payment = fields.Boolean('Secure Payment', 
        help='If order comes from a secure market, as Amazon is secure'
        'and direct confirmed, instead need to be checked'
        )

class AccountPayment(models.Model):
    """ Model name: Account Payment
    """
    
    _inherit = 'account.payment.term'

    # -------------------------------------------------------------------------    
    #                          COLUMNS:
    # -------------------------------------------------------------------------    
    secure_payment = fields.Boolean('Secure Payment', 
        help='This payment is consider as secure, order directly confirmed'
        )

class AccountFiscalPosition(models.Model):
    """ Model name: Account Fiscal Position
    """
    
    _inherit = 'account.fiscal.position'

    # -------------------------------------------------------------------------    
    #                          COLUMNS:
    # -------------------------------------------------------------------------    
    secure_payment = fields.Boolean('Secure Payment', 
        help='This fiscal position is consider as secure, order direct confirm'
        )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
