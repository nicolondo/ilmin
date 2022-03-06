odoo.define('tree_dashboard_ept.tree', function (require) {
    "use strict";

    var fieldRegistry = require('web.field_registry');
    var AbstractField = require('web.AbstractField');
    var core = require('web.core');
    var QWeb = core.qweb;
    var EmiproDashboardTree= AbstractField.extend({

        init: function () {
            this._super.apply(this, arguments);

            // this.data = JSON.parse(this.value);
            this.data = this.recordData
            this.match_key = _.find(_.keys(this.data), function(key){ return key.includes('tree_data') })
            this.graph_data = this.match_key.length ? JSON.parse(this.data[this.match_key]) : {}
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
            var dashboard = $(QWeb.render('graph_tree_ept',{widget: this}))
            this.$el.append(dashboard);
            var config = this._getTreeConfig();
            $("#my_tree").click();

        },

        _getTreeConfig: function () {
            if(!_.isEmpty(this.graph_data)){

                        let tree = this.graph_data.tree
                        let treeParams = this.graph_data.tree_params

                        return treeMaker(tree, {
                            id: 'my_tree',
                            treeParams: treeParams,
                            link_width: '2px',
                            link_color: '#818181'
                        });

            }
        },
    });

    fieldRegistry.add('dashboard_tree_ept', EmiproDashboardTree);
    return {
        EmiproDashboardTree: EmiproDashboardTree
    };
});