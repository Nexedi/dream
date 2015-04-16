/*global rJS, jQuery, initGadgetMixin, console */
/*jslint unparam: true */
(function(window, rJS, $, initGadgetMixin) {
    "use strict";
    var gadget_klass = rJS(window);
    initGadgetMixin(gadget_klass);
    gadget_klass.declareAcquiredMethod("aq_getAttachment", "jio_getAttachment").declareMethod("render", function(options) {
        var jio_key = options.id, gadget = this;
        gadget.props.jio_key = jio_key;
        gadget.props.result = options.result;
        return gadget.aq_getAttachment({
            _id: gadget.props.jio_key,
            _attachment: "body.json"
        }).push(function(simulation_json) {
            var json_data = JSON.parse(simulation_json);
            gadget.props.data = json_data.result.result_list[options.result][options.action_definition.configuration.output_id];
        });
    }).declareMethod("startService", function() {
        var i = 0, options = this.props.data.options, datasets = this.props.data.series, graph_container = this.props.element.querySelector(".graph_container"), choice_container = $(this.props.element.querySelector(".choices"));
        $.plot(graph_container, this.props.data.series, this.props.data.options);
        // Add checkboxes to toggle series on & off, inspired from http//:www.flotcharts.org/flot/examples/series-toggle/index.html
        function plotAccordingToChoices() {
            var data = [];
            choice_container.find("input:checked").each(function() {
                var key = $(this).attr("name");
                if (key && datasets[key]) {
                    data.push(datasets[key]);
                }
            });
            if (data.length > 0) {
                $.plot(graph_container, data, options);
            }
        }
        if (!this.props.data.options.bars) {
            if (this.props.data.series.length >= 5) {
                // display the boxes
                $(graph_container).css({
                    width: "90%"
                });
                // hard-code color indices to prevent them from shifting as
                // series are turned on/off
                $.each(datasets, function(key, val) {
                    val.color = i;
                    i += 1;
                });
                // insert checkboxes
                $.each(datasets, function(key, val) {
                    choice_container.append("<br/><input type='checkbox' name='" + key + "' checked='checked' id='id" + key + "'></input>" + "<label style='display:inline' for='id" + key + "'>" + val.label + "</label>");
                });
                choice_container.find("input").click(plotAccordingToChoices);
                plotAccordingToChoices();
            }
        }
    });
})(window, rJS, jQuery, initGadgetMixin);