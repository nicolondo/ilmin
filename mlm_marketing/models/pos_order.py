# -*- coding: utf-8 -*-
from odoo import models, fields, api


class PosOrder(models.Model):
    _inherit = 'pos.order'

    comission_level1 = fields.Float(string='Comission l1', compute="_compute_comissions", store=True)
    comission_level2 = fields.Float(string='Comission l2', compute="_compute_comissions", store=True)
    comission_level3 = fields.Float(string='Comission l3', compute="_compute_comissions", store=True)

    @api.depends('amount_total')
    def _compute_comissions(self):
        for order in self:
            level1 = int(self.env['ir.config_parameter'].sudo().get_param('mlm_marketing.comission_level_1'))
            level2 = int(self.env['ir.config_parameter'].sudo().get_param('mlm_marketing.comission_level_2'))
            level3 = int(self.env['ir.config_parameter'].sudo().get_param('mlm_marketing.comission_level_3'))
            if level1 > 0:
                order.comission_level1 = order.amount_total * level1 / 100
            else:
                order.comission_level1 = 0
            if level2 > 0:
                order.comission_level2 = order.amount_total * level2 / 100
            else:
                order.comission_level2 = 0
            if level3 > 0:
                order.comission_level3 = order.amount_total * level3 / 100
            else:
                order.comission_level3 = 0

    @api.model
    def _process_order(self, order, draft, existing_order):
        pos_order_id = super(PosOrder, self)._process_order(order, draft, existing_order)
        pos_order = self.browse(pos_order_id)
        if pos_order.state == 'paid':
            pos_order._generate_pos_order_commissions()

    def _generate_pos_order_commissions(self):
        self.ensure_one()

        commission_obj = self.env['pos.commission']

        # Force company for all SUPERUSER_ID action
        if self.comission_level1 > 0 and self.user_id:
            commission_obj.create({
                'pos_order': self.id,
                'user_id': self.user_id.id,
                'commission_type': "l1",
            })
        if self.comission_level2 > 0 and self.user_id.sponsor:
            commission_obj.create({
                'pos_order': self.id,
                'user_id': self.user_id.id,
                'commission_type': "l2",
            })

        if self.comission_level3 > 0 and self.user_id.sponsor.sponsor:
            commission_obj.create({
                'pos_order': self.id,
                'user_id': self.user_id.id,
                'commission_type': "l3",
            })

        return self.id
