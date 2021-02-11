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
import time
import sys
from datetime import datetime

pidfile = '/tmp/auto_print_daemon.pid'
log_exec_file = './log/execution.log'


# -----------------------------------------------------------------------------
# Function:
# -----------------------------------------------------------------------------
def write_log(log_f, message, mode='info'):
    """ Log on file
    """
    log_f.write('%s - [%s] %s\n' % (
        datetime.now(),
        mode.upper(),
        message,
    ))


# -----------------------------------------------------------------------------
# Check multi execution:
# -----------------------------------------------------------------------------
log_exec_f = open(log_exec_file, 'a')

# A. Check if yet running:
pid = str(os.getpid())
if os.path.isfile(pidfile):
    message = '\n[%s] Invoice Daemon already running [%s]\n' % (pid, pidfile)
    # write_log(log_exec_f, message, 'error')
    print(message)
    sys.exit()
else:
    message = '[%s] Invoice Daemon running [%s]' % (pid, pidfile)
    write_log(log_exec_f, message)

# B. Create PID file:
pid_f = open(pidfile, 'w')
pid_f.write(pid)
pid_f.close()

# -----------------------------------------------------------------------------
# Read configuration parameter:
# -----------------------------------------------------------------------------
try:
    cfg_file = os.path.expanduser('../odoo.cfg')

    config = ConfigParser.ConfigParser()
    config.read([cfg_file])
    dbname = config.get('dbaccess', 'dbname')
    user = config.get('dbaccess', 'user')
    pwd = config.get('dbaccess', 'pwd')
    server = config.get('dbaccess', 'server')
    port = config.get('dbaccess', 'port')   # verify if it's necessary: getint

    # -------------------------------------------------------------------------
    # Connect to ODOO:
    # -------------------------------------------------------------------------
    odoo = erppeek.Client(
        'http://%s:%s' % (server, port),
        db=dbname,
        user=user,
        password=pwd,
        )
    order_pool = odoo.model('sale.order')
    company_pool = odoo.model('sale.order')

    auto_order_ids = order_pool.search([
        ('auto_print_order', '=', True)
    ])

    # If present read parameters and print:
    orders = order_pool.browse(auto_order_ids)
    company = orders[0].company_id
    block = company.auto_print
    wait = company.auto_wait

    # -------------------------------------------------------------------------
    # Print order:
    # -------------------------------------------------------------------------
    counter = 0
    for order in orders:
        counter += 1

        # Print N order and wait after print block:
        if counter > block:
            counter = 1
            time.sleep(wait)

        order.workflow_ready_to_done_current_order()
        order.write_log_chatter_message('Lancio stampa automatica ordine')
finally:
    os.unlink(pidfile)
    message = '[%s] Invoice Daemon stopped [%s]\n' % (pid, pidfile)
    write_log(log_exec_f, message)
    log_exec_f.close()
