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
import base64
from odoo import api, models
from odoo import tools
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)


class StockPicking(models.AbstractModel):
    ''' Stock picking extract
    '''
    _inherit = 'stock.picking'
    
    @api.model
    def extract_account_ddt_report(self):
        ''' Extract PDF report
        '''
        import pdb; pdb.set_trace()
        REPORT_ID = 'logistic_account_report.action_report_ddt_lang'        
        pdf = self.env.ref(REPORT_ID).render_qweb_pdf(self.ids)
        b64_pdf = base64.b64encode(pdf[0])
        f_pdf = open('/home/thebrush/prova.pdf', 'wb')
        f_pdf.write(b64.pdf)
    
class ReportDdtLangParser(models.AbstractModel):
    ''' Load move report:
    '''
    _name = 'report.logistic_account_report.report_ddt_lang'
    
    @api.model
    def get_report_values(self, docids, data=None):
    # EX: def render_html(self, docids, data=None):
        ''' Render report parser:
        '''
        REPORT_NAME = 'logistic_account_report.report_ddt_lang'
        report_pool = self.env['ir.actions.report']
        report = report_pool._get_report_from_name(REPORT_NAME)

        picking_pool = self.env['stock.picking']    
        pickings = picking_pool.search([]) # TODO Change filter here
        
        if not pickings.exists():
             raise Warning(
                 _('No movement to print!'))
        
        docids = pickings.ids # list of IDs
        docargs = {
            'doc_ids': docids,
            'doc_model': 'stock.picking',
            'docs': pickings,
            }
        
        if not data.get('form'):
            raise UserError(
                _('Form content is missing, this report cannot be printed.'))

        return {
            'doc_ids': docids,#self.ids,
            'doc_model': picking_pool.mode,#holidays_report.model,
            'docs': pickings,
            }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
