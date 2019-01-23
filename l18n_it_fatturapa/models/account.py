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
        
        # 2.1.1
        f_invoice.write('  <DatiGeneraliDocumento>\n')

        # 2.1.1.1
        f_invoice.write('   <TipoDocumento>\n')
        # DATA
        f_invoice.write('   </TipoDocumento>\n')

        # 2.1.1.2
        f_invoice.write('   <Divisa>\n')
        # DATA
        f_invoice.write('   </Divisa>\n')

        # 2.1.1.3
        f_invoice.write('   <Data>\n')
        # DATA
        f_invoice.write('   </Data>\n')

        # 2.1.1.4
        f_invoice.write('   <Numero>\n')
        # DATA
        f_invoice.write('   </Numero>\n')

        # 2.1.1.5
        #f_invoice.write('   <DatiRitenuta>\n')
        # 2.1.1.5.1 TipoRitenuta
        # 2.1.1.5.1 ImportoRitenuta
        # 2.1.1.5.1 AliquotaRitenuta
        # 2.1.1.5.1 CausaleRitenuta
        #f_invoice.write('   </DatiRitenuta>\n')

        # 2.1.1.6
        f_invoice.write('   <DatiBollo>\n')        
        
        # 2.1.1.6.1 
        f_invoice.write('    <BolloVirtuale>\n')        
        # DATA
        f_invoice.write('    </BolloVirtuale>\n')        

        # 2.1.1.6.2
        f_invoice.write('    <ImportoBollo>\n')        
        # DATA
        f_invoice.write('    </ImportoBollo>\n')        

        f_invoice.write('   </DatiBollo>\n')

        # 2.1.1.7 DatiCassaPrevidenziale
        # 2.1.1.7.1 TipoCassa
        # 2.1.1.7.2 AlCassa
        # 2.1.1.7.3 ImportoContributoCassa
        # 2.1.1.7.4 ImponibileCassa
        # 2.1.1.7.5 AliquotaIVA
        # 2.1.1.7.6 Ritenuta
        # 2.1.1.7.7 Natura
        # 2.1.1.7.8 RiferimentoAmministrazione

        # ---------------------------------------------------------------------
        # TEST: Abbuoni attivi / passivi:
        # 2.1.1.8
        f_invoice.write('   <ScontoMaggiorazione>\n')        
        
        # 2.1.1.8.1 
        f_invoice.write('    <Tipo>\n')        
        # DATA
        f_invoice.write('    </Tipo>\n')        

        # ---------------------------------------------------------------------
        # 2.1.1.8.2     >>> Alternative 2.1.1.8.3
        f_invoice.write('    <Percentuale>\n')        
        # DATA
        f_invoice.write('    </Percentuale>\n')        

        # ---------------------------------------------------------------------
        # 2.1.1.8.3     >>> Alternative 2.1.1.8.2
        f_invoice.write('    <Importo>\n')        
        # DATA
        f_invoice.write('    </Importo>\n')        

        f_invoice.write('   </ScontoMaggiorazione>\n')        
        
        # 2.1.1.9
        f_invoice.write('   <ImportoTotaleDocumento>\n')        
        f_invoice.write('   </ImportoTotaleDocumento>\n')        
        
        # 2.1.1.10
        f_invoice.write('   <Arrotondamento>\n')        
        f_invoice.write('   </Arrotondamento>\n')        

        # 2.1.1.11
        f_invoice.write('   <Causale>\n')        
        f_invoice.write('   </Causale>\n')        

        # 2.1.1.12
        f_invoice.write('   <Art73>\n')        
        # DATA
        f_invoice.write('   </Art73>\n')        
        
        f_invoice.write('  </DatiGeneraliDocumento>\n')
        
        # 2.1.2
        f_invoice.write('  <DatiOrdineAcquisto>\n')
        
        # 2.1.2.1 
        f_invoice.write('   <RiferimentoNumeroLinea>\n')
        # DATA
        f_invoice.write('   </RiferimentoNumeroLinea>\n')

        # 2.1.2.2
        f_invoice.write('   <IdDocumento>\n')
        # DATA
        f_invoice.write('   </IdDocumento>\n')

        # 2.1.2.3 
        f_invoice.write('   <Data>\n')
        # DATA
        f_invoice.write('   </Data>\n')

        # 2.1.2.4 
        f_invoice.write('   <NumItem>\n')
        # DATA
        f_invoice.write('   </NumItem>\n')

        # 2.1.2.5 
        f_invoice.write('   <CodiceCommessaConvenzione>\n')
        # DATA
        f_invoice.write('   </CodiceCommessaConvenzione>\n')

        # NOT MANDATORI: PA only:
        # 2.1.2.6 
        #f_invoice.write('   <CodiceCUP>\n')
        # DATA
        #f_invoice.write('   </CodiceCUP>\n')
        # 2.1.2.7 
        #f_invoice.write('   <CodiceCIG>\n')
        # DATA
        #f_invoice.write('   </CodiceCIG>\n')
 
        f_invoice.write('  </DatiOrdineAcquisto>\n')

        # 2.1.3
        f_invoice.write('   <DatiContratto>\n')
        # DATA
        f_invoice.write('   </DatiContratto>\n')

        # 2.1.4
        f_invoice.write('   <DatiConvenzione>\n')
        # DATA
        f_invoice.write('   </DatiConvenzione>\n')

        # 2.1.5
        f_invoice.write('   <DatiRicezione>\n')
        # DATA
        f_invoice.write('   </DatiRicezione>\n')

        # 2.1.6
        f_invoice.write('   <DatiFattureCollegate>\n')
        # DATA
        f_invoice.write('   </DatiFattureCollegate>\n')

        # 2.1.7
        f_invoice.write('   <DatiSAL>\n')
        
        # 2.1.7.1
        f_invoice.write('    <RiferimenntoFase>\n')
        # DATA 
        f_invoice.write('    </RiferimenntoFase>\n')
        
        f_invoice.write('   </DatiSAL>\n')

        # 2.1.8
        f_invoice.write('   <DatiDDT>\n')
        
        # 2.1.8.1 
        f_invoice.write('    <NumeroDDT>\n')
        # DATA
        f_invoice.write('    </NumeroDDT>\n')
                    
        # 2.1.8.2
        f_invoice.write('    <DataDDT>\n')
        # DATA                    
        f_invoice.write('    </DataDDT>\n')

        # 2.1.8.3
        f_invoice.write('    <RiferimentoNumeroLinea>\n')
        # DATA                    
        f_invoice.write('    </RiferimentoNumeroLinea>\n')
        
        f_invoice.write('   </DatiDDT>\n')

        # 2.1.9
        f_invoice.write('   <DatiTrasporto>\n')
        
        # 2.1.9.1
        f_invoice.write('    <DatiAnagraficiVettore>\n')

        # 2.1.9.1.1
        f_invoice.write('    <IdFiscaleIVA>\n')
        
        # 2.1.9.1.1.1
        f_invoice.write('     <IdPaese>\n')
        # DATI
        f_invoice.write('     </IdPaese>\n')

        # 2.1.9.1.1.2
        f_invoice.write('     <IdCodice>\n')
        # DATI
        f_invoice.write('     </IdCodice>\n')
        
        f_invoice.write('    </IdFiscaleIVA>\n')

        # 2.1.9.1.2
        f_invoice.write('    <CodiceFiscale>\n')
        # DATA        
        f_invoice.write('    </CodiceFiscale>\n')

        # 2.1.9.1.3
        f_invoice.write('    <Anagrafica>\n')
        
        # ---------------------------------------------------------------------
        # 2.1.9.1.3.1 (alternative 2.1.9.1.3.2    2.1.9.1.3.3
        f_invoice.write('     <Denominazione>\n')
        # DATI
        f_invoice.write('     </Denominazione>\n')
        
        # ---------------------------------------------------------------------
        # 2.1.9.1.3.2 (altenative 2.1.9.1.3.1)
        f_invoice.write('     <Nome>\n')
        # DATI
        f_invoice.write('     </Nome>\n')
        # 2.1.9.1.3.3 (altenative 1.2.1.3.3)
        f_invoice.write('     <Cognome>\n')
        # DATI
        f_invoice.write('     </Cognome>\n')

        # 2.1.9.1.3.4
        #f_invoice.write('     <Titolo>\n')
        # DATI
        #f_invoice.write('     </Titolo>\n')
        
        # 2.1.9.1.3.5
        #f_invoice.write('     <CodEORI>\n')
        # DATI
        #f_invoice.write('     </CodEORI>\n')

        # 2.1.9.1.4
        #f_invoice.write('    <NumeroLicenzaGuida>\n')
        # DATA        
        #f_invoice.write('    </NumeroLicenzaGuida>\n')

        f_invoice.write('    </Anagrafica>\n')

        f_invoice.write('    </DatiAnagraficiVettore>\n')

        # 2.1.9.2
        f_invoice.write('    <MezzoTrasporto>\n')
        # DATA
        f_invoice.write('    </MezzoTrasporto>\n')

        # 2.1.9.3
        f_invoice.write('    <CausaleTrasporto>\n')
        # DATA
        f_invoice.write('    </CausaleTrasporto>\n')

        # 2.1.9.4
        f_invoice.write('    <NumeroColli>\n')
        # DATA
        f_invoice.write('    </NumeroColli>\n')

        # 2.1.9.5
        f_invoice.write('    <Descrizione>\n')
        # DATA
        f_invoice.write('    </Descrizione>\n')

        # 2.1.9.6
        f_invoice.write('    <UnitaMisuraPeso>\n')
        # DATA
        f_invoice.write('    </UnitaMisuraPeso>\n')

        # 2.1.9.7
        f_invoice.write('    <PesoLordo>\n')
        # DATA
        f_invoice.write('    </PesoLordo>\n')

        # 2.1.9.8
        f_invoice.write('    <PesoNetto>\n')
        # DATA
        f_invoice.write('    </PesoNetto>\n')

        # 2.1.9.9
        f_invoice.write('    <DataOraRitiro>\n')
        # DATA
        f_invoice.write('    </DataOraRitiro>\n')

        # 2.1.9.10
        f_invoice.write('    <DataInizioTrasporto>\n')
        # DATA
        f_invoice.write('    </DataInizioTrasporto>\n')

        # 2.1.9.11
        f_invoice.write('    <TipoResa>\n')
        # DATA
        f_invoice.write('    </TipoResa>\n')

        # ---------------------------------------------------------------------
        # 2.1.9.12
        f_invoice.write('   <IndirizzoResa>\n')
        
        # 2.1.9.12.1
        f_invoice.write('    <Indirizzo>\n')
        # DATA
        f_invoice.write('    </Indirizzo>\n')

        # 2.1.9.12.2
        f_invoice.write('    <NumeroCivico>\n')
        # DATA
        f_invoice.write('    </NumeroCivico>\n')

        # 2.1.9.12.3
        f_invoice.write('    <CAP>\n')
        # DATA
        f_invoice.write('    </CAP>\n')

        # 2.1.9.12.4
        f_invoice.write('    <Comune>\n')
        # DATA
        f_invoice.write('    </Comune>\n')

        # 2.1.9.12.5
        f_invoice.write('    <Provincia>\n')
        # DATA
        f_invoice.write('    </Provincia>\n')

        # 2.1.9.12.6
        f_invoice.write('    <Nazione>\n')
        # DATA
        f_invoice.write('    </Nazione>\n')
                
        f_invoice.write('   </IndirizzoResa>\n')
        # ---------------------------------------------------------------------

        # 2.1.9.13
        f_invoice.write('    <DataOraConsegna>\n')
        # DATA
        f_invoice.write('    </DataOraConsegna>\n')

        f_invoice.write('   </DatiTrasporto>\n')

        # ---------------------------------------------------------------------
        # NOT MANADATORY: Agevolazione trasportatore:
        # 2.1.10
        f_invoice.write('   <FatturaPrincipale>\n')        
        
        # 2.1.10.1
        f_invoice.write('    <NumeroFatturaPrincipale>\n')        
        # DATA
        f_invoice.write('    </NumeroFatturaPrincipale>\n')

        # 2.1.10.2
        f_invoice.write('    <DataFatturaPrincipale>\n')        
        # DATA
        f_invoice.write('    </DataFatturaPrincipale>\n')

        f_invoice.write('   </FatturaPrincipale>\n')
        # ---------------------------------------------------------------------
        
        f_invoice.write(' </DatiGenerali>\n')

        # 2.2
        f_invoice.write(' <DatiBeniServizi>\n')

        # 2.2.1
        f_invoice.write('  <DettaglioLinee>\n')

        # 2.2.1.1
        f_invoice.write('   <NumeroLinea>\n')
        f_invoice.write('   </NumeroLinea>\n')

        # 2.2.1.2 # Solo se SC PR AB AC (spesa accessoria)
        #f_invoice.write('   <TipoCessionePrestazione>\n')
        #f_invoice.write('   </TipoCessionePrestazione>\n')

        # 2.2.1.3
        f_invoice.write('   <CodiceArticolo>\n')

        # 2.2.1.3.1 # PROPRIETARIO EAN TARIC SSC
        f_invoice.write('    <CodiceTipo>\n')
        f_invoice.write('    </CodiceTipo>\n')

        # 2.2.1.3.2 # come da punto precedente
        f_invoice.write('    <CodiceValore>\n')
        f_invoice.write('    </CodiceValore>\n')

        f_invoice.write('   </CodiceArticolo>\n')

        # 2.2.1.4
        f_invoice.write('   <Descrizione>\n')
        f_invoice.write('   </Descrizione>\n')

        # 2.2.1.5
        f_invoice.write('   <Quantita>\n')
        f_invoice.write('   </Quantita>\n')

        # 2.2.1.6
        f_invoice.write('   <UnitaMisura>\n')
        f_invoice.write('   </UnitaMisura>\n')

        # 2.2.1.7 # Per Servizi
        f_invoice.write('   <DataInizioPeriodo>\n')
        f_invoice.write('   </DataInizioPeriodo>\n')

        # 2.2.1.8 # Per Servizi
        f_invoice.write('   <DataFinePeriodo>\n')
        f_invoice.write('   </DataFinePeriodo>\n')

        # 2.2.1.9 # Anche negativo # Vedi 2.2.1.2
        f_invoice.write('   <PrezzoUnitario>\n')
        f_invoice.write('   </PrezzoUnitario>\n')

        # 2.2.1.10
        f_invoice.write('   <ScontoMaggiorazione>\n')

        # 2.2.1.10.1 # SC o MG
        f_invoice.write('    <Tipo>\n')
        f_invoice.write('    </Tipo>\n')

        # 2.2.1.10.2 # Alternativo a 2.2.1.10.3
        f_invoice.write('    <Percentuale>\n')
        f_invoice.write('    </Percentuale>\n')

        # 2.2.1.10.3 # Alternativo a 2.2.1.10.2
        f_invoice.write('    <Importo>\n')
        f_invoice.write('    </Importo>\n')

        f_invoice.write('   </ScontoMaggiorazione>\n')

        # 2.2.1.11
        f_invoice.write('   <PrezzoTotale>\n')
        f_invoice.write('   </PrezzoTotale>\n')

        # 2.2.1.12
        f_invoice.write('   <AliquotaIVA>\n')
        f_invoice.write('   </AliquotaIVA>\n')

        # 2.2.1.13
        f_invoice.write('   <Ritenuta>\n')
        f_invoice.write('   </Ritenuta>\n')

        # 2.2.1.14
        f_invoice.write('   <Natura>\n')
        f_invoice.write('   </Natura>\n')

        # 2.2.1.15
        f_invoice.write('   <RiferimentoAmministrazione>\n')
        f_invoice.write('   </RiferimentoAmministrazione>\n')

        # 2.2.1.16
        f_invoice.write('   <AltriDatiGestionali>\n')

        # 2.2.1.16.1
        f_invoice.write('    <TipoDato>\n')
        f_invoice.write('    </TipoDato>\n')

        # 2.2.1.16.2
        f_invoice.write('    <RiferimentoTesto>\n')
        f_invoice.write('    </RiferimentoTesto>\n')

        # 2.2.1.16.3
        f_invoice.write('    <RiferimentoNumero>\n')
        f_invoice.write('    </RiferimentoNumero>\n')

        # 2.2.1.16.4
        f_invoice.write('    <RiferimentoData>\n')
        f_invoice.write('    </RiferimentoData>\n')

        f_invoice.write('   </AltriDatiGestionali>\n')
        
        f_invoice.write(' </DettaglioLinee>\n')

        # 2.2.2
        f_invoice.write('  <DatiRiepilogo>\n')

        # 2.2.2.1
        f_invoice.write('   <AliquotaIVA>\n')
        f_invoice.write('   </AliquotaIVA>\n')

        # 2.2.2.2 # Tabella
        f_invoice.write('   <Natura>\n')
        f_invoice.write('   </Natura>\n')

        # 2.2.2.3
        f_invoice.write('   <SpeseAccessorie>\n')
        f_invoice.write('   </SpeseAccessorie>\n')

        # 2.2.2.4
        f_invoice.write('   <Arrotondamento>\n')
        f_invoice.write('   </Arrotondamento>\n')

        # 2.2.2.5
        f_invoice.write('   <ImponibileImporto>\n')
        f_invoice.write('   </ImponibileImporto>\n')

        # 2.2.2.6
        f_invoice.write('   <Imposta>\n')
        f_invoice.write('   </Imposta>\n')

        # 2.2.2.7
        f_invoice.write('   <EsigibilitaIVA>\n')
        f_invoice.write('   </EsigibilitaIVA>\n')

        # 2.2.2.8
        f_invoice.write('   <RiferimentoNormativo>\n')
        f_invoice.write('   </RiferimentoNormativo>\n')

        f_invoice.write('  </DatiRiepilogo>\n')

        f_invoice.write(' </DatiBeniServizi>\n')

        # 2.4
        f_invoice.write(' <DatiPagamento>\n')

        # 2.4.1
        f_invoice.write('  <CondizioniPagamento>\n')
        f_invoice.write('  </CondizioniPagamento>\n')
        
        # 2.4.2
        f_invoice.write('  <DettaglioPagamento>\n')

        # 2.4.2.1
        f_invoice.write('   <Beneficiario>\n')
        f_invoice.write('   </Beneficiario>\n')
        
        # 2.4.2.2
        f_invoice.write('   <ModalitaPagamento>\n')
        f_invoice.write('   </ModalitaPagamento>\n')
        
        # 2.4.2.3
        f_invoice.write('   <DataRiferimentoTerminiPagamento>\n')
        f_invoice.write('   </DataRiferimentoTerminiPagamento>\n')
        
        # 2.4.2.4
        f_invoice.write('   <GiorniTerminiPagamento>\n')
        f_invoice.write('   </GiorniTerminiPagamento>\n')
        
        # 2.4.2.5
        f_invoice.write('   <DataScadenzaPagamento>\n')
        f_invoice.write('   </DataScadenzaPagamento>\n')
        
        # 2.4.2.6
        f_invoice.write('   <ImportoPagamento>\n')
        f_invoice.write('   </ImportoPagamento>\n')
        
        # 2.4.2.7
        f_invoice.write('   <CodUfficioPostale>\n')
        f_invoice.write('   </CodUfficioPostale>\n')
        
        # 2.4.2.8
        f_invoice.write('   <CognomeQuietanzante>\n')
        f_invoice.write('   </CognomeQuietanzante>\n')
        
        # 2.4.2.9
        f_invoice.write('   <NomeQuietanzante>\n')
        f_invoice.write('   </NomeQuietanzante>\n')
        
        # 2.4.2.10
        f_invoice.write('   <CFQuietanzante>\n')
        f_invoice.write('   </CFQuietanzante>\n')
        
        # 2.4.2.11
        f_invoice.write('   <TitoloQuietanzante>\n')
        f_invoice.write('   </TitoloQuietanzante>\n')
        
        # 2.4.2.12
        f_invoice.write('   <BenefiIstitutoFInanziariociario>\n')
        f_invoice.write('   </IstitutoFInanziario>\n')
        
        # 2.4.2.13
        f_invoice.write('   <IBAN>\n')
        f_invoice.write('   </IBAN>\n')
        
        # 2.4.2.14
        f_invoice.write('   <ABI>\n')
        f_invoice.write('   </ABI>\n')
        
        # 2.4.2.15
        f_invoice.write('   <CAB>\n')
        f_invoice.write('   </CAB>\n')
        
        # 2.4.2.16
        f_invoice.write('   <BIC>\n')
        f_invoice.write('   </BIC>\n')
        
        # 2.4.2.17
        f_invoice.write('   <ScontoPagamentoAnticipato>\n')
        f_invoice.write('   </ScontoPagamentoAnticipato>\n')
        
        # 2.4.2.18
        f_invoice.write('   <DataLimitePagamentoAnticipato>\n')
        f_invoice.write('   </DataLimitePagamentoAnticipato>\n')
        
        # 2.4.2.19
        f_invoice.write('   <PenalitaPagamentiRitardati>\n')
        f_invoice.write('   </PenalitaPagamentiRitardati>\n')
        
        # 2.4.2.20
        f_invoice.write('   <DataDecorrenzaPenale>\n')
        f_invoice.write('   </DataDecorrenzaPenale>\n')
        
        # 2.4.2.21
        f_invoice.write('   <CodicePagamento>\n')
        f_invoice.write('   </CodicePagamento>\n')

        f_invoice.write('  </DettaglioPagamento>\n')
        f_invoice.write(' </DatiPagamento>\n')

        # 2.5
        f_invoice.write(' <Allegati>\n')

        # 2.5.1
        f_invoice.write('  <NomeAttachment>\n')
        f_invoice.write('  </NomeAttachment>\n')

        # 2.5.2 # ZIP RAR
        f_invoice.write('  <AlgoritmoCompressione>\n')
        f_invoice.write('  </AlgoritmoCompressione>\n')

        # 2.5.3 # TXT XML DOC PDF
        f_invoice.write('  <FormatoAttachment>\n')
        f_invoice.write('  </FormatoAttachment>\n')

        # 2.5.4
        f_invoice.write('  <DescrizioneAttachment>\n')
        f_invoice.write('  </DescrizioneAttachment>\n')

        # 2.5.5
        f_invoice.write('  <Attachment>\n')
        f_invoice.write('  </Attachment>\n')

        f_invoice.write(' </Allegati>\n')

        f_invoice.write('</FatturaElettronicaBody>\n')
        f_invoice.write('</p:FatturaElettronica>\n')

        f_invoice.close()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
