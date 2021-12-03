# -*- coding: utf-8 -*-
# from odoo import http


# class MlmMarketing(http.Controller):
#     @http.route('/mlm_marketing/mlm_marketing/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mlm_marketing/mlm_marketing/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mlm_marketing.listing', {
#             'root': '/mlm_marketing/mlm_marketing',
#             'objects': http.request.env['mlm_marketing.mlm_marketing'].search([]),
#         })

#     @http.route('/mlm_marketing/mlm_marketing/objects/<model("mlm_marketing.mlm_marketing"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mlm_marketing.object', {
#             'object': obj
#         })
