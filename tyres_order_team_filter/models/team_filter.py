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

class ResUsers(models.Model):
    """ Model name: Res Users
    """
    
    _inherit = 'res.users'

    # -------------------------------------------------------------------------
    # COLUMNS:
    # -------------------------------------------------------------------------
    my_group_id = fields.Many2one('res.groups', 'My Menu group')
    my_action_id = fields.Many2one('ir.actions.act_window', 'My action')
    my_menu_id = fields.Many2one('ir.ui.menu', 'My menu')    
    team_ids = fields.Many2many(
        'crm.team', relation='rel_user_team', 
        column1='user_id', column2='team_id', 
        string='Teams', help='Select team for filter orders')
    # -------------------------------------------------------------------------

    @api.multi
    def update_my_menu(self, ):
        ''' Update my menu block
        '''        
        self.ensure_one()
        user = self[0]
        
        # Pool used:
        group_pool = self.env['res.groups']
        action_pool = self.env['ir.actions.act_window']
        menu_pool = self.env['ir.ui.menu']
        
        team_ids = [item.id for item in user.team_ids]
        domain = str([('team_id', 'in', team_ids)])

        # ---------------------------------------------------------------------        
        # 1. Create or get my group:
        # ---------------------------------------------------------------------        
        # All group has this category owner:
        category_id = self.env.ref(
            'tyres_logistic_management.ir_module_category_logistic_my').id
        if user.my_group_id:
            my_group_id = user.my_group_id.id

            # Update some fields:
            user.my_group_id.write({
                'users': [(6, 0, [user.id, ])],
                'category_id': category_id,
                })
        else:
            my_group_id = group_pool.create({
                'name': _('My Order %s') % user.name,
                'comment': 'Group auto created from tyres_order_team_filter',
                'users': [(6, 0, [user.id, ])],
                'category_id': category_id,
                }).id
            user.my_group_id = my_group_id

        # ---------------------------------------------------------------------        
        # 2. Create or get my action
        # ---------------------------------------------------------------------        
        name = ''
        if user.my_action_id:
            my_action_id = user.my_action_id.id            

            # Update some fields:
            user.my_action_id.domain = domain # Update domain filter
            
        else:
            # Default action used to copy
            origin_action = self.env.ref(
                'tyres_logistic_management.action_sale_order_all_form')
            name = _('My %s') % origin_action.name
            my_action_id = action_pool.create({
                'name': name,
                'type': origin_action.type,
                'help': origin_action.help,
                'binding_model_id': origin_action.binding_model_id.id,
                'binding_type': origin_action.binding_type,
                'view_id': origin_action.view_id.id,
                'domain': domain,
                'context': origin_action.context,
                'res_id': origin_action.res_id,
                'res_model': origin_action.res_model,
                'src_model': origin_action.src_model,
                'target': origin_action.target,
                'view_mode': origin_action.view_mode,
                'view_type': origin_action.view_type,
                'usage': origin_action.usage,
                'limit': origin_action.limit,
                'search_view_id': origin_action.search_view_id.id,
                'filter': origin_action.filter,
                'auto_search': origin_action.auto_search,
                'multi': origin_action.multi,     
                }).id
            user.my_action_id = my_action_id

        # ---------------------------------------------------------------------        
        # 3. Create or get my menuitem
        # ---------------------------------------------------------------------        
        if not name:
            name = self.my_action_id.name

        if user.my_menu_id:
            my_menu_id = user.my_menu_id
        else:
            # Default action used to copy
            parent_menu = self.env.ref(
                'tyres_order_team_filter.menu_logistic_my_order_root')
            my_menu_id = menu_pool.create({
                'name': name,
                'active': True,
                'sequence': 10,
                'parent_id': parent_menu.id,
                'action': 'ir.actions.act_window,%s' % my_action_id,
                'groups_id': [(6, 0, [my_group_id])],
                #'parent_left'
                #'parent_right'
                #'web_icon': 
                }).id
            user.my_menu_id = my_menu_id
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
