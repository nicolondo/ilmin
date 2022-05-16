from odoo import fields, models, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    comission_level_1 = fields.Integer('Comission level 1 %', config_parameter='mlm_marketing.comission_level_1')
    comission_level_2 = fields.Integer('Comission level 2 %', config_parameter='mlm_marketing.comission_level_2')
    comission_level_3 = fields.Integer('Comission level 3 %', config_parameter='mlm_marketing.comission_level_3')
    comission_product = fields.Many2one('product.product', String='Commission Product', config_parameter='mlm_marketing.comission_product')
