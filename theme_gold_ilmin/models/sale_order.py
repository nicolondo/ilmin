
from odoo import api, models, _

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _cart_update_custom(self,order_id=None, product_id=None, line_id=None, add_qty=0, set_qty=0, **kwargs):

        OrderLine = self.env['sale.order.line']
        order =  self.env['sale.order'].browse(order_id)
        product =  self.env['product.product'].browse(product_id)
        Monetary = self.env['ir.qweb.field.monetary']
        currency = order.currency_id

        set_qty = float(set_qty)


        if line_id:
            line = OrderLine.browse(line_id)
            old_qty = int(line.product_uom_qty)

        else:
            line = order.order_line.filtered(
                lambda l: l.product_id.id == product_id)
            if line:
                old_qty = int(line.product_uom_qty)
            else:
                line = OrderLine.create({'order_id': order_id, 'product_id': product_id})
                old_qty = 0

        new_qty = set_qty or 0

        if new_qty > 0:
            line.update({'product_uom_qty':new_qty})
        else :
            line.unlink()
            line=False

        product_tmpl_order_lines = order.order_line.filtered(
            lambda l: l.product_id.product_tmpl_id.id == product.product_tmpl_id.id)
        product_tmlp_total = sum(li.price_subtotal for li in product_tmpl_order_lines)
        return {'success': True, 'line_id': line.id if line else False,
                'line_total': Monetary.value_to_html(line.price_subtotal if line else 0, {'display_currency': currency}),
                'product_tmlp_total': 'TOTAL : '+Monetary.value_to_html(product_tmlp_total, {'display_currency': currency}),
                'cart_amount_total':  Monetary.value_to_html(order.amount_untaxed, {'display_currency': currency}),
                'cart_qty': order.cart_quantity,
                }

    def _get_line_info(self,order_id=None,product_id=None):
        order =  self.env['sale.order'].browse(order_id)
        product =  self.env['product.product'].browse(product_id)

        order_lines_product_total = order.order_line.filtered(
            lambda l: l.product_id.id == product_id)
        order_line_product_total =sum(li.price_reduce_taxexcl for li in order_lines_product_total)
        order_line_product_qty =sum(li.product_uom_qty for li in order_lines_product_total)

        product_tmpl_order_lines = order.order_line.filtered(
            lambda l: l.product_id.product_tmpl_id.id == product.product_tmpl_id.id)
        order_line_product_tmlp_total = sum(li.price_subtotal for li in product_tmpl_order_lines)

        return {
            'line_id': False,
            'order_line_product_total': order_line_product_total,
            'order_line_product_qty': int(order_line_product_qty),
            'order_line_product_tmlp_total': order_line_product_tmlp_total,
        }

    def _get_order_product_tpml(self,order_id=None):
        order =  self.env['sale.order'].browse(order_id)
        product_tmpl_order_lines = order.order_line.product_template_id
        return product_tmpl_order_lines


    def _get_order_line_by_tpml(self,order_id=None,product_templ_id=None):
        order =  self.env['sale.order'].browse(order_id)
        product_tmpl_order_lines = order.order_line.filtered(
            lambda l: l.product_id.product_tmpl_id.id == product_templ_id)

        return product_tmpl_order_lines


    def _get_product_tmlp_info(self,order_id=None,product_templ_id=None):
        order =  self.env['sale.order'].browse(order_id)
        product =  self.env['product.template'].browse(product_templ_id)



        product_tmpl_order_lines = order.order_line.filtered(
            lambda l: l.product_id.product_tmpl_id.id == product_templ_id)
        order_line_product_tmlp_total = sum(li.price_subtotal for li in product_tmpl_order_lines)

        return {
            'order_line_product_tmlp_total': order_line_product_tmlp_total,
        }


    def _get_shippings(self,partner_id=None):
        partner = self.env['res.partner'].browse(partner_id)

        shippings = []
        if partner_id :
            Partner = partner.with_context(show_address=1).sudo()
            shippings = Partner.search([
                ("id", "child_of",partner.commercial_partner_id.ids),
                '|', ("type", "in", ["delivery", "other"]), ("id", "=", partner.commercial_partner_id.id)
            ], order='id desc')


        return shippings

