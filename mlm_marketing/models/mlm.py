# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, timedelta
import json
from odoo.exceptions import UserError


class Mlm(models.Model):
    _name = 'mlm_marketing.mlm'

    user_id = fields.Many2one('res.users', string='Sales person', required=True)
    level1_profit_today = fields.Float('Profit today', compute="_compute_profit")
    level1_profit_week = fields.Float('Profit last 7 days', compute="_compute_profit")
    level1_profit_month = fields.Float('Profit last month', compute="_compute_profit")

    level2_profit_today = fields.Float('Profit level 2 today', compute="_compute_profit")
    level2_profit_week = fields.Float('Profit level 2 last 7 days', compute="_compute_profit")
    level2_profit_month = fields.Float('Profit level 2 last month', compute="_compute_profit")

    level3_profit_today = fields.Float('Profit level 3 today', compute="_compute_profit")
    level3_profit_week = fields.Float('Profit level 3 last 7 days', compute="_compute_profit")
    level3_profit_month = fields.Float('Profit level 3 last month', compute="_compute_profit")

    level1_nbr_customer = fields.Integer('New Client today', compute="_compute_nbr_customer")
    level2_nbr_customer = fields.Integer('New Client level 2 today', compute="_compute_nbr_customer")
    level3_nbr_customer = fields.Integer('New Client level 3 today', compute="_compute_nbr_customer")

    graph_order_data = fields.Text(compute="_compute_graph_order_data")
    tree_data = fields.Text(compute="_compute_tree_data")
    statistic_profit_data = fields.Text(compute="_compute_profit")

    def _compute_profit(self):
        if not self._context.get('sort_profit'):
            context = dict(self.env.context)
            context.update({'sort_profit': 'week'})
            self.env.context = context
        for record in self:
            order_obj = self.env['pos.order']

            today = datetime.combine(fields.Date.today(), datetime.min.time())
            last_week = today - timedelta(days=7)
            last_month = today - timedelta(days=30)

            level1_profit_today = sum(order_obj.search(
                [('user_id', '=', self.env.uid), ('date_order', '>=', today),
                 ('date_order', '<', today + timedelta(days=1))]).mapped('comission_level1'))
            record.level1_profit_today = level1_profit_today

            level1_profit_week = sum(
                order_obj.search([('user_id', '=', self.env.uid), ('date_order', '>', last_week)]).mapped(
                    'comission_level1'))
            record.level1_profit_week = level1_profit_week

            level1_profit_month = sum(
                order_obj.search([('user_id', '=', self.env.uid), ('date_order', '>', last_month)]).mapped(
                    'comission_level1'))
            record.level1_profit_month = level1_profit_month

            level2_profit_today = sum(order_obj.search(
                [('user_id.sponsor.id', '=', self.env.uid), ('date_order', '>=', today),
                 ('date_order', '<', today + timedelta(days=1))]).mapped(
                'comission_level2'))
            record.level2_profit_today = level2_profit_today

            level2_profit_week = sum(order_obj.search(
                [('user_id.sponsor.id', '=', self.env.uid), ('date_order', '>', last_week)]).mapped(
                'comission_level2'))
            record.level2_profit_week = level2_profit_week

            level2_profit_month = sum(order_obj.search(
                [('user_id.sponsor.id', '=', self.env.uid), ('date_order', '>', last_month)]).mapped(
                'comission_level2'))
            record.level2_profit_month = level2_profit_month

            level3_profit_today = sum(order_obj.search([('user_id.sponsor.sponsor.id', '=', self.env.uid)
                                                           , ('date_order', '>=', today),
                                                        ('date_order', '<', today + timedelta(days=1))]).mapped(
                'comission_level3'))
            record.level3_profit_today = level3_profit_today

            level3_profit_week = sum(order_obj.search(
                [('user_id.sponsor.sponsor.id', '=', self.env.uid), ('date_order', '>', last_week)]).mapped(
                'comission_level3'))
            record.level3_profit_week = level3_profit_week

            level3_profit_month = sum(order_obj.search(
                [('user_id.sponsor.sponsor.id', '=', self.env.uid), ('date_order', '>', last_month)]).mapped(
                'comission_level3'))
            record.level3_profit_month = level3_profit_month

            Monetary = self.env['ir.qweb.field.monetary']
            currency = self.env.company.currency_id
            if self._context.get('sort_profit') == 'day':
                record.statistic_profit_data = json.dumps({
                    "level1_profit": Monetary.value_to_html(level1_profit_today, {'display_currency': currency}),
                    "level2_profit": Monetary.value_to_html(level2_profit_today, {'display_currency': currency}),
                    "level3_profit": Monetary.value_to_html(level3_profit_today, {'display_currency': currency}),
                    "sort_on": self._context.get('sort_profit'),

                })
            elif self._context.get('sort_profit') == "week":
                record.statistic_profit_data = json.dumps({
                    "level1_profit": Monetary.value_to_html(level1_profit_week, {'display_currency': currency}),
                    "level2_profit": Monetary.value_to_html(level2_profit_week, {'display_currency': currency}),
                    "level3_profit": Monetary.value_to_html(level3_profit_week, {'display_currency': currency}),
                    "sort_on": self._context.get('sort_profit'),

                })
            elif self._context.get('sort_profit') == "month":
                record.statistic_profit_data = json.dumps({
                    "level1_profit": Monetary.value_to_html(level1_profit_month, {'display_currency': currency}),
                    "level2_profit": Monetary.value_to_html(level2_profit_month, {'display_currency': currency}),
                    "level3_profit": Monetary.value_to_html(level3_profit_month, {'display_currency': currency}),
                    "sort_on": self._context.get('sort_profit'),

                })

    def _compute_nbr_customer(self):
        for record in self:
            partner_obj = self.env['res.partner']

            record.level1_nbr_customer = partner_obj.search_count([('user_id', '=', self.env.uid)])
            record.level2_nbr_customer = partner_obj.search_count([('user_id.sponsor.id', '=', self.env.uid)])
            record.level3_nbr_customer = partner_obj.search_count([('user_id.sponsor.sponsor.id', '=', self.env.uid)])

    def _compute_graph_order_data(self):
        if not self._context.get('sort'):
            context = dict(self.env.context)
            context.update({'sort': 'month'})
            self.env.context = context
        for record in self:
            values = record.get_graph_data(record.user_id.id)

            record.graph_order_data = json.dumps({
                "values": values,
                "title": "",
                "key": "Order: Untaxed amount",
                "area": True,
                "color": "#875A7B",
                "is_sample_data": False,
                "total_sales": "dsds",
                "order_data": "dsds",
                "product_date": "dsds",
                "customer_data": "dsds",
                "order_shipped": "dsds",
                "refund_data": "dsds",
                "refund_count": "dsds",
                "sort_on": self._context.get('sort'),
                "currency_symbol": "dsds",
                "graph_sale_percentage": {'type': "dsds", 'value': "dsds", }
            })

    def get_graph_data(self, user_id):
        def graph_of_current_year(user_id):
            self._cr.execute("""select TRIM(TO_CHAR(DATE_TRUNC('month',month),'MONTH')),sum(amount_total) from
                                            (SELECT DATE_TRUNC('month',date(day)) as month,
                                              0 as amount_total
                                            FROM generate_series(date(date_trunc('year', (current_date - interval '1 YEAR - 1 day')))
                                            , date(date_trunc('year', (current_date)) )
                                            , interval  '1 MONTH') day
                                            union all
                                            SELECT DATE_TRUNC('month',date(date_order)) as month,
                                            sum(amount_total) as amount_total
                                              FROM   pos_order
                                            WHERE  date(date_order) >= (select date_trunc('year', date(current_date))) AND 
                                            date(date_order)::date <= (select date_trunc('year', date(current_date)) 
                                            + '1 YEAR - 1 day')
                                            and user_id = %s
                                            group by DATE_TRUNC('month',date(date_order))
                                            order by month
                                            )foo 
                                            GROUP  BY foo.month
                                            order by foo.month""" % user_id)
            return self._cr.dictfetchall()

        def graph_of_current_week(user_id):
            self._cr.execute("""SELECT to_char(date(d.day),'DAY'), t.amount_total as sum
                                            FROM  (
                                                SELECT day
                                               FROM generate_series(date(date_trunc('day', (current_date - interval '6 days')) )
                                                , date(date_trunc('day', (current_date)) )
                                                , interval  '1 day') day
                                               ) d
                                            LEFT   JOIN 
                                            (SELECT date(date_order)::date AS day, sum(amount_total) as amount_total
                                               FROM   pos_order
                                               WHERE  date(date_order) >= (select date_trunc('day', date(current_date - interval '6 days')))
                                               AND    date(date_order) <= (select date_trunc('day', date(current_date)) )
            								 	AND user_id =%s
                                               GROUP  BY 1
                                               ) t USING (day)
                                            ORDER  BY day
            								""" % user_id)
            return self._cr.dictfetchall()

        def graph_of_current_month(user_id):
            self._cr.execute("""select EXTRACT(DAY from date(date_day)) :: integer,sum(amount_total) from (
                                    SELECT 
                                      day::date as date_day,
                                      0 as amount_total
                                    FROM generate_series(date(date_trunc('day', (current_date - interval '27 day')))
                                        , date(date_trunc('day', (current_date)))
                                        , interval  '1 day') day
                                    union all
                                    SELECT date(date_order)::date AS date_day,
                                    sum(amount_total) as amount_total
                                      FROM   pos_order
                                    WHERE  date(date_order) >= (select date_trunc('day', date(current_date - interval '30 day')))
                                    AND date(date_order)::date <= (select date_trunc('day', date(current_date)))
            	                    and user_id = %s
                                    group by 1
                                    )foo 
                                    GROUP  BY date_day
                                    ORDER  BY date_day
            								""" % user_id)
            return self._cr.dictfetchall()

        # Prepare values for Graph
        if self._context.get('sort') == 'week':
            result = graph_of_current_week(user_id)
        elif self._context.get('sort') == "month":
            result = graph_of_current_month(user_id)
        elif self._context.get('sort') == "year":
            result = graph_of_current_year(user_id)

        values = [{"x": ("{}".format(data.get(list(data.keys())[0]))), "y": data.get('sum') or 0.0} for data in result]
        return values

    def _compute_tree_data(self):
        for record in self:
            if record.user_id:
                tree = {1: ''}
                treeParams = {1: record.user_id}
                sec_level_users = self.env['res.users'].search([('sponsor.id', '=', record.user_id.id)])
                if sec_level_users:
                    index = 2
                    node_level2 = {}
                    for user in sec_level_users:
                        node_level2[index] = ''
                        treeParams[index] = user
                        index += 1

                    tree[1] = node_level2

                    for user_l2 in sec_level_users:
                        node_level3 = {}
                        third_level_users = self.env['res.users'].search([('sponsor.id', '=', user_l2.id)])
                        for user_l3 in third_level_users:
                            node_level3[index] = ''
                            treeParams[index] = user_l3
                            index += 1

                        found_key = [key for key, value in treeParams.items() if value == user_l2][0]
                        tree[1][found_key] = node_level3

                for key, value in treeParams.items():
                    treeParams[key] = {'trad': value.name}

                record.tree_data = json.dumps({
                    "tree": tree,
                    "tree_params": treeParams,
                })
