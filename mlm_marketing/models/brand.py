# -*- coding: utf-8 -*-

from odoo import fields, models


class Brand(models.Model):
    _name = 'mlm_marketing.brand'

    name =fields.Char('Name')

    description =fields.Char('Description')
