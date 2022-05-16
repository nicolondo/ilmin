from odoo import models, fields, api
from datetime import datetime, timedelta


class Mlm(models.Model):
    _name = 'pos.commission'
    _description = 'pos commission'

    pos_order = fields.Many2one("pos.order", string='Order', required=True)
    user_id = fields.Many2one('res.users', string='Sales person', required=True)
    total = fields.Float(related='pos_order.amount_total')
    commission_l1 = fields.Float(related="pos_order.comission_level1", string='Comission')
    commission_l2 = fields.Float(related="pos_order.comission_level2", string='Comission')
    commission_l3 = fields.Float(related="pos_order.comission_level3", string='Comission')
    currency_id = fields.Many2one(string="Currency", related='pos_order.company_id.currency_id', readonly=True)
    move_id = fields.Many2one('account.move', string='Invoice', readonly=True)

    commission_type = fields.Selection([
        ('l1', 'Level 1'),
        ('l2', 'Level 2'),
        ('l3', 'Level 3')
    ], string='Type', readonly=True, required=True, tracking=True, copy=False)
    state = fields.Selection([
        ('new', 'New'),
        ('confirm', 'Invoiced'),
        ('paid', 'Paid')
    ], string='Status', readonly=True, required=True, tracking=True, copy=False, default='new')

    def action_confirm(self):
        for com in self:
            com.state = 'confirm'

    def action_cancel(self):
        for com in self:
            com.state = 'new'

    def action_create_payment(self):
        for com in self:
            com.state = 'paid'

    def _prepare_invoice(self, journal_id, company_id, partner_id, commissions):
        """Prepare the dict of values to create the new invoice for a purchase order.
        """
        move_type = self._context.get('default_move_type', 'out_invoice')
        journal = self.env['account.move'].browse(journal_id)
        company = self.env['res.company'].browse(company_id)

        if not journal:
            raise UserError(_('Please define an accounting  journal'))
        product_id = int(self.env['ir.config_parameter'].sudo().get_param('mlm_marketing.comission_product'))
        if not product_id:
            raise UserError(_("Please select an cimission product"))

        partner_invoice_id = partner_id.address_get(['invoice'])['invoice']

        inv_lines = []
        for com in commissions:
            price = 0
            if com.commission_type == 'l1':
                price = com.commission_l1
            elif com.commission_type == 'l2':
                price = com.commission_l2
            elif com.commission_type == 'l3':
                price = com.commission_l3

            inv_lines += [(0, 0, {
                'product_id': product_id,
                'price_unit': price,
            })]

        invoice_vals = {
            'invoice_date': datetime.today(),
            'move_type': move_type,
            'currency_id': company.currency_id.id,
            'partner_id': partner_invoice_id,
            'invoice_line_ids': inv_lines,
            'company_id': company_id,
        }
        return invoice_vals
