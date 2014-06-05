/*global console, rJS, RSVP, initDocumentPageMixin */
(function(window, rJS, RSVP, initDocumentPageMixin) {
    "use strict";
    var gadget_klass = rJS(window);
    initDocumentPageMixin(gadget_klass);
    gadget_klass.ready(function(g) {
        g.props = {};
    }).ready(function(g) {
        return g.getElement().push(function(element) {
            g.props.element = element;
        });
    }).declareAcquiredMethod("aq_getAttachment", "jio_getAttachment").declareMethod("render", function(options) {
        var gadget = this;
        this.props.jio_key = options.id;
        return new RSVP.Queue().push(function() {
            return RSVP.all([ gadget.aq_getAttachment({
                _id: gadget.props.jio_key,
                _attachment: "body.json"
            }), gadget.aq_getAttachment({
                _id: gadget.props.jio_key,
                _attachment: "simulation.json"
            }) ]);
        }).push(function(result_list) {
            gadget.props.element.querySelector(".json_input").textContent = result_list[0];
            // XXX Hardcoded result
            gadget.props.element.querySelector(".json_output").textContent = JSON.stringify(JSON.parse(result_list[1])[0].result);
        });
    });
})(window, rJS, RSVP, initDocumentPageMixin);