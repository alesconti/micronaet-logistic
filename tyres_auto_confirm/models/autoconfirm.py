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
import pdb
import logging
from odoo import api, fields, models, tools, exceptions, SUPERUSER_ID
from odoo.tools.translate import _
from dateutil.easter import easter
_logger = logging.getLogger(__name__)


class AutoConfirmTemplate(models.Model):
    """ Auto confirm working template
    """
    _name = 'auto.confirm.template'
    _description = 'Working template'
    _rec_name = 'name'
    _order = 'name'

    name = fields.Char(string='Name', size=35, required=True)
    note = fields.Text(string='Note')


class AutoConfirmTemplateLine(models.Model):
    """ Auto confirm working template line
    """
    _name = 'auto.confirm.template.line'
    _description = 'Working line'
    _rec_name = 'day'
    _order = 'day, from_hour'

    day = fields.Selection(
        string='Day',
        selection=[
            ('mon', 'Monday'),
            ('tue', 'Tuesday'),
            ('wed', 'Wednesday'),
            ('thu', 'Thursday'),
            ('fri', 'Friday'),
            ('sat', 'Saturday'),
            ('sun', 'Sunday'),
        ],
        required=True,
    )
    from_hour = fields.Float(
        string='From hour (morning)',
        required=True,
    )
    to_hour = fields.Float(
        string='From hour (morning)',
        required=True,
    )
    template_id = fields.Many2one(
        comodel_name='auto.confirm.template',
        string='Template',
    )


class AutoConfirmWorkingRelations(models.Model):
    """ Auto confirm working template relations
    """
    _inherit = 'auto.confirm.template'

    day_ids = fields.One2many(
        comodel_name='auto.confirm.template.line',
        inverse_name='template_id',
        string='Days'
    )


class AutoConfirmPeriod(models.Model):
    """ Auto period
    """
    _name = 'auto.confirm.period'
    _description = 'Auto confirm period'
    _rec_name = 'name'
    _order = 'passed, from_date'

    name = fields.Char(string='Name', size=35)
    passed = fields.Boolean(
        string='Passed',
        help='If range date is passed remove from list'
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        )
    from_date = fields.Date(
        string='From date',
        required=True)
    to_date = fields.Date(
        string='To date',
        required=True)


class ResCompany(models.Model):
    """ Add configuration part
    """
    _inherit = 'res.company'

    # Button event:
    @api.multi
    def setup_this_year(self):
        """ Create this year date
        """
        period_pool = self.env['auto.confirm.period']
        pdb.set_trace()
        year = fields.Datetime.now()[:4]

        date_excluded = {
            '01-01': 'Capodanno',
            '01-06': 'Befana',
            '04-25': '25 Aprile',
            '05-01': 'I Maggio',
            '06-02': 'Festa della Repubblica',
            '08-15': 'Ferragosto',
            '12-08': 'Immacolata concezione',
            ('12-25', '12-26'): 'Natale',
        }
        easter_date = easter(int(year))
        easter_record = '%02d-%02d' % (easter_date.month, easter_date.day)
        date_excluded[easter_record] = 'Pasqua'

        if self.patron_day:
            patron_day = self.patron_day
            date_excluded[patron_day] = 'Festa patronale'

        for date in sorted(date_excluded):
            if len(date) == 2:
                from_date, to_date = date
            else:
                from_date = to_date = date
            name = date_excluded[date]
            periods = period_pool.search([('from_date', '=', from_date)])
            data = {
                'name': name,
                'company_id': self.env.user.company_id.id,
                'from_date': '{}-{}'.format(year, from_date),
                'to_date': '{}-{}'.format(year, to_date),
                }
            if periods:
                period_pool.write(data)
            else:
                period_pool.create(data)
        return True

    @api.multi
    def enable_auto_confirm(self):
        """ Create this year date
        """
        return self.write({'auto_state': 'enabled'})

    @api.multi
    def disable_auto_confirm(self):
        """ Create this year date
        """
        return self.write({'auto_state': 'disabled'})

    @api.multi
    def check_still_enable(self):
        """ Check if operation need to be still active
        """
        return True

    @api.multi
    def check_exclude_now_period(self):
        """ Check if now can enabled the auto button
        """
        return self.write({'auto_enabled': False})

    # Default function:
    '''@api.multi
    def get_default_auto_group(self):
        """ Init setup for basic management group
        """
        group_id = self.env.ref(
            'tyres_auto_confirm.group_auto_confirm_manager').id
        return group_id'''

    # Columns:
    patron_day = fields.Char(
        string='Patron day',
        help='Write patron day in format MM-DD, ex.: 02-15 for 15 feb.',
        default='02-15',
    )
    auto_end_period = fields.Datetime(
        string='End date time',
        help='When enabled this date time is the end of che auto period'
             '(used to check if the button need to be disabled)'
        )
    auto_period = fields.Integer(
        string='Auto period (min.)',
        help='Auto period for enable auto go in delivery',
        default=30,
        required=True)
    auto_print = fields.Integer(
        string='Auto print block',
        help='Every list of ready order will be print with block of X items',
        default=3,
        required=True)
    auto_wait = fields.Integer(
        string='Auto print wait',
        help='All printable orders will be spliced in blocks, every block wait'
             'X seconds before print next',
        default=10,
        required=True)
    auto_group = fields.Many2one(
        comodel_name='res.groups',
        string='Auto group',
        help='Group for user that can manage auto button',
        # default=lambda s: s.get_default_auto_group(),
        )
    date_ids = fields.One2many(
        comodel_name='auto.confirm.period',
        inverse_name='company_id',
        string='Exclude date',
        help='Exclude date list'
    )
    template_id = fields.Many2one(
        comodel_name='auto.confirm.template',
        string='Template',
        help='Template for working period'
        )
    auto_state = fields.Selection([
        ('enabled', 'Enabled'),
        ('disabled', 'Disabled'),
        ], string='State', default='disabled',
        help='Orders go in delivery when ready automatically',
    )
