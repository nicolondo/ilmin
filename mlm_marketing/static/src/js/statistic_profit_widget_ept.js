odoo.define('statistic_profit_dashboard_ept.graph', function (require) {
    "use strict";

    var fieldRegistry = require('web.field_registry');
    var AbstractField = require('web.AbstractField');
    var core = require('web.core');
    var QWeb = core.qweb;
    var EmiproDashboarStatisticProfit = AbstractField.extend({
        events: {
            'click .day-filter': '_sortOrders',
        },

        init: function () {
            this._super.apply(this, arguments);
            // this.data = JSON.parse(this.value);
            this.data = this.recordData
            this.match_key = _.find(_.keys(this.data), function(key){ return key.includes('statistic_profit_data') })
            this.graph_data = this.match_key.length ? JSON.parse(this.data[this.match_key]) : {}
            this.context = this.record.context
        },
        /**
         * The widget view uses the ChartJS lib to render the graph. This lib
         * requires that the rendering is done directly into the DOM (so that it can
         * correctly compute positions). However, the views are always rendered in
         * fragments, and appended to the DOM once ready (to prevent them from
         * flickering). We here use the on_attach_callback hook, called when the
         * widget is attached to the DOM, to perform the rendering. This ensures
         * that the rendering is always done in the DOM.
         */
        on_attach_callback: function () {
            this._isInDOM = true;
            this._renderInDOM();
        },
        /**
         * Called when the field is detached from the DOM.
         */
        on_detach_callback: function () {
            this._isInDOM = false;
        },

        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------

        /**
         * Render the widget only when it is in the DOM.
         *
         * @override
         * @private
         */
        _render: function () {
            if (this._isInDOM) {
                return this._renderInDOM();
            }
            return Promise.resolve();
        },
        /**
         * Render the widget. This function assumes that it is attached to the DOM.
         *
         * @private
         */
        _renderInDOM: function () {
            this.$el.empty();
            if(this.graph_data){
                var dashboard = $(QWeb.render('statistic_profit_ept',{widget: this}))
                this.$el.append(dashboard);
                this.$el.find('#l1').html(this.graph_data.level_profit_today);
                this.$el.find('#l2').html(this.graph_data.level_profit_week);
                this.$el.find('#l3').html(this.graph_data.level_profit_month)

            }

        },

        /*Render action for  Sale Orders */
        _sortOrders: function (e) {
          var self = this;
          this.context.sort_profit = e.currentTarget.value
            return this._rpc({model: self.model,method: 'read',args:[this.res_id],'context':this.context}).then(function (result) {
                if(result.length) {
                    self.graph_data = JSON.parse(result[0][self.match_key])
                    self.on_attach_callback()
                }
            })
        },
    });

    fieldRegistry.add('statistic_profit_ept', EmiproDashboarStatisticProfit);
    return {
        EmiproDashboarStatisticProfit: EmiproDashboarStatisticProfit
    };
});