# -*- coding: utf-8 -*-
from odoo import models, fields, api


class Product(models.Model):
    _inherit = 'product.template'

    brand_id = fields.Many2one('mlm_marketing.brand', string='Brand')


