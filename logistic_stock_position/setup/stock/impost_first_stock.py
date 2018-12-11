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
import xlrd

remove_char = ('\t', '\n')
inventory_xls = 'inventario_esportat.xlsx'

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
product_pool = odoo.model('product.template')
slot_pool = odoo.model('stock.location.slot')
quant_pool = odoo.model('stock.quant')

slot_db = {}
slot_ids = slot_pool.search([])
for slot in slot_pool.browse(slot_ids):
    slot_db[slot.name] = slot.id

# -----------------------------------------------------------------------------
# Load origin name from XLS
# -----------------------------------------------------------------------------
try:
    WB = xlrd.open_workbook(inventory_xls)
except:
    print '[ERROR] Cannot read XLS file: %s' % inventory_xls

WS = WB.sheet_by_index(0)

i = 0
import pdb; pdb.set_trace()
for row in range(row_start, WS.nrows):
    i += 1
    
    # Parameter:
    default_code = WS.cell(row, 0).value
    new_qty = WS.cell(row, 1).value
    slot = WS.cell(row, 2).value

    if not default_code or not new_qty or not slot:
        print('{}. Dati mancanti riga {}'.format(i, row))
        continue

    if '#' in default_code:
        print('{}. Prodotto kit (non importato): {}'.format(i, default_code))
        continue
        
    # -------------------------------------------------------------------------    
    # Slot check:
    # -------------------------------------------------------------------------    
    if slot not in slot_db:
        print('{}. Slot non trovato: {}'.format(i, slot))
        continue

    # TODO Create slot:
    #    partner_id = partner_pool.create({
    #        'name': supplier,
    #        'supplier': True,
    #        'is_company': True,
    #        #'product_suffix': prefix.strip('-'),
    #        }).id
    # TODO update product position
        
    # -------------------------------------------------------------------------    
    # Product check:    
    # -------------------------------------------------------------------------    
    product_ids = product_pool.search([('default_code', '=', default_code)])
    if not product_ids:
        print('{}. Prodotto non trovato: {}'.format(i, default_code))
        continue
        
    if len(product_ids) > 1:
        print('{}. Prodotto doppio (preso primo): {}'.format(i, default_code))
        
    product_proxy = product_pool.browse(product_id)[0]
    qty_available = product_proxy.qty_available
    if qty_available == new_qty:
        print('{}. Q. corretta [Old: {}] [New: {}]'.format(
            i, qty_available, new_qty))
        continue

    # -------------------------------------------------------------------------    
    # -------------------------------------------------------------------------    
    gap_qty = new_qty - qty_available
    print('{}. [{}] Da creare quant: {}'.format(i, default_code, gap_qty))
    
    # Create quant for gap:
    # TODO
    

