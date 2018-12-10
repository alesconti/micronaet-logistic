import os
import sys
import openerp
import logging
import base64
from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.tools import (
    DEFAULT_SERVER_DATE_FORMAT, 
    DEFAULT_SERVER_DATETIME_FORMAT, 
    DATETIME_FORMATS_MAP, 
    float_compare,
    )


_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    ''' Template add fields
    '''
    _inherit = 'product.template'

    @api.model
    def _get_root_image_folder(self):
        ''' Default folder path
            NOTE: This function could be overrider to setup different path
        '''
        installation_root = os.path.expanduser('~/images')
        try:
            os.system('mkdir -p %s' % installation_root)
        except:
            return False
        return installation_root

    @api.multi
    def _get_folder_image_file(self):
        ''' Return image loading from file:
        '''
        folder = self._get_root_image_folder()
        for product in self:
            filename = product.mmac_url_image
            if not folder or not filename:
                product.new_image = False
                _logger.info('Missed folder of filename: %s' % product.name)
                continue
            filename = os.path.join(folder, filename)
            try:
                import pdb; pdb.set_trace()
                binary_data = open(filename, 'rb').read()
                product.new_image = base64.encodestring(binary_data)
                binary_data.close()                    
                _logger.info('Product image loaded: %s' % filename)
            except:
                product.new_image = False    
                _logger.error('Product image not found: %s' % filename)

    # -------------------------------------------------------------------------
    # Columns:
    # -------------------------------------------------------------------------
    mmac_url_image = fields.Char('Filename', size=120, 
        help='Filename of image file, path is a standard folder')
    new_image = fields.Binary(
         compute=_get_folder_image_file,
         help='Automatically sanitized HTML contents', string='Image')
