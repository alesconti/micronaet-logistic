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

remove_char = ('\t', '\n')

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

# Supplier, suffix, defauls, SL x 5
database = [
    'AA0.A1.A', 'AC0.A1.A', 'BA0.A1.A', 'BC0.A1.A', 'CA0.A1.A', 'CC0.A1.A', 'DA0.A1.A', 'EA0.A1', 'EB0.B1', 'EC0.B1', 'FA0.B1', 'FB0.B1'
    'AA0.A1.B', 'AC0.A1.B', 'BA0.A1.B', 'BC0.A1.B', 'CA0.A1.B', 'CC0.A1.B', 'DA0.A1.B', 'EA0.A2', 'EB0.B2', 'EC0.B2', 'FA0.B2', 'FB0.B2'
    'AA0.A1.C', 'AC0.A1.C', 'BA0.A1.C', 'BC0.A1.C', 'CA0.A1.C', 'CC0.A1.C', 'DA0.A1.C', 'EA0.A3', 'EB0.B3', 'EC0.B3', 'FA0.B3', 'FB0.B3'
    'AA0.A2.A', 'AC0.A2.A', 'BA0.A2.A', 'BC0.A2.A', 'CA0.A2.A', 'CC0.A2.A', 'DA0.A2.A', 'EA0.A4', 'EB0.B4', 'EC0.B4', 'FA0.B4', 'FB0.B4'
    'AA0.A2.B', 'AC0.A2.B', 'BA0.A2.B', 'BC0.A2.B', 'CA0.A2.B', 'CC0.A2.B', 'DA0.A2.B',
    'AA0.A2.C', 'AC0.A2.C', 'BA0.A2.C', 'BC0.A2.C', 'CA0.A2.C', 'CC0.A2.C', 'DA0.A2.C',
    'AA0.A3.A', 'AC0.A3.A', 'BA0.A3.A', 'BC0.A3.A', 'CA0.A3.A', 'CC0.A3.A', 'DA0.A3.A',
    'AA0.A3.B', 'AC0.A3.B', 'BA0.A3.B', 'BC0.A3.B', 'CA0.A3.B', 'CC0.A3.B', 'DA0.A3.B',
    'AA0.A3.C', 'AC0.A3.C', 'BA0.A3.C', 'BC0.A3.C', 'CA0.A3.C', 'CC0.A3.C', 'DA0.A3.C',
    'AA1.A1.A', 'AB1.A1.A', 'AC1.A1.A', 'AD1.A1.A', 'BA1.A1.A', 'BB1.A1.A', 'BC1.A1.A', 'BD1.A1.A', 'CA1.A1.A', 'CB1.A1.A', 'CC1.A1.A', 'CDA.A1.A', 'DA1.A1.A', 'DB1.A1.A', 'EA1.A1', 'EB1.A1', 'EC1.A1', 'FA1.B1', 'FB1.B1'
    'AA1.A1.B', 'AB1.A1.B', 'AC1.A1.B', 'AD1.A1.B', 'BA1.A1.B', 'BB1.A1.B', 'BC1.A1.B', 'BD1.A1.B', 'CA1.A1.B', 'CB1.A1.B', 'CC1.A1.B', 'CDA.A1.B', 'DA1.A1.B', 'DB1.A1.B', 'EA1.A2', 'EB1.A2', 'EC1.A2.A', 'FA1.B2', 'FB1.B2'
    'AA1.A1.C', 'AB1.A1.C', 'AC1.A1.C', 'AD1.A1.C', 'BA1.A1.C', 'BB1.A1.C', 'BC1.A1.C', 'BD1.A1.C', 'CA1.A1.C', 'CB1.A1.C', 'CC1.A1.C', 'CDA.A1.C', 'DA1.A1.C', 'DB1.A1.C', 'EA1.A3', 'EB1.A3', 'EC1.A2.B', 'FA1.B3', 'FB1.B3'
    'AA1.A1.D', 'AB1.A1.D', 'AC1.A1.D', 'AD1.A1.D', 'BA1.A1.D', 'BB1.A1.D', 'BC1.A1.D', 'BD1.A1.D', 'CA1.A1.D', 'CB1.A1.D', 'CC1.A1.D', 'CDA.A1.D', 'DA1.A1.D', 'DB1.A1.D', 'EA1.A4', 'EB1.A4', 'EC1.A2.C', 'FA1.B4', 'FB1.B4'
    'AA1.B1.A', 'AB1.B1.A', 'AC1.B1.A', 'AD1.B1.A', 'BA1.B1.A', 'BB1.B1.A', 'BC1.B1.A', 'BD1.B1.A', 'CA1.B1.A', 'CB1.B1.A', 'CC1.B1.A', 'CDA.B1.A', 'DA1.B1.A', 'DB1.B1.A', 'EC1.A2.D', 'FA1.B5', 'FB1.B5'
    'AA1.B1.B', 'AB1.B1.B', 'AC1.B1.B', 'AD1.B1.B', 'BA1.B1.B', 'BB1.B1.B', 'BC1.B1.B', 'BD1.B1.B', 'CA1.B1.B', 'CB1.B1.B', 'CC1.B1.B', 'CDA.B1.B', 'DA1.B1.B', 'DB1.B1.B', 'EC1.A3.A', 'FA1.B6', 'FB1.B6'
    'AA1.B1.C', 'AB1.B1.C', 'AC1.B1.C', 'AD1.B1.C', 'BA1.B1.C', 'BB1.B1.C', 'BC1.B1.C', 'BD1.B1.C', 'CA1.B1.C', 'CB1.B1.C', 'CC1.B1.C', 'CDA.B1.C', 'DA1.B1.C', 'DB1.B1.C', 'EC1.A3.B',
    'AA1.B1.D', 'AB1.B1.D', 'AC1.B1.D', 'AD1.B1.D', 'BA1.B1.D', 'BB1.B1.D', 'BC1.B1.D', 'BD1.B1.D', 'CA1.B1.D', 'CB1.B1.D', 'CC1.B1.D', 'CDA.B1.D', 'DA1.B1.D', 'DB1.B1.D', 'EC1.A3.C',
    'AA1.A2.A', 'AB1.A2.A', 'AC1.A2.A', 'AD1.A2.A', 'BA1.A2.A', 'BB1.A2.A', 'BC1.A2.A', 'BD1.A2.A', 'CA1.A2.A', 'CB1.A2.A', 'CC1.A2.A', 'CDA.A2.A', 'DA1.A2.A', 'DB1.A2.A', 'EC1.A3.D',
    'AA1.A2.B', 'AB1.A2.B', 'AC1.A2.B', 'AD1.A2.B', 'BA1.A2.B', 'BB1.A2.B', 'BC1.A2.B', 'BD1.A2.B', 'CA1.A2.B', 'CB1.A2.B', 'CC1.A2.B', 'CDA.A2.B', 'DA1.A2.B', 'DB1.A2.B', 'EC1.A4.A',
    'AA1.A2.C', 'AB1.A2.C', 'AC1.A2.C', 'AD1.A2.C', 'BA1.A2.C', 'BB1.A2.C', 'BC1.A2.C', 'BD1.A2.C', 'CA1.A2.C', 'CB1.A2.C', 'CC1.A2.C', 'CDA.A2.C', 'DA1.A2.C', 'DB1.A2.C', 'EC1.A4.B',
    'AA1.A2.D', 'AB1.A2.D', 'AC1.A2.D', 'AD1.A2.D', 'BA1.A2.D', 'BB1.A2.D', 'BC1.A2.D', 'BD1.A2.D', 'CA1.A2.D', 'CB1.A2.D', 'CC1.A2.D', 'CDA.A2.D', 'DA1.A2.D', 'DB1.A2.D', 'EC1.A4.C',
    'AA1.B2.A', 'AB1.B2.A', 'AC1.B2.A', 'AD1.B2.A', 'BA1.B2.A', 'BB1.B2.A', 'BC1.B2.A', 'BD1.B2.A', 'CA1.B2.A', 'CB1.B2.A', 'CC1.B2.A', 'CDA.B2.A', 'DA1.B2.A', 'DB1.B2.A', 'EC1.A4.D',
    'AA1.B2.B', 'AB1.B2.B', 'AC1.B2.B', 'AD1.B2.B', 'BA1.B2.B', 'BB1.B2.B', 'BC1.B2.B', 'BD1.B2.B', 'CA1.B2.B', 'CB1.B2.B', 'CC1.B2.B', 'CDA.B2.B', 'DA1.B2.B', 'DB1.B2.B',
    'AA1.B2.C', 'AB1.B2.C', 'AC1.B2.C', 'AD1.B2.C', 'BA1.B2.C', 'BB1.B2.C', 'BC1.B2.C', 'BD1.B2.C', 'CA1.B2.C', 'CB1.B2.C', 'CC1.B2.C', 'CDA.B2.C', 'DA1.B2.C', 'DB1.B2.C',
    'AA1.B2.D', 'AB1.B2.D', 'AC1.B2.D', 'AD1.B2.D', 'BA1.B2.D', 'BB1.B2.D', 'BC1.B2.D', 'BD1.B2.D', 'CA1.B2.D', 'CB1.B2.D', 'CC1.B2.D', 'CDA.B2.D', 'DA1.B2.D', 'DB1.B2.D',
    'AA1.A3.A', 'AB1.A3.A', 'AC1.A3.A', 'AD1.A3.A', 'BA1.A3.A', 'BB1.A3.A', 'BC1.A3.A', 'BD1.A3.A', 'CA1.A3.A', 'CB1.A3.A', 'CC1.A3.A', 'CDA.A3.A', 'DA1.A3.A', 'DB1.A3.A',
    'AA1.A3.B', 'AB1.A3.B', 'AC1.A3.B', 'AD1.A3.B', 'BA1.A3.B', 'BB1.A3.B', 'BC1.A3.B', 'BD1.A3.B', 'CA1.A3.B', 'CB1.A3.B', 'CC1.A3.B', 'CDA.A3.B', 'DA1.A3.B', 'DB1.A3.B',
    'AA1.A3.C', 'AB1.A3.C', 'AC1.A3.C', 'AD1.A3.C', 'BA1.A3.C', 'BB1.A3.C', 'BC1.A3.C', 'BD1.A3.C', 'CA1.A3.C', 'CB1.A3.C', 'CC1.A3.C', 'CDA.A3.C', 'DA1.A3.C', 'DB1.A3.C',
    'AA1.A3.D', 'AB1.A3.D', 'AC1.A3.D', 'AD1.A3.D', 'BA1.A3.D', 'BB1.A3.D', 'BC1.A3.D', 'BD1.A3.D', 'CA1.A3.D', 'CB1.A3.D', 'CC1.A3.D', 'CDA.A3.D', 'DA1.A3.D', 'DB1.A3.D',
    'AA1.B3.A', 'AB1.B3.A', 'AC1.B3.A', 'AD1.B3.A', 'BA1.B3.A', 'BB1.B3.A', 'BC1.B3.A', 'BD1.B3.A', 'CA1.B3.A', 'CB1.B3.A', 'CC1.B3.A', 'CDA.B3.A', 'DA1.B3.A', 'DB1.B3.A',
    'AA1.B3.C', 'AB1.B3.C', 'AC1.B3.C', 'AD1.B3.C', 'BA1.B3.C', 'BB1.B3.C', 'BC1.B3.C', 'BD1.B3.C', 'CA1.B3.C', 'CB1.B3.C', 'CC1.B3.C', 'CDA.B3.C', 'DA1.B3.C', 'DB1.B3.C',
    'AA1.B3.D', 'AB1.B3.D', 'AC1.B3.D', 'AD1.B3.D', 'BA1.B3.D', 'BB1.B3.D', 'BC1.B3.D', 'BD1.B3.D', 'CA1.B3.D', 'CB1.B3.D', 'CC1.B3.D', 'CDA.B3.D', 'DA1.B3.D', 'DB1.B3.D',
    'AA1.A4.A', 'AB1.A4.A', 'AC1.A4.A', 'AD1.A4.A', 'BA1.A4.A', 'BB1.A4.A', 'BC1.A4.A', 'BD1.A4.A', 'CA1.A4.A', 'CB1.A4.A', 'CC1.A4.A', 'CDA.A4.A', 'DA1.A4.A', 'DB1.A4.A',
    'AA1.A4.B', 'AB1.A4.B', 'AC1.A4.B', 'AD1.A4.B', 'BA1.A4.B', 'BB1.A4.B', 'BC1.A4.B', 'BD1.A4.B', 'CA1.A4.B', 'CB1.A4.B', 'CC1.A4.B', 'CDA.A4.B', 'DA1.A4.B', 'DB1.A4.B',
    'AA1.A4.C', 'AB1.A4.C', 'AC1.A4.C', 'AD1.A4.C', 'BA1.A4.C', 'BB1.A4.C', 'BC1.A4.C', 'BD1.A4.C', 'CA1.A4.C', 'CB1.A4.C', 'CC1.A4.C', 'CDA.A4.C', 'DA1.A4.C', 'DB1.A4.C',
    'AA1.A4.D', 'AB1.A4.D', 'AC1.A4.D', 'AD1.A4.D', 'BA1.A4.D', 'BB1.A4.D', 'BC1.A4.D', 'BD1.A4.D', 'CA1.A4.D', 'CB1.A4.D', 'CC1.A4.D', 'CDA.A4.D', 'DA1.A4.D', 'DB1.A4.D',
    'AA1.B4.A', 'AB1.B4.A', 'AC1.B4.A', 'AD1.B4.A', 'BA1.B4.A', 'BB1.B4.A', 'BC1.B4.A', 'BD1.B4.A', 'CA1.B4.A', 'CB1.B4.A', 'CC1.B4.A', 'CDA.B4.A', 'DA1.B4.A', 'DB1.B4.A',
    'AA1.B4.B', 'AB1.B4.B', 'AC1.B4.B', 'AD1.B4.B', 'BA1.B4.B', 'BB1.B4.B', 'BC1.B4.B', 'BD1.B4.B', 'CA1.B4.B', 'CB1.B4.B', 'CC1.B4.B', 'CDA.B4.B', 'DA1.B4.B', 'DB1.B4.B',
    'AA1.B4.C', 'AB1.B4.C', 'AC1.B4.C', 'AD1.B4.C', 'BA1.B4.C', 'BB1.B4.C', 'BC1.B4.C', 'BD1.B4.C', 'CA1.B4.C', 'CB1.B4.C', 'CC1.B4.C', 'CDA.B4.C', 'DA1.B4.C', 'DB1.B4.C',
    'AA1.B4.D', 'AB1.B4.D', 'AC1.B4.D', 'AD1.B4.D', 'BA1.B4.D', 'BB1.B4.D', 'BC1.B4.D', 'BD1.B4.D', 'CA1.B4.D', 'CB1.B4.D', 'CC1.B4.D', 'CDA.B4.D', 'DA1.B4.D', 'DB1.B4.D',
    'AA1.A5.A', 'AB1.A5.A', 'AC1.A5.A', 'AD1.A5.A', 'BA1.A5.A', 'BB1.A5.A', 'BC1.A5.A', 'BD1.A5.A', 'CA1.A5.A', 'CB1.A5.A', 'CC1.A5.A', 'CDA.A5.A', 'DA1.A5.A', 'DB1.A5.A',
    'AA1.A5.B', 'AB1.A5.B', 'AC1.A5.B', 'AD1.A5.B', 'BA1.A5.B', 'BB1.A5.B', 'BC1.A5.B', 'BD1.A5.B', 'CA1.A5.B', 'CB1.A5.B', 'CC1.A5.B', 'CDA.A5.B', 'DA1.A5.B', 'DB1.A5.B',
    'AA1.A5.C', 'AB1.A5.C', 'AC1.A5.C', 'AD1.A5.C', 'BA1.A5.C', 'BB1.A5.C', 'BC1.A5.C', 'BD1.A5.C', 'CA1.A5.C', 'CB1.A5.C', 'CC1.A5.C', 'CDA.A5.C', 'DA1.A5.C', 'DB1.A5.C',
    'AA1.A5.D', 'AB1.A5.D', 'AC1.A5.D', 'AD1.A5.D', 'BA1.A5.D', 'BB1.A5.D', 'BC1.A5.D', 'BD1.A5.D', 'CA1.A5.D', 'CB1.A5.D', 'CC1.A5.D', 'CDA.A5.D', 'DA1.A5.D', 'DB1.A5.D',
    'AA1.B5.A', 'AB1.B5.A', 'AC1.B5.A', 'AD1.B5.A', 'BA1.B5.A', 'BB1.B5.A', 'BC1.B5.A', 'BD1.B5.A', 'CA1.B5.A', 'CB1.B5.A', 'CC1.B5.A', 'CDA.B5.A', 'DA1.B5.A', 'DB1.B5.A',
    'AA1.B5.B', 'AB1.B5.B', 'AC1.B5.B', 'AD1.B5.B', 'BA1.B5.B', 'BB1.B5.B', 'BC1.B5.B', 'BD1.B5.B', 'CA1.B5.B', 'CB1.B5.B', 'CC1.B5.B', 'CDA.B5.B', 'DA1.B5.B', 'DB1.B5.B',
    'AA1.B5.C', 'AB1.B5.C', 'AC1.B5.C', 'AD1.B5.C', 'BA1.B5.C', 'BB1.B5.C', 'BC1.B5.C', 'BD1.B5.C', 'CA1.B5.C', 'CB1.B5.C', 'CC1.B5.C', 'CDA.B5.C', 'DA1.B5.C', 'DB1.B5.C',
    'AA1.B5.D', 'AB1.B5.D', 'AC1.B5.D', 'AD1.B5.D', 'BA1.B5.D', 'BB1.B5.D', 'BC1.B5.D', 'BD1.B5.D', 'CA1.B5.D', 'CB1.B5.D', 'CC1.B5.D', 'CDA.B5.D', 'DA1.B5.D', 'DB1.B5.D',
    'AA1.A6.A', 'AB1.A6.A', 'AC1.A6.A',
    'AA1.A6.B', 'AB1.A6.B', 'AC1.A6.B',
    'AA1.A6.C', 'AB1.A6.C', 'AC1.A6.C',
    'AA1.A6.D', 'AB1.A6.D', 'AC1.A6.D',
    'AA1.B6.A', 'AB1.B6.A', 'AC1.B6.A',
    'AA1.B6.B', 'AB1.B6.B', 'AC1.B6.B',
    'AA1.B6.C', 'AB1.B6.C', 'AC1.B6.C',
    'AA1.B6.D', 'AB1.B6.D', 'AC1.B6.D',
    'AA2', 'AB2', 'AC2', 'AD2', 'BA2', 'BB2', 'BC2', 'BD2', 'CA2', 'CB2', 'CC2', 'CD2', 'DA2', 'DB2', 'EA2.B1', 'EB2.B1', 'EC2.B1',
    'EA2.B2', 'EB2.B2', 'EC2.B2',
    'EA2.B3', 'EB2.B3', 'EC2.B3',
    'EA2.B4', 'EB2.B4', 'EC2.B4',
    'EA2.B5', 'EB2.B5', 'EC2.B5',
    ]

for name in database:
    # -------------------------------------------------------------------------
    # Create slot for ready:
    # -------------------------------------------------------------------------
    mode = 'stock'
    slot_ids = slot_pool.search([
        ('mode', '=', mode),
        ('name', '=', name),
        ])
    if not slot_ids:
        slot_pool.create({
            'mode': mode,
            'name': name,
            })
