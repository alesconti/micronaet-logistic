#!/usr/bin/python
# -*- coding: utf-8 -*-
###############################################################################
#
# ODOO (ex OpenERP) 
# Open Source Management Solution
# Copyright (C) 2001-2015 Micronaet S.r.l. (<https://micronaet.com>)
# Developer: Nicola Riolini @thebrush (<https://it.linkedin.com/in/thebrush>)
# Copyright (C) 2014 Davide Corio <davide.corio@lsweb.it>
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
from odoo import api, models, fields
from odoo import tools
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)


class FatturapaFormat(models.Model):
    ''' Fattura PA Format and utility for formatting
        ['1.1.3']
    '''
    _name = 'fatturapa.format'
    _description = 'FatturaPA Format'

    # -------------------------------------------------------------------------
    # Utility:
    # -------------------------------------------------------------------------
    @api.model
    def format_pa_date(self, value):
        ''' Date ISO format YYYY-MM-GG
        '''        
        return value

    @api.model
    def format_pa_float(self, value):
        ''' Date ISO format 0.00
        '''
        if not value or type(value) != float:
            return '0.00'
        else:
            return ('%10.2f' % value).strip()

    # -------------------------------------------------------------------------
    #                             COLUMNS:
    # -------------------------------------------------------------------------
    name = fields.Char('Description', size=128)
    code = fields.Char('Code', size=5)
    doc_part = fields.Text('Doc Part')

class FatturapaDocumentType(models.Model):
    ''' Document type (invoice, credit note):
        ['2.1.1.1'] (Startup data)
    '''
    _name = 'fatturapa.document_type'
    _description = 'FatturaPA Document Type'

    # -------------------------------------------------------------------------
    #                             COLUMNS:
    # -------------------------------------------------------------------------
    name = fields.Char('Description', size=128)
    code = fields.Char('Code', size=4)

class FatturapaPaymentTerm(models.Model):
    ''' Payment term
        ['2.4.1']
    '''
    _name = 'fatturapa.payment_term'
    _description = 'FatturaPA Payment Term'

    # -------------------------------------------------------------------------
    #                             COLUMNS:
    # -------------------------------------------------------------------------
    name = fields.Char('Description', size=128)
    code = fields.Char('Code', size=4)

class FatturapaPaymentMethod(models.Model):
    ''' Payment method
        ['2.4.2.2']
    '''
    _name = 'fatturapa.payment_method'
    _description = 'FatturaPA Payment Method'

    # -------------------------------------------------------------------------
    #                             COLUMNS:
    # -------------------------------------------------------------------------
    name = fields.Char('Description', size=128)
    code = fields.Char('Code', size=4)

class WelfareFundType(models.Model):
    ''' Welfare fund
        ['2.1.1.7.1']
    '''
    _name = 'welfare.fund.type'
    _description = 'welfare fund type'

    # -------------------------------------------------------------------------
    #                             COLUMNS:
    # -------------------------------------------------------------------------
    name = fields.Char('Name')
    description = fields.Char('Description')

class FatturapaFiscalPosition(models.Model):
    ''' Fiscal position:
        ['2.1.1.7.7', '2.2.1.14']
    '''
    _name = 'fatturapa.fiscal_position'
    _description = 'FatturaPA Fiscal Position'

    # -------------------------------------------------------------------------
    #                             COLUMNS:
    # -------------------------------------------------------------------------
    name = fields.Char('Description', size=128)
    code = fields.Char('Code', size=4)

class AccountPaymentTerm(models.Model):
    ''' Payment term
        ['2.4.2.2']
    '''
    _inherit = 'account.payment.term'

    # -------------------------------------------------------------------------
    #                             COLUMNS:
    # -------------------------------------------------------------------------
    fatturapa_pt_id = fields.Many2one(
        'fatturapa.payment_term', string='FatturaPA Payment Term')
    fatturapa_pm_id = fields.Many2one(
        'fatturapa.payment_method', string='FatturaPA Payment Method')

class ResPartner(models.Model):
    ''' Extra data for partner 
    '''
    _inherit = 'res.partner'

    # -------------------------------------------------------------------------
    #                             COLUMNS:
    # -------------------------------------------------------------------------
    # REA:
    rea_office = fields.Many2one(
        'res.country.state', string='Office Province')
    rea_code = fields.Char('REA Code', size=20)
    rea_capital = fields.Float('Capital')
    rea_member_type = fields.Selection(
        [('SU', 'Unique Member'),
         ('SM', 'Multiple Members')], 'Member Type')
    rea_liquidation_state = fields.Selection(
        [('LS', 'In liquidation'),
         ('LN', 'Not in liquidation')], 'Liquidation State')

    # Fattura PA:
    eori_code = fields.Char('EORI Code', size=20)
    license_number = fields.Char('License Code', size=20)
    # 1.2.6 RiferimentoAmministrazione
    pa_partner_code = fields.Char('PA Code for partner', size=20)
    # 1.2.1.4
    register = fields.Char('Professional Register', size=60)
    # 1.2.1.5
    register_province = fields.Many2one(
        'res.country.state', string='Register Province')
    # 1.2.1.6
    register_code = fields.Char('Register Code', size=60)
    # 1.2.1.7
    register_regdate = fields.Date('Register Registration Date')
    # 1.2.1.8
    register_fiscalpos = fields.Many2one(
        'fatturapa.fiscal_position',
        string='Register Fiscal Position')

    # -------------------------------------------------------------------------
    # Contraints:
    # -------------------------------------------------------------------------
    _sql_constraints = [
        ('rea_code_uniq', 'unique (rea_code, company_id)',
         'The rea code code must be unique per company !'),
        ]

class ResCompany(models.Model):
    ''' Company data
    '''
    
    _inherit = 'res.company'
    
    # -------------------------------------------------------------------------
    #                             COLUMNS:
    # -------------------------------------------------------------------------
    fatturapa_fiscal_position_id = fields.Many2one(
        'fatturapa.fiscal_position', 'Fiscal Position',
        help='Fiscal position used by FatturaPA',
        )
    fatturapa_format_id = fields.Many2one(
        'fatturapa.format', 'Format',
        help='FatturaPA Format',
        )
    fatturapa_sequence_id = fields.Many2one(
        'ir.sequence', 'Sequence',
        help='Il progressivo univoco del file è rappresentato da una '
             'stringa alfanumerica di lunghezza massima di 5 caratteri '
             'e con valori ammessi da "A" a "Z" e da "0" a "9".',
        )
    fatturapa_art73 = fields.Boolean('Art73')
    fatturapa_pub_administration_ref = fields.Char(
        'Public Administration Reference Code', size=20,
        )
    fatturapa_rea_office = fields.Many2one('res.country.state',
        related='partner_id.rea_office', string='REA office')
    #fatturapa_rea_number = fields.Char(
    #    related='partner_id.rea_code', string='Rea Number')
    fatturapa_rea_capital = fields.Float(
        related='partner_id.rea_capital', string='Rea Capital')
    fatturapa_rea_partner = fields.Selection([
        ('SU', 'Unique Member'),
        ('SM', 'Multiple Members'),
        ], related='partner_id.rea_member_type', string='Member Type')
    fatturapa_rea_liquidation = fields.Selection([
        ('LS', 'In liquidation'),
        ('LN', 'Not in liquidation'),
        ], related='partner_id.rea_liquidation_state', 
        string='Liquidation State')
    fatturapa_tax_representative = fields.Many2one(
        'res.partner', 'Legal Tax Representative'
        )
    fatturapa_sender_partner = fields.Many2one(
        'res.partner', 'Third Party/Sender'
        )

class AccountFiscalPosition(models.Model):
    ''' Fattura PA for fiscal position
    '''
    _inherit = 'account.fiscal.position'
    
    # -------------------------------------------------------------------------
    #                             COLUMNS:
    # -------------------------------------------------------------------------
    fatturapa = fields.Boolean('Fattura PA')

class AccountTax(models.Model):
    ''' Account tax fattura PA data
    '''
    _inherit = 'account.tax'

    # -------------------------------------------------------------------------
    #                             COLUMNS:
    # -------------------------------------------------------------------------
    non_taxable_nature = fields.Selection([
        ('N1', 'escluse ex art. 15'),
        ('N2', 'non soggette'),
        ('N3', 'non imponibili'),
        ('N4', 'esenti'),
        ('N5', 'regime del margine'),
        ('N6', 'inversione contabile (reverse charge)'),
        ], string="Non taxable nature")
    payability = fields.Selection([
        ('I', 'Immediate payability'),
        ('D', 'Deferred payability'),
        ('S', 'Split payment'),
        ], string="VAT payability")
    law_reference = fields.Char(
        'Law reference', size=128)

    """@api.model
    def get_tax_by_invoice_tax(self, invoice_tax):
        if ' - ' in invoice_tax:
            tax_descr = invoice_tax.split(' - ')[0]
            tax_ids = self.search(cr, uid, [
                ('description', '=', tax_descr),
                ], context=context)
            if not tax_ids:
                raise orm.except_orm(
                    _('Error'), _('No tax %s found') %
                    tax_descr)
            if len(tax_ids) > 1:
                raise orm.except_orm(
                    _('Error'), _('Too many tax %s found') %
                    tax_descr)
        else:
            tax_name = invoice_tax
            tax_ids = self.search(cr, uid, [
                ('name', '=', tax_name),
                ], context=context)
            if not tax_ids:
                raise orm.except_orm(
                    _('Error'), _('No tax %s found') %
                    tax_name)
            if len(tax_ids) > 1:
                raise orm.except_orm(
                    _('Error'), _('Too many tax %s found') %
                    tax_name)
        return tax_ids[0]"""
        
class StockPicking(models.Model):
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
        #company_pool = self.env['res.company']
        #company = company_pool.search([])[0]
        
        # TODO mode parameter in company: fatturapa_format_id
        
        # ---------------------------------------------------------------------
        # Generate filename for invoice:
        # ---------------------------------------------------------------------
        # TODO
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
        # TODO IR
        f_invoice.write('   </IdPaese>\n')
        # 1.1.1.2
        f_invoice.write('   <IdCodice>\n')
        # TODO codice fiscale     
        f_invoice.write('   </IdCodice>\n')                
        f_invoice.write('  </IdTrasmittente>\n')
        
        # 1.1.2
        f_invoice.write('  <ProgressivoInvio>\n')
        # TODO numero fattura
        f_invoice.write('  </ProgressivoInvio>\n')
        
        # 1.1.3
        f_invoice.write('  <FormatoTrasmissione>\n')
        # TODO FPR12   (No FPA12)
        f_invoice.write('  </FormatoTrasmissione>\n')

        # 1.1.4
        f_invoice.write('  <CodiceDestinatario>\n')
        # TODO Cocide univoco destinatario (7 caratteri PR, 6 PA) tutti 0 alt.
        f_invoice.write('  </CodiceDestinatario>\n')

        # ---------------------------------------------------------------------
        # 1.1.5 (alternative 1.1.6)
        #f_invoice.write('  <ContattiTrasmittente>\n')
        # 1.1.5.1
        #f_invoice.write('   <Telefono>\n')
        # DATI
        #f_invoice.write('   </Telefono>\n')
        # 1.1.5.2
        #f_invoice.write('   <Email>\n')
        # DATI
        #f_invoice.write('   </Email>\n')

        #f_invoice.write('  </ContattiTrasmittente>\n')
        
        # ---------------------------------------------------------------------
        # 1.1.6 (alternative 1.1.5)
        f_invoice.write('  <PECDestinatario>\n')
        # TODO obbligatorio se non c'è CodiceDestinatario
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
        # TODO IT 
        f_invoice.write('    </IdPaese>\n')

        # 1.2.1.1.2
        f_invoice.write('    <IdCodice>\n')
        # TODO VAT company
        f_invoice.write('    </IdCodice>\n')
        
        f_invoice.write('   </IdFiscaleIVA>\n')

        # 1.2.1.2
        f_invoice.write('   <CodiceFiscale>\n')
        # TODO Codice fiscale company
        f_invoice.write('   </CodiceFiscale>\n')

        # 1.2.1.3
        f_invoice.write('   <Anagrafica>\n')
        
        # ---------------------------------------------------------------------
        # 1.2.1.3.1 (alternative 1.2.1.3.2   1.2.1.3.3
        f_invoice.write('    <Denominazione>\n')
        # RAGIONE SOCIALE Company
        f_invoice.write('    </Denominazione>\n')
        
        # ---------------------------------------------------------------------
        # 1.2.3.1.2 (altenative 1.2.1.3.1)
        #f_invoice.write('    <Nome>\n')
        # DATI
        #f_invoice.write('    </Nome>\n')
        # 1.2.3.1.3 (altenative 1.2.1.3.3)
        #f_invoice.write('    <Cognome>\n')
        # DATI
        #f_invoice.write('    </Cognome>\n')

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
        # TODO TABELLA: RF01
        f_invoice.write('   </RegimeFiscale>\n')

        f_invoice.write('  </DatiAnagrafici>\n')

        # 1.2.2
        f_invoice.write('  <Sede>\n')
        
        # 1.2.2.1
        f_invoice.write('   <Indirizzo>\n')
        # TODO
        f_invoice.write('   </Indirizzo>\n')

        # 1.2.2.2
        f_invoice.write('   <NumeroCivico>\n')
        # TODO
        f_invoice.write('   </NumeroCivico>\n')

        # 1.2.2.3
        f_invoice.write('   <CAP>\n')
        # TODO
        f_invoice.write('   </CAP>\n')

        # 1.2.2.4
        f_invoice.write('   <Comune>\n')
        # TODO
        f_invoice.write('   </Comune>\n')

        # 1.2.2.5
        f_invoice.write('   <Provincia>\n')
        # TODO
        f_invoice.write('   </Provincia>\n')

        # 1.2.2.6
        f_invoice.write('   <Nazione>\n')
        # TODO
        f_invoice.write('   </Nazione>\n')

        f_invoice.write('  </Sede>\n')

        # ---------------------------------------------------------------------
        # IF PRESENT:
        # 1.2.3
        #f_invoice.write('  <StabileOrganizzazione>\n')
        
        # 1.2.3.1
        #f_invoice.write('   <Indirizzo>\n')
        # DATA
        #f_invoice.write('   </Indirizzo>\n')

        # 1.2.3.2
        #f_invoice.write('   <NumeroCivico>\n')
        # DATA
        #f_invoice.write('   </NumeroCivico>\n')

        # 1.2.3.3
        #f_invoice.write('   <CAP>\n')
        # DATA
        #f_invoice.write('   </CAP>\n')

        # 1.2.3.4
        #f_invoice.write('   <Comune>\n')
        # DATA
        #f_invoice.write('   </Comune>\n')

        # 1.2.3.5
        #f_invoice.write('   <Provincia>\n')
        # DATA
        #f_invoice.write('   </Provincia>\n')

        # 1.2.3.6
        #f_invoice.write('   <Nazione>\n')
        # DATA
        #f_invoice.write('   </Nazione>\n')

        #f_invoice.write('  </StabileOrganizzazione>\n')
        # ---------------------------------------------------------------------

        # 1.2.4
        f_invoice.write('  <IscrizioneREA>\n')
        
        # 1.2.4.1
        f_invoice.write('   <Ufficio>\n')
        # TODO
        f_invoice.write('   </Ufficio>\n')

        # 1.2.4.2
        f_invoice.write('   <NumeroREA>\n')
        # TODO
        f_invoice.write('   </NumeroREA>\n')

        # 1.2.4.3  (0.1)
        #f_invoice.write('   <CapitaleSociale>\n')
        # TODO
        #f_invoice.write('   </CapitaleSociale>\n')

        # 1.2.4.3  (0.1)
        #f_invoice.write('   <SocioUnico>\n')
        # TODO
        #f_invoice.write('   </SocioUnico>\n')
       
        # 1.2.4.3  (0.1)
        f_invoice.write('   <StatoLiquidazione>\n')
        # TODO
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

        # Alternativo al blocco 1.4.1.2 ---------------------------------------
        # 1.4.1.1
        f_invoice.write('   <IdFiscaleIVA>\n')
        
        # 1.4.1.1.1
        f_invoice.write('    <IdPaese>\n')
        # TODO IT cliente
        f_invoice.write('    </IdPaese>\n')

        # 1.4.1.1.2
        f_invoice.write('    <IdCodice>\n')
        # TODO Codice fiscale cliente
        f_invoice.write('    </IdCodice>\n')
        
        f_invoice.write('   </IdFiscaleIVA>\n')

        # Alternativo al blocco 1.4.1.1 ---------------------------------------
        # 1.4.1.2
        f_invoice.write('   <CodiceFiscale>\n')
        # TODO        
        f_invoice.write('   </CodiceFiscale>\n')

        # 1.4.1.3
        f_invoice.write('   <Anagrafica>\n')
        
        # ---------------------------------------------------------------------
        # 1.4.1.3.1 (alternative 1.2.1.3.2   1.2.1.3.3
        f_invoice.write('    <Denominazione>\n')
        # TODO Ragione sociale
        f_invoice.write('    </Denominazione>\n')
        
        # ---------------------------------------------------------------------
        # 1.4.3.1.2 (altenative 1.2.1.3.1)
        f_invoice.write('    <Nome>\n')
        # TODO
        f_invoice.write('    </Nome>\n')
        # 1.4.3.1.3 (altenative 1.2.1.3.3)
        f_invoice.write('    <Cognome>\n')
        # TODO
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
        # TODO
        f_invoice.write('   </Indirizzo>\n')

        # 1.4.2.2
        f_invoice.write('   <NumeroCivico>\n')
        # TODO
        f_invoice.write('   </NumeroCivico>\n')

        # 1.4.2.3
        f_invoice.write('   <CAP>\n')
        # TODO
        f_invoice.write('   </CAP>\n')

        # 1.4.2.4
        f_invoice.write('   <Comune>\n')
        # TODO
        f_invoice.write('   </Comune>\n')

        # 1.4.2.5
        f_invoice.write('   <Provincia>\n')
        # TODO
        f_invoice.write('   </Provincia>\n')

        # 1.4.2.6
        f_invoice.write('   <Nazione>\n')
        # TODO
        f_invoice.write('   </Nazione>\n')

        f_invoice.write('  </Sede>\n')

        # ---------------------------------------------------------------------
        # IF PRESENT:
        # 1.4.3
        #f_invoice.write('  <StabileOrganizzazione>\n')
        
        # 1.4.3.1
        #f_invoice.write('   <Indirizzo>\n')
        # DATA
        #f_invoice.write('   </Indirizzo>\n')

        # 1.4.3.2
        #f_invoice.write('   <NumeroCivico>\n')
        # DATA
        #f_invoice.write('   </NumeroCivico>\n')

        # 1.4.3.3
        #f_invoice.write('   <CAP>\n')
        # DATA
        #f_invoice.write('   </CAP>\n')

        # 1.4.3.4
        #f_invoice.write('   <Comune>\n')
        # DATA
        #f_invoice.write('   </Comune>\n')

        # 1.4.3.5
        #f_invoice.write('   <Provincia>\n')
        # DATA
        #f_invoice.write('   </Provincia>\n')

        # 1.4.3.6
        #f_invoice.write('   <Nazione>\n')
        # DATA
        #f_invoice.write('   </Nazione>\n')

        #f_invoice.write('  </StabileOrganizzazione>\n')
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
        # TODO Usare la tabella TD01 Fattura TD04 Nota di credito
        f_invoice.write('   </TipoDocumento>\n')

        # 2.1.1.2
        f_invoice.write('   <Divisa>\n')
        # TODO EUR
        f_invoice.write('   </Divisa>\n')

        # 2.1.1.3
        f_invoice.write('   <Data>\n')
        # TODO Data fattura ISO format YYYY-MM-DD
        f_invoice.write('   </Data>\n')

        # 2.1.1.4
        f_invoice.write('   <Numero>\n')
        # TODO Serie - Numero
        f_invoice.write('   </Numero>\n')

        # 2.1.1.5
        #f_invoice.write('   <DatiRitenuta>\n')
        # 2.1.1.5.1 TipoRitenuta
        # 2.1.1.5.1 ImportoRitenuta
        # 2.1.1.5.1 AliquotaRitenuta
        # 2.1.1.5.1 CausaleRitenuta
        #f_invoice.write('   </DatiRitenuta>\n')

        # TODO Valutare questione bollo:
        # 2.1.1.6
        f_invoice.write('   <DatiBollo>\n')        
        
        # 2.1.1.6.1 
        f_invoice.write('    <BolloVirtuale>\n')        
        # TODO
        f_invoice.write('    </BolloVirtuale>\n')        

        # 2.1.1.6.2
        f_invoice.write('    <ImportoBollo>\n')        
        # TODO
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
        # VALUTARE: Abbuoni attivi / passivi:
        # 2.1.1.8
        f_invoice.write('   <ScontoMaggiorazione>\n')        
        
        # 2.1.1.8.1 
        f_invoice.write('    <Tipo>\n')        
        # TODO
        f_invoice.write('    </Tipo>\n')        

        # ---------------------------------------------------------------------
        # 2.1.1.8.2     >>> Alternative 2.1.1.8.3
        f_invoice.write('    <Percentuale>\n')        
        # TODO
        f_invoice.write('    </Percentuale>\n')        

        # ---------------------------------------------------------------------
        # 2.1.1.8.3     >>> Alternative 2.1.1.8.2
        f_invoice.write('    <Importo>\n')        
        # TODO
        f_invoice.write('    </Importo>\n')        

        f_invoice.write('   </ScontoMaggiorazione>\n')        
        
        # 2.1.1.9
        f_invoice.write('   <ImportoTotaleDocumento>\n')        
        # TODO Totale IVATO (al netto di sconti)
        f_invoice.write('   </ImportoTotaleDocumento>\n')        
        
        # 2.1.1.10
        f_invoice.write('   <Arrotondamento>\n')        
        # TODO
        f_invoice.write('   </Arrotondamento>\n')        

        # 2.1.1.11
        f_invoice.write('   <Causale>\n')        
        # TODO Causale del documento (testo)
        f_invoice.write('   </Causale>\n')        

        # 2.1.1.12
        #f_invoice.write('   <Art73>\n')        
        # TODO
        #f_invoice.write('   </Art73>\n')        
        
        f_invoice.write('  </DatiGeneraliDocumento>\n')

        # ---------------------------------------------------------------------        
        # RIFERIMENTO ORDINE:
        # ---------------------------------------------------------------------        
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
        # ---------------------------------------------------------------------        

        # ---------------------------------------------------------------------        
        # RIFERIMENTO CONTRATTO:
        # ---------------------------------------------------------------------        
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
        # ---------------------------------------------------------------------        

        # ---------------------------------------------------------------------        
        # RIFERIMENTO DDT:
        # ---------------------------------------------------------------------        
        # 2.1.8
        f_invoice.write('   <DatiDDT>\n')
        
        # 2.1.8.1 
        f_invoice.write('    <NumeroDDT>\n')
        # TODO Numero documento
        f_invoice.write('    </NumeroDDT>\n')
                    
        # 2.1.8.2
        f_invoice.write('    <DataDDT>\n')
        # TODO ISO   
        f_invoice.write('    </DataDDT>\n')

        # 2.1.8.3
        f_invoice.write('    <RiferimentoNumeroLinea>\n')
        # TODO Numero linea                   
        f_invoice.write('    </RiferimentoNumeroLinea>\n')
        
        f_invoice.write('   </DatiDDT>\n')
        # ---------------------------------------------------------------------        

        # ---------------------------------------------------------------------        
        # FATTURA ACCOMPAGNATORIA:
        # ---------------------------------------------------------------------        
        """
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
        """
        # ---------------------------------------------------------------------        


        # 2.2
        f_invoice.write(' <DatiBeniServizi>\n')

        # 2.2.1
        f_invoice.write('  <DettaglioLinee>\n')

        # 2.2.1.1
        f_invoice.write('   <NumeroLinea>\n')
        # TODO 
        f_invoice.write('   </NumeroLinea>\n')

        # Spesa accessoria (condizionale):
        # 2.2.1.2 # Solo se SC PR AB AC (spesa accessoria)
        f_invoice.write('   <TipoCessionePrestazione>\n')
        # TODO AB(uono)  AC(essoria)  SC(onto) PR(remio)
        f_invoice.write('   </TipoCessionePrestazione>\n')

        # 2.2.1.3
        f_invoice.write('   <CodiceArticolo>\n')

        # 2.2.1.3.1 # PROPRIETARIO EAN TARIC SSC
        f_invoice.write('    <CodiceTipo>\n')
        # TODO PROPRIETARIO o EAN (o altri)
        f_invoice.write('    </CodiceTipo>\n')

        # 2.2.1.3.2 # come da punto precedente
        f_invoice.write('    <CodiceValore>\n')
        # TODO CODICE
        f_invoice.write('    </CodiceValore>\n')

        f_invoice.write('   </CodiceArticolo>\n')

        # 2.2.1.4
        f_invoice.write('   <Descrizione>\n')
        # TODO 
        f_invoice.write('   </Descrizione>\n')

        # 2.2.1.5
        f_invoice.write('   <Quantita>\n')
        # TODO
        f_invoice.write('   </Quantita>\n')

        # 2.2.1.6
        f_invoice.write('   <UnitaMisura>\n')
        # TODO 
        f_invoice.write('   </UnitaMisura>\n')

        # Servizi: Opzionale:
        # 2.2.1.7 # Per Servizi
        #f_invoice.write('   <DataInizioPeriodo>\n')
        # TODO
        #f_invoice.write('   </DataInizioPeriodo>\n')

        # 2.2.1.8 # Per Servizi
        #f_invoice.write('   <DataFinePeriodo>\n')
        # TODO
        #f_invoice.write('   </DataFinePeriodo>\n')

        # 2.2.1.9 # Anche negativo # Vedi 2.2.1.2
        f_invoice.write('   <PrezzoUnitario>\n')
        # TODO prezzo unitario, totale sconto (anche negativo)
        f_invoice.write('   </PrezzoUnitario>\n')

        # ---------------------------------------------------------------------
        # Sconto manuale (opzionale:
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
        # ---------------------------------------------------------------------


        # 2.2.1.11
        f_invoice.write('   <PrezzoTotale>\n')
        # TODO Subtotale
        f_invoice.write('   </PrezzoTotale>\n')

        # 2.2.1.12
        f_invoice.write('   <AliquotaIVA>\n')
        # TODO percentuale 22.00
        f_invoice.write('   </AliquotaIVA>\n')

        # 2.2.1.13
        #f_invoice.write('   <Ritenuta>\n')
        # TODO 
        #f_invoice.write('   </Ritenuta>\n')

        # Se IVA 0 obbligatorio:
        # 2.2.1.14
        f_invoice.write('   <Natura>\n')
        # TODO Descrizione eventuale esenzione
        f_invoice.write('   </Natura>\n')

        # 2.2.1.15
        #f_invoice.write('   <RiferimentoAmministrazione>\n')
        # TODO
        #f_invoice.write('   </RiferimentoAmministrazione>\n')

        # 2.2.1.16
        """
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
        """
        
        f_invoice.write(' </DettaglioLinee>\n')

        # Elenco riepilogativo IVA del documento (1:N):
        # 2.2.2
        f_invoice.write('  <DatiRiepilogo>\n')

        # 2.2.2.1        
        f_invoice.write('   <AliquotaIVA>\n')
        # TODO 22.00
        f_invoice.write('   </AliquotaIVA>\n')

        # 2.2.2.2 # Tabella
        f_invoice.write('   <Natura>\n')
        # TODO 
        f_invoice.write('   </Natura>\n')

        # 2.2.2.3
        #f_invoice.write('   <SpeseAccessorie>\n')
        # TODO 
        #f_invoice.write('   </SpeseAccessorie>\n')

        # 2.2.2.4
        #f_invoice.write('   <Arrotondamento>\n')
        # TODO 
        #f_invoice.write('   </Arrotondamento>\n')

        # 2.2.2.5
        f_invoice.write('   <ImponibileImporto>\n')
        # TODO Base imponibile
        f_invoice.write('   </ImponibileImporto>\n')

        # 2.2.2.6
        f_invoice.write('   <Imposta>\n')
        # TODO Imposta totale
        f_invoice.write('   </Imposta>\n')

        # 2.2.2.7
        f_invoice.write('   <EsigibilitaIVA>\n')
        # TODO I(mmediata) D(ifferita) S(cissione)
        f_invoice.write('   </EsigibilitaIVA>\n')

        # 2.2.2.8
        f_invoice.write('   <RiferimentoNormativo>\n')
        # Se natura valorizzato
        f_invoice.write('   </RiferimentoNormativo>\n')

        f_invoice.write('  </DatiRiepilogo>\n')

        f_invoice.write(' </DatiBeniServizi>\n')

        # 2.3
        """
        f_invoice.write(' <DatiVeicoli>\n')

        # 2.3.1
        f_invoice.write('  <Data>\n')
        f_invoice.write('  </Data>\n')

        # 2.3.1
        f_invoice.write('  <TotalePercorso>\n')
        f_invoice.write('  </TotalePercorso>\n')

        f_invoice.write(' </DatiVeicoli>\n')
        """

        # ---------------------------------------------------------------------
        # Pagamento:
        # ---------------------------------------------------------------------
        # 2.4
        f_invoice.write(' <DatiPagamento>\n')

        # 2.4.1
        f_invoice.write('  <CondizioniPagamento>\n')
        # TODO tabelle TP01 a rate TP02 pagamento completo TP03 anticipo
        f_invoice.write('  </CondizioniPagamento>\n')
        
        # Elenco rate:
        # 2.4.2
        f_invoice.write('  <DettaglioPagamento>\n')

        # 2.4.2.1 (0.1)
        f_invoice.write('   <Beneficiario>\n')
        # TODO se differente dal cedente
        f_invoice.write('   </Beneficiario>\n')
        
        # 2.4.2.2
        f_invoice.write('   <ModalitaPagamento>\n')
        # TODO Tabella MP
        f_invoice.write('   </ModalitaPagamento>\n')
        
        # 2.4.2.3 (0.1)
        f_invoice.write('   <DataRiferimentoTerminiPagamento>\n')
        # TODO 
        f_invoice.write('   </DataRiferimentoTerminiPagamento>\n')
        
        # 2.4.2.4 (0.1)
        f_invoice.write('   <GiorniTerminiPagamento>\n')
        # TODO 
        f_invoice.write('   </GiorniTerminiPagamento>\n')
        
        # 2.4.2.5 (0.1)
        f_invoice.write('   <DataScadenzaPagamento>\n')
        # TODO 
        f_invoice.write('   </DataScadenzaPagamento>\n')
        
        # 2.4.2.6
        f_invoice.write('   <ImportoPagamento>\n')
        # TODO 
        f_invoice.write('   </ImportoPagamento>\n')

        # ---------------------------------------------------------------------
        # Ufficio postale:        
        # ---------------------------------------------------------------------
        """
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
        """
        # ---------------------------------------------------------------------
        
        # 2.4.2.12 (0.1)
        f_invoice.write('   <IstitutoFinanziario>\n')
        f_invoice.write('   </IstitutoFinanziario>\n')
        
        # 2.4.2.13 (0.1)
        f_invoice.write('   <IBAN>\n')
        f_invoice.write('   </IBAN>\n')
        
        # 2.4.2.14 (0.1)
        f_invoice.write('   <ABI>\n')
        f_invoice.write('   </ABI>\n')
        
        # 2.4.2.15 (0.1)
        f_invoice.write('   <CAB>\n')
        f_invoice.write('   </CAB>\n')
        
        # 2.4.2.16 (0.1)
        f_invoice.write('   <BIC>\n')
        f_invoice.write('   </BIC>\n')

        # ---------------------------------------------------------------------
        # Pagamento anticipato:        
        # 2.4.2.17
        """
        f_invoice.write('   <ScontoPagamentoAnticipato>\n')
        # TODO 
        f_invoice.write('   </ScontoPagamentoAnticipato>\n')
        
        # 2.4.2.18
        f_invoice.write('   <DataLimitePagamentoAnticipato>\n')
        # TODO 
        f_invoice.write('   </DataLimitePagamentoAnticipato>\n')
        
        # 2.4.2.19
        f_invoice.write('   <PenalitaPagamentiRitardati>\n')
        # TODO 
        f_invoice.write('   </PenalitaPagamentiRitardati>\n')
        
        # 2.4.2.20
        f_invoice.write('   <DataDecorrenzaPenale>\n')
        # TODO 
        f_invoice.write('   </DataDecorrenzaPenale>\n')
        
        # 2.4.2.21
        f_invoice.write('   <CodicePagamento>\n')
        # TODO 
        f_invoice.write('   </CodicePagamento>\n')
        """
        # ---------------------------------------------------------------------


        f_invoice.write('  </DettaglioPagamento>\n')
        f_invoice.write(' </DatiPagamento>\n')
        # ---------------------------------------------------------------------


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
