#!/usr/bin/python
# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2001-2018 Micronaet S.r.l. (<https://micronaet.com>)
#    Developer: Nicola Riolini @thebrush 
#               (<https://it.linkedin.com/in/thebrush>)
#    Copyright (C) 2014 Abstract (http://www.abstract.it)
#    @author Davide Corio <davide.corio@abstract.it>
#    Copyright (C) 2014 Agile Business Group (http://www.agilebg.com)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import fields, models, api
from odoo import _

class AccountFiscalPosition(models.Model):
    """ Model name: Fiscal position
    """
    
    _inherit = 'account.fiscal.position'
    
    # -------------------------------------------------------------------------
    #                                   COLUMNS:
    # -------------------------------------------------------------------------
    sequence_id = fields.Many2one('ir.sequence', 'Sequence', required=True)


class StockPickingCarriageCondition(models.Model):

    _name = "stock.picking.carriage_condition"
    _description = "Carriage Condition"

    name = fields.Char(string='Carriage Condition', required=True)
    note = fields.Text(string='Note')

class StockPickingGoodsDescription(models.Model):

    _name = 'stock.picking.goods_description'
    _description = "Description of Goods"

    name = fields.Char(string='Description of Goods', required=True)
    note = fields.Text(string='Note')

class StockPickingTransportationReason(models.Model):

    _name = 'stock.picking.transportation_reason'
    _description = 'Reason for Transportation'

    name = fields.Char(string='Reason For Transportation', required=True)
    note = fields.Text(string='Note')

class StockPickingTransportationMethod(models.Model):

    _name = 'stock.picking.transportation_method'
    _description = 'Method of Transportation'

    name = fields.Char(string='Method of Transportation', required=True)
    note = fields.Text(string='Note')


class StockPicking(models.Model):
    ''' Add extra fields to keep picking as DDT or Invoice:
    '''
    _inherit = 'stock.picking'

    @api.multi
    def assign_invoice_number(self):
        ''' Assign invoice number depend on fiscal position and parameter in
            partner configuration
        '''
        for picking in self:
            # Load partner sequence (depend on fiscal position)
            partner = picking.partner_id
            sequence = partner.property_account_position_id.sequence_id
            sequence_number = sequence.next_by_id()
            if picking.stock_mode == 'out':
                picking.write({
                    'invoice_number': sequence_number,
                    'invoice_date': fields.Datetime.now(),    
                    })
            else: # 'nc' >> Credit note        
                sequence_number = sequence_number.replace('FT', 'NC')
                picking.write({
                    'invoice_number': sequence_number,
                    'invoice_date': fields.Datetime.now(),
                    })
            
        return True
                
    @api.multi
    def assign_ddt_number(self):
        ''' Assign DDt number depend on fiscal position and parameter in
            partner configuration
        '''
        # TODO Manage sequence from fiscal position
        for picking in self:
            if picking.stock_mode == 'out':
                picking.write({
                    'ddt_number': self.env['ir.sequence'].next_by_code(
                        'stock.picking.ddt.sequence'),
                    'ddt_date': fields.Datetime.now(),    
                    })
            else: # in >> Refund value:
                picking.write({
                    'refund_number': self.env['ir.sequence'].next_by_code(
                        'stock.picking.refund.sequence'),
                    'refund_date': fields.Datetime.now(),    
                    })
        return True

    # -------------------------------------------------------------------------
    # Columns: 
    # -------------------------------------------------------------------------
    stock_mode = fields.Selection([
        ('in', 'Refund document'),
        ('out', 'Delivery document'),
        ], string='Stock mode', default='out')
    refund_origin_id = fields.Many2one(
        'stock.picking', string='Back document refunded')
    refunded_ids = fields.One2many(
        'stock.picking', refund_origin_id, string='Document refunded this BC')
        
        
    refund_number = fields.Char('Refund number')
    refund_date = fields.Datetime('Refund date')
    ddt_number = fields.Char('DDT number')
    ddt_date = fields.Datetime('DDT date')
    invoice_number = fields.Char('Invoice number') 
    invoice_date = fields.Datetime('Invoice date')

    carriage_condition_id = fields.Many2one(
        'stock.picking.carriage_condition', string='Carriage Condition')
    goods_description_id = fields.Many2one(
        'stock.picking.goods_description', string='Description of Goods')
    transportation_reason_id = fields.Many2one(
        'stock.picking.transportation_reason',
        string='Reason for Transportation')
    transportation_method_id = fields.Many2one(
        'stock.picking.transportation_method',
        string='Method of Transportation')
    carrier_id = fields.Many2one(
        'res.partner', string='Carrier')
    parcels = fields.Integer('Parcels')
    weight = fields.Float('Weight')

