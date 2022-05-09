from odoo import models, fields, api


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
        ('confirm', 'Confirmed'),
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

    def _prepare_invoice(self, journal_id):
        """Prepare the dict of values to create the new invoice for a purchase order.
        """
        self.ensure_one()
        move_type = self._context.get('default_move_type', 'in_invoice')
        journal = self.env['account.move'].browse(journal_id)
        if not journal:
            raise UserError(_('Please define an accounting purchase journal for the company %s (%s).') % (
                self.company_id.name, self.company_id.id))

        partner_invoice_id = self.partner_id.address_get(['invoice'])['invoice']
        invoice_vals = {
            'ref': self.partner_ref or '',
            'move_type': move_type,
            'narration': self.notes,
            'currency_id': self.currency_id.id,
            'invoice_user_id': self.user_id and self.user_id.id or self.env.user.id,
            'partner_id': partner_invoice_id,
            'fiscal_position_id': (
                    self.fiscal_position_id or self.fiscal_position_id.get_fiscal_position(partner_invoice_id)).id,
            'payment_reference': self.partner_ref or '',
            'partner_bank_id': self.partner_id.bank_ids[:1].id,
            'invoice_origin': self.name,
            'invoice_payment_term_id': self.payment_term_id.id,
            'invoice_line_ids': [],
            'company_id': self.company_id.id,
        }
        return invoice_vals
