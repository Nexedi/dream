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
            _attachment: "body.json"
        }).push(function(result_json) {
            var document = JSON.parse(result_json);
            gadget.props.element.querySelector(".json").textContent = JSON.stringify(document, undefined, " ");
        });
    });
})(window, rJS, initGadgetMixin);