from odoo import models


class ThemeGoldIlmin(models.AbstractModel):
    _inherit = 'theme.utils'

    def _theme_gold_ilmin_post_copy(self, mod):
        self.disable_view('website_sale.sort')
        self.disable_view('website_sale.filter_products_price')
        self.enable_view('website_sale.products_list_view')
        self.disable_view('website_sale.add_grid_or_list_option')
        self.enable_view('portal.my_account_link')






