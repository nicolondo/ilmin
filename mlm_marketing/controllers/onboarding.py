# -*- coding: utf-8 -*-
"""
Onboarding Controller.
"""
from odoo import http
from odoo.http import request


class MLMOnboarding(http.Controller):
    """
        Controller for Onboarding (Banner).
        @author: Dipak Gogiya on Date 26-Sep-2020.
    """

    @http.route('/mlm/mlm_onboarding_panel', auth='user', type='json')
    def mlm_onboarding_panel(self):
        """ Returns the `banner` for the shopify onboarding panel.
            It can be empty if the user has closed it or if he doesn't have
            the permission to see it. """

        current_user_id = request.env.user
        mlm_dashbord = request.env['mlm_marketing.mlm'].search([('user_id', '=', current_user_id.id)], limit=1)
        if not mlm_dashbord:
            mlm_dashbord = request.env['mlm_marketing.mlm'].create({'user_id': current_user_id.id})
        return {
            'html': request.env.ref('mlm_marketing.mlm_onboarding_panel')._render()
        }
