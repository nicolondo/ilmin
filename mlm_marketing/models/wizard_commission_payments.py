from odoo import models, fields, api, _
from odoo.exceptions import UserError


class WizardBom(models.TransientModel):
    _name = "pos.wizardgpayment"
    _description = "pos.wizardgpayment"

    journal_id = fields.Many2one('account.journal', string='Journal')

    def confirm(self):
        commissions = self.env['pos.commission'].browse(self._context.get('active_ids', []))
        for com in commissions:
            com.state = 'confirm'

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def generate_payments(self):
        if not self.journal_id:
            raise UserError(_("Please select an account journal"))

        invoice_obj = self.env['account.move']
        commission_obj = self.env['pos.commission']

        commissions = commission_obj.browse(self._context.get('active_ids', []))
        current_date = datetime.date.today()

        for com in commissions:
            com.state = 'paid'
            invoice_vals = commission_obj.with_company(self.purchase_id.company_id)._prepare_invoice()
            new_invoice = invoice_obj.create(invoice_vals)

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
