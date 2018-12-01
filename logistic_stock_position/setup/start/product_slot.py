#!/usr/bin/python
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
import sys
import erppeek

cfg_file = os.path.expanduser('../odoo.cfg')

try: # Pyton 2.7
    import ConfigParser
    config = ConfigParser.ConfigParser()
except: # Python 3 (pip install ConfigParser)
    import configparser
    config = configparser.ConfigParser()

# -----------------------------------------------------------------------------
# From config file:
# -----------------------------------------------------------------------------
config.read([cfg_file])
dbname = config.get('dbaccess', 'dbname')
user = config.get('dbaccess', 'user')
pwd = config.get('dbaccess', 'pwd')
server = config.get('dbaccess', 'server')
port = config.get('dbaccess', 'port')   # verify if it's necessary: getint
        
# -----------------------------------------------------------------------------
# Connect to ODOO:
# -----------------------------------------------------------------------------
odoo = erppeek.Client(
    'http://%s:%s' % (server, port), 
    db=dbname,
    user=user,
    password=pwd,
    )
slot_pool = odoo.model('stock.location.slot')
template_pool = odoo.model('product.template')

# Create slot database:
slot_db = {}
slot_ids = slot_pool.search([('mode', '=', 'stock')])
for slot in slot_pool.browse(slot_ids):
    slot_db[slot.name] = slot.id
    
def clean(value): 
    ''' Clean value
    '''
    value = value or ''
    return value.strip().strip('\'').strip('"').strip()

i = 0
for line in open('./link.csv'):
    i += 1
    if i == 1:
        continue
        
    row = line.split(',')
    default_code = clean(row[1])
    slot = clean(row[3])
    if slot not in slot_db:
        print '%s. [ERROR] slot not found: %s' % (i, slot)
        continue
    template_ids = template_pool.search([
        ('default_code', '=', default_code)])
    if not template_ids:
        print '%s. [ERROR] product code not found: %s' % (i, default_code)
        continue
    template_pool.write(template_ids, {
        'default_stock_id': slot_db[slot]})
    print '%s. [INFO] Link %s to slot %s' % (i, default_code, slot)
    continue

