odoo.define('graph_dashboard_ept.graph', function (require) {
    "use strict";

    var fieldRegistry = require('web.field_registry');
    var AbstractField = require('web.AbstractField');
    var core = require('web.core');
    var QWeb = core.qweb;
    var EmiproDashboardGraph = AbstractField.extend({
        events: {
            'click .day-filter': '_sortOrders',
        },
        jsLibs: [
            '/web/static/lib/Chart/Chart.js',
        ],
        init: function () {
            this._super.apply(this, arguments);
            this.graph_type = this.attrs.graph_type;

            // this.data = JSON.parse(this.value);
            this.data = this.recordData
            this.match_key = _.find(_.keys(this.data), function(key){ return key.includes('_order_data') })
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
            this.$canvas = $('<canvas width="800" height="400"/>');
            this.$el.addClass(cssClass);
            this.$el.empty();
            if(this.graph_data){
                var dashboard = $(QWeb.render('graph_dashboard_ept',{widget: this}))
                this.$el.append(dashboard);
                this.$el.find('.graph_ept').append(this.$canvas);
            } else {
                this.$el.append(this.$canvas);
            }
            var config, cssClass;
            var context = this.$canvas[0].getContext('2d');
            if (this.graph_type === 'line') {
                config = this._getLineChartConfig(context);
                cssClass = 'o_graph_linechart';
            }
            this.chart = new Chart(context, config);
        },

        _getLineChartConfig: function (context) {
            if(!_.isEmpty(this.graph_data) && this.graph_data.hasOwnProperty('values')){
                var labels = this.graph_data.values.map(function (pt) {
                    return pt.x;
                });

                return {
                    type: 'bar',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Total Sales',
                            data: this.graph_data.values,
                            backgroundColor: '#C4C4C4',
                            borderColor: '#C4C4C4',
                            borderWidth: 1
                        }]
                    },
                    options: {
                        scales: {
                            yAxes: [{
                                ticks: {
                                    beginAtZero:true
                                }
                            }]
                        }
                    },
                };
            }
        },

        /*Render action for  Sale Orders */
        _sortOrders: function (e) {
          var self = this;
          this.context.sort = e.currentTarget.value
            return this._rpc({model: self.model,method: 'read',args:[this.res_id],'context':this.context}).then(function (result) {
                if(result.length) {
                    self.graph_data = JSON.parse(result[0][self.match_key])
                    self.on_attach_callback()
                }
            })
        },
    });

    fieldRegistry.add('dashboard_graph_ept', EmiproDashboardGraph);
    return {
        EmiproDashboardGraph: EmiproDashboardGraph
    };
});