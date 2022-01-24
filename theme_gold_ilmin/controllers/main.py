from odoo import http, fields, tools, api, _
from odoo.http import request
import json
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.website_sale.controllers.main import TableCompute
from odoo.addons.web.controllers import main


class Home(main.Home):

    def _login_redirect(self, uid, redirect=None):
        if not redirect and not request.env['res.users'].sudo().browse(uid).has_group('base.group_user'):
            redirect = '/shop'
        return super(Home, self)._login_redirect(uid, redirect=redirect)


class WebsiteSale(WebsiteSale):

    def sitemap_shop(env, rule, qs):
        if not qs or qs.lower() in '/shop':
            yield {'loc': '/shop'}

        Category = env['product.public.category']
        dom = sitemap_qs2dom(qs, '/shop/category', Category._rec_name)
        dom += env['website'].get_current_website().website_domain()
        for cat in Category.search(dom):
            loc = '/shop/category/%s' % slug(cat)
            if not qs or qs.lower() in loc:
                yield {'loc': loc}

    @http.route([
        '''/shop''',
        '''/shop/page/<int:page>''',
        '''/shop/category/<model("product.public.category"):category>''',
        '''/shop/category/<model("product.public.category"):category>/page/<int:page>'''
    ], type='http', auth="user", website=True, sitemap=sitemap_shop)
    def shop(self, page=0, category=None, search='', min_price=0.0, max_price=0.0, ppg=False, **post):
        post['order'] = "name asc"
        order = request.website.sale_get_order()
        if order and order.state != 'draft':
            request.session['sale_order_id'] = None
            order = request.website.sale_get_order()

        add_qty = int(post.get('add_qty', 1))
        try:
            min_price = float(min_price)
        except ValueError:
            min_price = 0
        try:
            max_price = float(max_price)
        except ValueError:
            max_price = 0

        Category = request.env['product.public.category']
        if category:
            category = Category.search([('id', '=', int(category))], limit=1)
            if not category or not category.can_access_from_current_website():
                raise NotFound()
        else:
            category = Category

        if ppg:
            try:
                ppg = int(ppg)
                post['ppg'] = ppg
            except ValueError:
                ppg = False
        if not ppg:
            ppg = request.env['website'].get_current_website().shop_ppg or 20

        ppr = request.env['website'].get_current_website().shop_ppr or 4

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
        attributes_ids = {v[0] for v in attrib_values}
        attrib_set = {v[1] for v in attrib_values}

        keep = QueryURL('/shop', category=category and int(category), search=search, attrib=attrib_list,
                        min_price=min_price, max_price=max_price, order=post.get('order'))

        pricelist_context, pricelist = self._get_pricelist_context()

        request.context = dict(request.context, pricelist=pricelist.id, partner=request.env.user.partner_id)

        filter_by_price_enabled = request.website.is_view_active('website_sale.filter_products_price')
        if filter_by_price_enabled:
            company_currency = request.website.company_id.currency_id
            conversion_rate = request.env['res.currency']._get_conversion_rate(company_currency, pricelist.currency_id,
                                                                               request.website.company_id,
                                                                               fields.Date.today())
        else:
            conversion_rate = 1

        url = "/shop"
        if search:
            post["search"] = search
        if attrib_list:
            post['attrib'] = attrib_list

        options = {
            'displayDescription': True,
            'displayDetail': True,
            'displayExtraDetail': True,
            'displayExtraLink': True,
            'displayImage': True,
            'allowFuzzy': not post.get('noFuzzy'),
            'category': str(category.id) if category else None,
            'min_price': min_price / conversion_rate,
            'max_price': max_price / conversion_rate,
            'attrib_values': attrib_values,
            'display_currency': pricelist.currency_id,
        }
        # No limit because attributes are obtained from complete product list
        product_count, details, fuzzy_search_term = request.website._search_with_fuzzy("products_only", search,
                                                                                       limit=None,
                                                                                       order=self._get_search_order(
                                                                                           post), options=options)
        search_product = details[0].get('results', request.env['product.template']).with_context(bin_size=True)

        filter_by_price_enabled = request.website.is_view_active('website_sale.filter_products_price')
        if filter_by_price_enabled:
            # TODO Find an alternative way to obtain the domain through the search metadata.
            Product = request.env['product.template'].with_context(bin_size=True)
            domain = self._get_search_domain(search, category, attrib_values)

            # This is ~4 times more efficient than a search for the cheapest and most expensive products
            from_clause, where_clause, where_params = Product._where_calc(domain).get_sql()
            query = f"""
                SELECT COALESCE(MIN(list_price), 0) * {conversion_rate}, COALESCE(MAX(list_price), 0) * {conversion_rate}
                  FROM {from_clause}
                 WHERE {where_clause}
            """
            request.env.cr.execute(query, where_params)
            available_min_price, available_max_price = request.env.cr.fetchone()

            if min_price or max_price:
                # The if/else condition in the min_price / max_price value assignment
                # tackles the case where we switch to a list of products with different
                # available min / max prices than the ones set in the previous page.
                # In order to have logical results and not yield empty product lists, the
                # price filter is set to their respective available prices when the specified
                # min exceeds the max, and / or the specified max is lower than the available min.
                if min_price:
                    min_price = min_price if min_price <= available_max_price else available_min_price
                    post['min_price'] = min_price
                if max_price:
                    max_price = max_price if max_price >= available_min_price else available_max_price
                    post['max_price'] = max_price

        website_domain = request.website.website_domain()
        categs_domain = [('parent_id', '=', False)] + website_domain
        if search:
            search_categories = Category.search(
                [('product_tmpl_ids', 'in', search_product.ids)] + website_domain).parents_and_self
            categs_domain.append(('id', 'in', search_categories.ids))
        else:
            search_categories = Category
        categs = Category.search(categs_domain)

        if category:
            url = "/shop/category/%s" % slug(category)

        pager = request.website.pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
        offset = pager['offset']
        products = search_product[offset:offset + ppg]

        ProductAttribute = request.env['product.attribute']
        if products:
            # get all products without limit
            attributes = ProductAttribute.search([
                ('product_tmpl_ids', 'in', search_product.ids),
                ('visibility', '=', 'visible'),
            ])
        else:
            attributes = ProductAttribute.browse(attributes_ids)

        layout_mode = request.session.get('website_sale_shop_layout_mode')
        if not layout_mode:
            if request.website.viewref('website_sale.products_list_view').active:
                layout_mode = 'list'
            else:
                layout_mode = 'grid'

        Country = request.env['res.country']

        values = {
            'search': fuzzy_search_term or search,
            'original_search': fuzzy_search_term and search,
            'category': category,
            'attrib_values': attrib_values,
            'attrib_set': attrib_set,
            'pager': pager,
            'pricelist': pricelist,
            'add_qty': add_qty,
            'products': products,
            'search_count': product_count,  # common for all searchbox
            'bins': TableCompute().process(products, ppg, ppr),
            'ppg': ppg,
            'ppr': ppr,
            'categories': categs,
            'attributes': attributes,
            'keep': keep,
            'search_categories_ids': search_categories.ids,
            'layout_mode': layout_mode,
            'country_states': Country.get_website_sale_states(mode="shipping"),
            'countries': Country.get_website_sale_countries(mode="shipping"),
        }
        if filter_by_price_enabled:
            values['min_price'] = min_price or available_min_price
            values['max_price'] = max_price or available_max_price
            values['available_min_price'] = tools.float_round(available_min_price, 2)
            values['available_max_price'] = tools.float_round(available_max_price, 2)
        if category:
            values['main_object'] = category
        return request.render("website_sale.products", values)

    @http.route(['/shop/cart/update_custom'], type='json', auth="public", methods=['GET', 'POST'], website=True,
                csrf=False)
    def cart_update_custom(self, product_id, line_id=None, set_qty=0,
                           **kw):
        """This route is called when adding a product to cart (no options)."""
        """This route is called when adding a product to cart (no options)."""
        sale_order = request.website.sale_get_order(force_create=True)
        if sale_order.state != 'draft':
            request.session['sale_order_id'] = None
            sale_order = request.website.sale_get_order(force_create=True)

        if sale_order:
            values = {
                "website_sale_order": sale_order,
            }

            result = sale_order._cart_update_custom(
                order_id=sale_order.id,
                line_id=int(line_id) if line_id else False,
                product_id=int(product_id),
                set_qty=set_qty,

            )
            cart_lines_ilmin = request.env['ir.ui.view']._render_template('theme_gold_ilmin.cart_lines_ilmin', values)

            result["cart_lines_ilmin"] = cart_lines_ilmin
            return result

        else:
            return False

    @http.route(['/shop/cart/getcontact_info'], type='json', auth="public", methods=['GET', 'POST'], website=True,
                csrf=False)
    def getcontact_info(self, contact_id,
                        **kw):
        """This route is called when adding a product to cart (no options)."""
        """This route is called when adding a product to cart (no options)."""

        contact = request.env['res.partner'].browse(int(contact_id))
        if contact:
            data = {
                'contact_id': contact.id,
                'name': contact.name,
                'email': contact.email,
                'phone': contact.phone,
                'street': contact.street,
                'street2': contact.street2,
                'zip': contact.zip,
                'country_id': contact.country_id,
                'city': contact.city,
            }
            return data
        else:
            return False

    @http.route(['/shop/cart/create_contacts'], type='json', auth="public", methods=['POST'], website=True,
                csrf=False)
    def create_contacts(self, data, **kw):
        """This route is called when adding a product to cart (no options)."""
        """This route is called when adding a product to cart (no options)."""
        Contact = request.env['res.partner']
        if (data['contact_id']):
            contact = Contact.browse(int(data['contact_id']))
            data = {
                'name': data['name'],
                'email': data['email'],
                'phone': data['phone'],
                'street': data['street'],
                'street2': data['street2'],
                'zip': data['zip'],
                'country_id': int(data['country_id']),
                'city': data['city'],
            }

            contact.sudo().write(data)

        else:

            data = {
                'type': 'delivery',
                'parent_id': int(data['partner_id']),
                'name': data['name'],
                'email': data['email'],
                'phone': data['phone'],
                'street': data['street'],
                'street2': data['street2'],
                'zip': data['zip'],
                'country_id': int(data['country_id']),
                'city': data['city'],
            }

            contact = Contact.sudo().create(data)

        if contact:
            result = {}
            order = request.website.sale_get_order()
            values = {
                "website_sale_order": order,
            }
            all_adress_shipping = request.env['ir.ui.view']._render_template(
                'theme_gold_ilmin.address_on_payment_ilmin', values)
            result["all_adress_shipping"] = all_adress_shipping

            return result
        else:
            return False

    @http.route(['/shop/cart/shop_confirm_order'], type='json', auth="public", website=True, sitemap=False)
    def shop_confirm_order(self, contact_id, **post):
        order = request.website.sale_get_order()
        data = {'success': False}
        if (contact_id):
            order.partner_shipping_id = int(contact_id)
        order.onchange_partner_shipping_id()
        order.order_line._compute_tax_id()
        order.action_confirm()
        if order and order.state != 'draft':
            data['url'] = request.httprequest.host_url + "shop"
            data['success'] = True
            data['order_name'] = order.name

        return data
