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
        var jio_key = options.id, gadget = this;
        gadget.props.jio_key = jio_key;
        return new RSVP.Queue().push(function() {
            return RSVP.all([ gadget.aq_getAttachment({
                _id: jio_key,
                _attachment: "body.json"
            }), gadget.getDeclaredGadget("tableeditor") ]);
        }).push(function(result_list) {
            return result_list[1].render(JSON.stringify(JSON.parse(result_list[0]).shift_spreadsheet));
        });
    }).declareMethod("startService", function() {
        return this.getDeclaredGadget("tableeditor").push(function(tableeditor) {
            return tableeditor.startService();
        });
    });
})(window, rJS, RSVP, initDocumentPageMixin);