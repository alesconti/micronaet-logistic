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
from odoo import api, models
from odoo import tools
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)


class StockPicking(models.AbstractModel):
    ''' Stock picking extract
    '''
    _inherit = 'stock.picking'

    # TODO create fields for write DDT / Invoice lines:

    # -------------------------------------------------------------------------
    # Default path (to be overrided)
    # -------------------------------------------------------------------------
    @api.multi
    def get_default_folder_xml_invoice(self):
        '''
        '''
        path = os.path.expanduser('~/Account/Invoice/XML')
        os.system('mkdir -p %s' % path)
        return path

    # -------------------------------------------------------------------------
    # Electronic Invoice extract:
    # -------------------------------------------------------------------------
    @api.multi
    def extract_account_electronic_invoice(self):
        ''' Extract electronic invoice (or interchange file)
        '''
        # TODO
        # ---------------------------------------------------------------------
        # Generate filename for invoice:
        # ---------------------------------------------------------------------
        path = self.get_default_folder_xml_invoice()

        # XXX Note: ERROR external field not declared here:
        filename = (
            '%s.xml' % (self.invoice_number or 'no_number')).replace('/', '_')
        fullname = os.path.join(path, filename)
        f_invoice = open(fullname, 'w')
        
        # ---------------------------------------------------------------------
        # Header part:
        # ---------------------------------------------------------------------
        f_invoice.write('''<?xml version="1.0" encoding="UTF-8"?>
<p:FatturaElettronica versione="FPR12" 
   xmlns:ds="http://www.w3.org/2000/09/xmldsig#" 
xmlns:p="http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2" 
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
xsi:schemaLocation="http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2 http://www.fatturapa.gov.it/export/fatturazione/sdi/fatturapa/v1.2/Schema_del_file_xml_FatturaPA_versione_1.2.xsd">
\n''')

        f_invoice.write('<FatturaElettronicaHeader>\n')
        
        f_invoice.write(' <DatiTrasmissione>\n')
        f_invoice.write(' </DatiTrasmissione>\n')

        f_invoice.write(' <CedentePrestatore>\n')
        f_invoice.write(' </CedentePrestatore>\n')
        
        f_invoice.write('</FatturaElettronicaHeader>\n')

        f_invoice.write('<FatturaElettronicaBody>\n')
        
        f_invoice.write(' <DatiGenerali>\n')
        f_invoice.write(' </DatiGenerali>\n')

        # ---------------------------------------------------------------------
        # Body part:
        # ---------------------------------------------------------------------
        #for line in self.order_lines:
        #    pass
        f_invoice.write('</FatturaElettronicaBody>\n')
        f_invoice.write('</p:FatturaElettronica>\n')
        
        f_invoice.close()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
