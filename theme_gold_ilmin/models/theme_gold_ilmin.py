from odoo import models


class ThemeGoldIlmin(models.AbstractModel):
    _inherit = 'theme.utils'

    def _theme_gold_ilmin_post_copy(self, mod):
        self.enable_view('website_sale.header_cart_link')


