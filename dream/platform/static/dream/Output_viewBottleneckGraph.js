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
            if (options.action_definition.configuration.select_label) {
                $(gadget.props.element.querySelector(".select_label")).text(options.action_definition.configuration.select_label);
            }
        });
    }).declareMethod("startService", function() {
        var first_option, datasets = this.props.data, graph_container = this.props.element.querySelector(".graph_container"), select = $(this.props.element.querySelector("select.choices"));
        function plotAccordingToChoices() {
            var data;
            if (select.val()) {
                data = datasets[select.val()];
                $.plot(graph_container, data.series, data.options);
            }
        }
        // insert options in the select
        $.each(datasets, function(key, val) {
            select.append("<option value='" + key + "'>" + key + "</option>");
        });
        first_option = $($("option", select).get(0));
        first_option.attr("selected", "selected");
        select.selectmenu("refresh", true);
        select.bind("change", plotAccordingToChoices);
        plotAccordingToChoices();
    });
})(window, rJS, jQuery, initGadgetMixin);