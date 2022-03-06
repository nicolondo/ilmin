# -*- coding: utf-8 -*-
from odoo import models, fields, api


class PosOrder(models.Model):
    _inherit = 'pos.order'

    comission_level1 = fields.Float(string='Comission l1', compute="_compute_comissions",store=True)
    comission_level2 = fields.Float(string='Comission l2', compute="_compute_comissions",store=True)
    comission_level3 = fields.Float(string='Comission l3', compute="_compute_comissions",store=True)

    @api.depends('amount_total')
    def _compute_comissions(self):
        for order in self:
            level1 = int(self.env['ir.config_parameter'].sudo().get_param('mlm_marketing.comission_level_1'))
            level2 = int(self.env['ir.config_parameter'].sudo().get_param('mlm_marketing.comission_level_2'))
            level3 = int(self.env['ir.config_parameter'].sudo().get_param('mlm_marketing.comission_level_3'))
            if level1 > 0 :
                order.comission_level1 = order.amount_total * level1 /100
            else :
                order.comission_level1 = 0
            if level2 > 0 :
                order.comission_level2 = order.amount_total * level2 /100
            else :
                order.comission_level2 = 0
            if level3 > 0 :
                order.comission_level3 = order.amount_total * level3 /100
            else :
                order.comission_level3 = 0