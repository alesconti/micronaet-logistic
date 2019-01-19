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
        # Doc part:
        # ---------------------------------------------------------------------
        f_invoice.write('''<?xml version="1.0" encoding="UTF-8"?>
<p:FatturaElettronica versione="FPR12" 
   xmlns:ds="http://www.w3.org/2000/09/xmldsig#" 
xmlns:p="http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2" 
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
xsi:schemaLocation="http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2 http://www.fatturapa.gov.it/export/fatturazione/sdi/fatturapa/v1.2/Schema_del_file_xml_FatturaPA_versione_1.2.xsd">
\n''')

        # ---------------------------------------------------------------------
        # Header part:
        # ---------------------------------------------------------------------
        # 1.
        f_invoice.write('<FatturaElettronicaHeader>\n')        
        # 1.1
        f_invoice.write(' <DatiTrasmissione>\n')
        # 1.1.1
        f_invoice.write('  <IdTrasmittente>\n')
        # 1.1.1.1
        f_invoice.write('   <IdPaese>\n')
        # DATA
        f_invoice.write('   </IdPaese>\n')
        # 1.1.1.2
        f_invoice.write('   <IdCodice>\n')
        # DATA        
        f_invoice.write('   </IdCodice>\n')                
        f_invoice.write('  </IdTrasmittente>\n')
        
        # 1.1.2
        f_invoice.write('  <ProgressivoInvio>\n')
        # DATA
        f_invoice.write('  </ProgressivoInvio>\n')
        
        # 1.1.3
        f_invoice.write('  <FormatoTrasmissione>\n')
        # DATA FPR12
        f_invoice.write('  </FormatoTrasmissione>\n')

        # 1.1.4
        f_invoice.write('  <CodiceDestinatario>\n')
        # DATA 
        f_invoice.write('  </CodiceDestinatario>\n')

        # ---------------------------------------------------------------------
        # 1.1.5 (alternative 1.1.6)
        f_invoice.write('  <ContattiTrasmittente>\n')
        # 1.1.5.1
        f_invoice.write('   <Telefono>\n')
        # DATI
        f_invoice.write('   </Telefono>\n')
        # 1.1.5.2
        f_invoice.write('   <Email>\n')
        # DATI
        f_invoice.write('   </Email>\n')

        f_invoice.write('  </ContattiTrasmittente>\n')
        
        # ---------------------------------------------------------------------
        # 1.1.6 (alternative 1.1.5)
        f_invoice.write('  <PECDestinatario>\n')
        # DATA 
        f_invoice.write('  </PECDestinatario>\n')        

        f_invoice.write(' </DatiTrasmissione>\n')

        # ---------------------------------------------------------------------
        # 1.2
        f_invoice.write(' <CedentePrestatore>\n')

        # 1.2.1
        f_invoice.write('  <DatiAnagrafici>\n')

        # 1.2.1.1
        f_invoice.write('   <IdFiscaleIVA>\n')
        
        # 1.2.1.1.1
        f_invoice.write('    <IdPaese>\n')
        # DATI
        f_invoice.write('    </IdPaese>\n')

        # 1.2.1.1.2
        f_invoice.write('    <IdCodice>\n')
        # DATI
        f_invoice.write('    </IdCodice>\n')
        
        f_invoice.write('   </IdFiscaleIVA>\n')

        # 1.2.1.2
        f_invoice.write('   <CodiceFiscale>\n')
        # DATA        
        f_invoice.write('   </CodiceFiscale>\n')

        # 1.2.1.3
        f_invoice.write('   <Anagrafica>\n')
        
        # ---------------------------------------------------------------------
        # 1.2.1.3.1 (alternative 1.2.1.3.2   1.2.1.3.3
        f_invoice.write('    <Denominazione>\n')
        # DATI
        f_invoice.write('    </Denominazione>\n')
        
        # ---------------------------------------------------------------------
        # 1.2.3.1.2 (altenative 1.2.1.3.1)
        f_invoice.write('    <Nome>\n')
        # DATI
        f_invoice.write('    </Nome>\n')
        # 1.2.3.1.3 (altenative 1.2.1.3.3)
        f_invoice.write('    <Cognome>\n')
        # DATI
        f_invoice.write('    </Cognome>\n')

        # 1.2.3.1.4
        #f_invoice.write('    <Titolo>\n')
        # DATI
        #f_invoice.write('    </Titolo>\n')
        
        # 1.2.3.1.5
        #f_invoice.write('    <CodEORI>\n')
        # DATI
        #f_invoice.write('    </CodEORI>\n')

        f_invoice.write('   </Anagrafica>\n')

        # 1.2.1.4
        #f_invoice.write('   <AlboProfessionale>\n')
        # DATA
        #f_invoice.write('   </AlboProfessionale>\n')

        # 1.2.1.5
        #f_invoice.write('   <ProvinciaAlbo>\n')
        # DATA
        #f_invoice.write('   </ProvinciaAlbo>\n')

        # 1.2.1.6
        #f_invoice.write('   <NumeroIscrizioneAlbo>\n')
        # DATA
        #f_invoice.write('   </NumeroIscrizioneAlbo>\n')

        # 1.2.1.7
        #f_invoice.write('   <DataIscrizioneAlbo>\n')
        # DATA
        #f_invoice.write('   </DataIscrizioneAlbo>\n')

        # 1.2.1.8
        f_invoice.write('   <RegimeFiscale>\n')
        # DATA (TABELLA)
        f_invoice.write('   </RegimeFiscale>\n')

        f_invoice.write('  </DatiAnagrafici>\n')

        # 1.2.2
        f_invoice.write('  <Sede>\n')
        
        # 1.2.2.1
        f_invoice.write('   <Indirizzo>\n')
        # DATA
        f_invoice.write('   </Indirizzo>\n')

        # 1.2.2.2
        f_invoice.write('   <NumeroCivico>\n')
        # DATA
        f_invoice.write('   </NumeroCivico>\n')

        # 1.2.2.3
        f_invoice.write('   <CAP>\n')
        # DATA
        f_invoice.write('   </CAP>\n')

        # 1.2.2.4
        f_invoice.write('   <Comune>\n')
        # DATA
        f_invoice.write('   </Comune>\n')

        # 1.2.2.5
        f_invoice.write('   <Provincia>\n')
        # DATA
        f_invoice.write('   </Provincia>\n')

        # 1.2.2.6
        f_invoice.write('   <Nazione>\n')
        # DATA
        f_invoice.write('   </Nazione>\n')

        f_invoice.write('  </Sede>\n')

        # ---------------------------------------------------------------------
        # IF PRESENT:
        # 1.2.3
        f_invoice.write('  <StabileOrganizzazione>\n')
        
        # 1.2.3.1
        f_invoice.write('   <Indirizzo>\n')
        # DATA
        f_invoice.write('   </Indirizzo>\n')

        # 1.2.3.2
        f_invoice.write('   <NumeroCivico>\n')
        # DATA
        f_invoice.write('   </NumeroCivico>\n')

        # 1.2.3.3
        f_invoice.write('   <CAP>\n')
        # DATA
        f_invoice.write('   </CAP>\n')

        # 1.2.3.4
        f_invoice.write('   <Comune>\n')
        # DATA
        f_invoice.write('   </Comune>\n')

        # 1.2.3.5
        f_invoice.write('   <Provincia>\n')
        # DATA
        f_invoice.write('   </Provincia>\n')

        # 1.2.3.6
        f_invoice.write('   <Nazione>\n')
        # DATA
        f_invoice.write('   </Nazione>\n')

        f_invoice.write('  </StabileOrganizzazione>\n')
        # ---------------------------------------------------------------------

        # 1.2.4
        f_invoice.write('  <IscrizioneREA>\n')
        
        # 1.2.4.1
        f_invoice.write('   <Ufficio>\n')
        # DATA
        f_invoice.write('   </Ufficio>\n')

        # 1.2.4.2
        f_invoice.write('   <NumeroREA>\n')
        # DATA
        f_invoice.write('   </NumeroREA>\n')

        # 1.2.4.3  (0.1)
        #f_invoice.write('   <CapitaleSociale>\n')
        # DATA
        #f_invoice.write('   </CapitaleSociale>\n')

        # 1.2.4.3  (0.1)
        #f_invoice.write('   <SocioUnico>\n')
        # DATA
        #f_invoice.write('   </SocioUnico>\n')
       
        # 1.2.4.3  (0.1)
        f_invoice.write('   <StatoLiquidazione>\n')
        # DATA
        f_invoice.write('   </StatoLiquidazione>\n')
       
        f_invoice.write('  </IscrizioneREA>\n')
        
        # ---------------------------------------------------------------------
        # NOT MANDATORY:
        # 1.2.5
        #f_invoice.write('  <Contatti>\n')
        
        # 1.2.5.1
        #f_invoice.write('   <Telefono>\n')
        # DATA
        #f_invoice.write('   </Telefono>\n')

        # 1.2.5.2
        #f_invoice.write('   <Fax>\n')
        # DATA
        #f_invoice.write('   </Fax>\n')

        # 1.2.5.2
        #f_invoice.write('   <Email>\n')
        # DATA
        #f_invoice.write('   </Email>\n')

        #f_invoice.write('  </Contatti>\n')
        # ---------------------------------------------------------------------
        
        # ---------------------------------------------------------------------
        # NOT MANDATORY:
        # 1.2.6 RiferimentoAmministrazione
        
        # ---------------------------------------------------------------------
        # NOT MANDATORY:
        # 1.3 RappresentanteFiscale
        # 1.3.1 DatiAnagrafici
        # 1.3.1.1 IdFiscaleIVA
        # 1.3.1.1.1 IdPaese
        # 1.3.1.1.2 Idcodice
        # 1.3.1.2 CodiceFiscale
        # 1.3.1.3 Anagrafica
        # 1.3.1.3.1 Denominazione
        # 1.3.1.3.2 Nome
        # 1.3.1.3.3 Cognome
        # 1.3.1.3.4 Titolo
        # 1.3.1.3.5 CodEORI

        f_invoice.write(' </CedentePrestatore>\n')
        
        # 1.4
        f_invoice.write(' <CessionarioCommittente>\n')

        # 1.4.1
        f_invoice.write('  <DatiAnagrafici>\n')

        # 1.4.1.1
        f_invoice.write('   <IdFiscaleIVA>\n')
        
        # 1.4.1.1.1
        f_invoice.write('    <IdPaese>\n')
        # DATI
        f_invoice.write('    </IdPaese>\n')

        # 1.4.1.1.2
        f_invoice.write('    <IdCodice>\n')
        # DATI
        f_invoice.write('    </IdCodice>\n')
        
        f_invoice.write('   </IdFiscaleIVA>\n')

        # 1.4.1.2
        f_invoice.write('   <CodiceFiscale>\n')
        # DATA        
        f_invoice.write('   </CodiceFiscale>\n')

        # 1.4.1.3
        f_invoice.write('   <Anagrafica>\n')
        
        # ---------------------------------------------------------------------
        # 1.4.1.3.1 (alternative 1.2.1.3.2   1.2.1.3.3
        f_invoice.write('    <Denominazione>\n')
        # DATI
        f_invoice.write('    </Denominazione>\n')
        
        # ---------------------------------------------------------------------
        # 1.4.3.1.2 (altenative 1.2.1.3.1)
        f_invoice.write('    <Nome>\n')
        # DATI
        f_invoice.write('    </Nome>\n')
        # 1.4.3.1.3 (altenative 1.2.1.3.3)
        f_invoice.write('    <Cognome>\n')
        # DATI
        f_invoice.write('    </Cognome>\n')

        # 1.4.3.1.4
        #f_invoice.write('    <Titolo>\n')
        # DATI
        #f_invoice.write('    </Titolo>\n')
        
        # 1.4.3.1.5
        #f_invoice.write('    <CodEORI>\n')
        # DATI
        #f_invoice.write('    </CodEORI>\n')

        f_invoice.write('   </Anagrafica>\n')

        # ---------------------------------------------------------------------
        # 1.4.2
        f_invoice.write('  <Sede>\n')
        
        # 1.4.2.1
        f_invoice.write('   <Indirizzo>\n')
        # DATA
        f_invoice.write('   </Indirizzo>\n')

        # 1.4.2.2
        f_invoice.write('   <NumeroCivico>\n')
        # DATA
        f_invoice.write('   </NumeroCivico>\n')

        # 1.4.2.3
        f_invoice.write('   <CAP>\n')
        # DATA
        f_invoice.write('   </CAP>\n')

        # 1.4.2.4
        f_invoice.write('   <Comune>\n')
        # DATA
        f_invoice.write('   </Comune>\n')

        # 1.4.2.5
        f_invoice.write('   <Provincia>\n')
        # DATA
        f_invoice.write('   </Provincia>\n')

        # 1.4.2.6
        f_invoice.write('   <Nazione>\n')
        # DATA
        f_invoice.write('   </Nazione>\n')

        f_invoice.write('  </Sede>\n')

        # ---------------------------------------------------------------------
        # IF PRESENT:
        # 1.4.3
        f_invoice.write('  <StabileOrganizzazione>\n')
        
        # 1.4.3.1
        f_invoice.write('   <Indirizzo>\n')
        # DATA
        f_invoice.write('   </Indirizzo>\n')

        # 1.4.3.2
        f_invoice.write('   <NumeroCivico>\n')
        # DATA
        f_invoice.write('   </NumeroCivico>\n')

        # 1.4.3.3
        f_invoice.write('   <CAP>\n')
        # DATA
        f_invoice.write('   </CAP>\n')

        # 1.4.3.4
        f_invoice.write('   <Comune>\n')
        # DATA
        f_invoice.write('   </Comune>\n')

        # 1.4.3.5
        f_invoice.write('   <Provincia>\n')
        # DATA
        f_invoice.write('   </Provincia>\n')

        # 1.4.3.6
        f_invoice.write('   <Nazione>\n')
        # DATA
        f_invoice.write('   </Nazione>\n')

        f_invoice.write('  </StabileOrganizzazione>\n')
        # ---------------------------------------------------------------------

        # NOT MANDATORY:
        # 1.4.4 RappresentanteFiscale
        # 1.4.4.1 IdFiscaleIVA
        # 1.4.4.1.1 IdPaese
        # 1.4.4.1.2 IdCodice
        # 1.4.4.2 Denominazione
        # 1.4.4.3 Nome
        # 1.4.4.4 Cognome

        f_invoice.write('  </DatiAnagrafici>\n')
        f_invoice.write(' </CessionarioCommittente>\n')

        # NOT MANDATORY:
        # 1.5 TerzoIntermediarioOSoggettoEmittente
        # 1.5.1 DatiAnagrafici
        # 1.5.1.1 IdFiscaleIVA
        # 1.5.1.1.1 IdPaese
        # 1.5.1.1.2 IdCodice
        # 1.5.1.2 CodiceFiscale
        # 1.5.1.3 Anagrafica
        # 1.5.1.3.1 Denominazione
        # 1.5.1.3.2 Nome
        # 1.5.1.3.3 Cognome
        # 1.5.1.3.4 Titolo
        # 1.5.1.3.5 CodEORI

        # NOT MANDATORY:
        # 1.6 SoggettoEmittente
        
        f_invoice.write('</FatturaElettronicaHeader>\n')
        # ---------------------------------------------------------------------

        # ---------------------------------------------------------------------
        #                                BODY:
        # ---------------------------------------------------------------------
        # 2.
        f_invoice.write('<FatturaElettronicaBody>\n')
        
        # 2.1
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
