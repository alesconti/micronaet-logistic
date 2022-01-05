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
import pdb
import sys
import erppeek
import xlrd
try:
    import ConfigParser as configparser
except:
    import configparser


# -----------------------------------------------------------------------------
# Read configuration parameter:
# -----------------------------------------------------------------------------
cfg_file = os.path.expanduser('../openerp.cfg')

config = configparser.ConfigParser()
config.read([cfg_file])
dbname = config.get('dbaccess', 'dbname')
user = config.get('dbaccess', 'user')
pwd = config.get('dbaccess', 'pwd')
server = config.get('dbaccess', 'server')
port = config.get('dbaccess', 'port')   # verify if it's necessary: getint

# Static parameter:
row_start = 1
filename = './Produttori GommeCerchi.xlsx'

# -----------------------------------------------------------------------------
# Connect to ODOO:
# -----------------------------------------------------------------------------
print('Connect to ODOO')
odoo = erppeek.Client(
    'http://%s:%s' % (
        server, port),
    db=dbname,
    user=user,
    password=pwd,
    )

brand_pool = odoo.model('mmac_brand')
country_pool = odoo.model('res.country')

try:
   WB = xlrd.open_workbook(filename)
except:
   sys.exit()

WS = WB.sheet_by_index(0)

i = 0
pdb.set_trace()
for row in range(row_start, WS.nrows):
    i += 1
    if i == 7:
        pdb.set_trace()
    brand = WS.cell(row, 0).value.upper()
    owner = WS.cell(row, 1).value
    street = WS.cell(row, 2).value
    city = WS.cell(row, 3).value
    zipcode = str(WS.cell(row, 4).value)
    country_name = WS.cell(row, 5).value.strip()
    if country_name == 'USA':
        country_name = 'Stati Uniti'

    if zipcode.endswith('.0'):
        zipcode = zipcode[:-2]

    brand_ids = brand_pool.search([
        ('name', '=', brand),
    ])
    if not brand_ids:
        print('%s. [ERR] Brand not found: %s' % (i, brand))
        continue

    data = {
        'owner': owner,
        'street': street,
        'city': city,
        'zipcode': zipcode,
    }

    if country_name == 'Italia':
        country_ids = [109]
    else:
        country_ids = country_pool.search([
            ('name', '=', country_name),
        ])
    if country_ids:
        data['country_id'] = country_ids[0]
    else:
        print('%s. [ERR] Country not found: %s' % (i, country_name))

    brand_pool.write(brand_ids, data)
    # print('%s. [INFO] Brand updated: %s' % (i, brand))
