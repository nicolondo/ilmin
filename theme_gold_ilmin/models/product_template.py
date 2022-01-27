from odoo import api,fields, models, _


class ProductTmpl(models.Model):
    _inherit = "product.template"

    only_user = fields.Many2one('res.users', string='Only for this user')

    @api.model
    def _search_get_detail(self, website, order, options):
        result  = super(ProductTmpl, self)._search_get_detail(website, order, options)
        result['base_domain'].append(['|',('only_user', '=', False),('only_user', '=', self.env.uid)])
        return result
