# -*- coding: utf-8 -*-
###############################################################################
#
# ODOO (ex OpenERP) 
# Open Source Management Solution
# Copyright (C) 2001-2015 Micronaet S.r.l. (<http://www.micronaet.it>)
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
import erppeek
import ConfigParser
from datetime import datetime, timedelta


# -----------------------------------------------------------------------------
# Read configuration parameter:
# -----------------------------------------------------------------------------
cfg_file = os.path.expanduser('../odoo.cfg')

config = ConfigParser.ConfigParser()
config.read([cfg_file])
dbname = config.get('dbaccess', 'dbname')
user = config.get('dbaccess', 'user')
pwd = config.get('dbaccess', 'pwd')
server = config.get('dbaccess', 'server')
port = config.get('dbaccess', 'port')   # verify if it's necessary: getint

now = datetime.now().strftime('%Y-%m-%d 00:00:00')

# -----------------------------------------------------------------------------
# Connect to ODOO:
# -----------------------------------------------------------------------------
odoo = erppeek.Client(
    'http://%s:%s' % (
        server, port), 
    db=dbname,
    user=user,
    password=pwd,
    )
order_pool = odoo.model('sale.order')

order_ids = order_pool.search([
    #('stats_level', '=', 'unset'), # Remove for ALL
    ('logistic_state', 'not in', ('draft', 'order')),
    ('write_date', '>=', now),
    ])

total = len(order_ids)
print 'Connect to ODOO: Update >= %s [Tot. %s]' % (now, total)

i = 0
for order in order_pool.browse(order_ids):
    i += 1 
    if i % 20 == 0:
        print 'Updated %s on %s' % (i, total)
    order.sale_order_refresh_margin_stats()
