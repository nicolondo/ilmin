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

        gourper_commission_lines = {}
        for com in commissions:
            if com.state != 'new': continue
            partner_id = com.user_id.partner_id
            if partner_id in gourper_commission_lines:
                gourper_commission_lines[partner_id] += com
            else:
                gourper_commission_lines[partner_id] = com

        for record in gourper_commission_lines:
            invoice_vals = commission_obj._prepare_invoice(self.journal_id,
                                                           record.company_id.id,
                                                           record, gourper_commission_lines[record])
            new_invoice = invoice_obj.create(invoice_vals)
            new_invoice.action_post()
            for com in gourper_commission_lines[record]:
                com.move_id = new_invoice.id
                com.state = 'confirm'

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
