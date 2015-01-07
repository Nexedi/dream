/*global rJS, initGadgetMixin */
(function(window, rJS, initGadgetMixin) {
    "use strict";
    var gadget_klass = rJS(window);
    initGadgetMixin(gadget_klass);
    gadget_klass.declareAcquiredMethod("aq_getAttachment", "jio_getAttachment").declareMethod("render", function(options) {
        var gadget = this;
        this.props.jio_key = options.id;
        this.props.result = options.result;
        return gadget.aq_getAttachment({
            _id: gadget.props.jio_key,
            _attachment: "simulation.json"
        }).push(function(result_json) {
            var document = JSON.parse(result_json), result = document.result.result_list, input = {
                input: document.input,
                graph: document.graph,
                general: document.general
            }, configuration = {
                application_configuration: document.application_configuration,
                class_definition: document.class_definition,
                constrains: document.constrains
            };
            gadget.props.element.querySelector(".json_input").textContent = JSON.stringify(input, undefined, " ");
            gadget.props.element.querySelector(".json_output").textContent = JSON.stringify(result[gadget.props.result], undefined, " ");
            gadget.props.element.querySelector(".json_configuration").textContent = JSON.stringify(configuration, undefined, " ");
        });
    });
})(window, rJS, initGadgetMixin);