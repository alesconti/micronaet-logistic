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
import openerp
import logging
from odoo import models, fields
from odoo.tools.translate import _


_logger = logging.getLogger(__name__)

class StockPickingRefundDocumentWizard(models.TransientModel):
    ''' Wizard for generate refund document
    '''
    _name = 'stock.picking.refund.wizard'

    # -------------------------------------------------------------------------
    # Wizard button event:
    # -------------------------------------------------------------------------
    def create_refund(self, cr, uid, ids, context=None):
        ''' Event for button done
        '''
        if context is None: 
            context = {}        

        # Pool used:        
        picking_pool = self.env['stock.picking']
        move_pool = self.env['stock.move']
        quant_pool = self.env['stock.quant']

        # Parameter from wizard:
        wiz_browse = self.browse(cr, uid, ids, context=context)[0]        
        from_picking = wiz_browse.picking_id
        
        to_picking_id = picking_pool.create({
            # TODO
            }).id
            
        for line in wiz_browse.line_ids:
            if line.refund_qty <= 0:
                continue # no refund line

            move_id = move_pool.create({
                'picking_id': to_picking_id,
                # TODO                 
                }).id

        # ---------------------------------------------------------------------
        # Return view:
        # ---------------------------------------------------------------------
        #model_pool = self.pool.get('ir.model.data')
        #view_id = model_pool.get_object_reference(
        #    'module_name', 'view_name')[1]
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Refund document'),
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_id': to_picking_id,
            'res_model': 'stock.picking',
            'view_id': False,#view_id,
            'views': [(False, 'form'), (False, 'tree')],
            'domain': [('id', '=', to_picking_id)],
            'context': self.env.context,
            'target': 'current',
            'nodestroy': False,
            }        

    # -------------------------------------------------------------------------
    # Columns:
    # -------------------------------------------------------------------------
    picking_id = fields.Many2one(
        'stock.picking', 'From document', required=True)

class StockPickingRefundDocumentLineWizard(models.TransientModel):
    ''' Wizard for generate refund document
    '''
    _name = 'stock.picking.refund.line.wizard'
    
    # -------------------------------------------------------------------------
    # Columns:
    # -------------------------------------------------------------------------
    wizard_id = fields.Many2one(
        'stock.picking.refund.wizard', 'Wizard')
    product_id = fields.Many2one(
        'product.product', 'Product')
    product_qty = fields.Float('Q. origin', digits=(16, 2))
    refund_qty = fields.Float('Q. refund', digits=(16, 2))

class StockPickingRefundDocumentWizard(models.TransientModel):
    ''' Wizard for generate refund document
    '''
    _inherit = 'stock.picking.refund.wizard'

    # -------------------------------------------------------------------------
    # Columns:
    # -------------------------------------------------------------------------
    line_ids = fields.One2many(
        'stock.picking.refund.line.wizard', 'wizard_id', 
        'Picking line')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
