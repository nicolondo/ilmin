# -*- coding: utf-8 -*-
{
    'name': "mlm_marketing",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'point_of_sale', 'sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_setting.xml',
        'views/res_users_views.xml',
        'views/product.xml',
        'views/pos_order.xml',
        'views/product_product.xml',
        'views/brand.xml',
        'views/import_bom_wizard.xml',
        'views/mlm_dashboard.xml',
        'views/mlm_onboarding_panel_view.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            '/mlm_marketing/static/src/scss/dashboard.css',
            '/mlm_marketing/static/src/js/graph_widget_ept.js',
            '/mlm_marketing/static/src/js/treeMaker-master/lib/tree_maker-min.css',
            '/mlm_marketing/static/src/js/treeMaker-master/lib/tree_maker-min.js',
            '/mlm_marketing/static/src/js/tree_widget_ept.js',
            '/mlm_marketing/static/src/js/statistic_profit_widget_ept.js'

        ],
        'web.assets_qweb': [
            '/mlm_marketing/static/src/xml/dashboard_widget.xml',
        ]

    },
}
