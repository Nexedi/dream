/*global console, rJS, RSVP, initDocumentPageMixin, jQuery */
(function(window, rJS, RSVP, initDocumentPageMixin, $) {
    "use strict";
    function promiseEventListener(target, type, useCapture) {
        //////////////////////////
        // Resolve the promise as soon as the event is triggered
        // eventListener is removed when promise is cancelled/resolved/rejected
        //////////////////////////
        var handle_event_callback;
        function canceller() {
            target.removeEventListener(type, handle_event_callback, useCapture);
        }
        function resolver(resolve) {
            handle_event_callback = function(evt) {
                canceller();
                evt.stopPropagation();
                evt.preventDefault();
                resolve(evt);
                return false;
            };
            target.addEventListener(type, handle_event_callback, useCapture);
        }
        return new RSVP.Promise(resolver, canceller);
    }
    var gadget_klass = rJS(window);
    initDocumentPageMixin(gadget_klass);
    gadget_klass.ready(function(g) {
        g.props = {};
    }).ready(function(g) {
        return g.getElement().push(function(element) {
            g.props.element = element;
        });
    }).declareAcquiredMethod("aq_getAttachment", "jio_getAttachment").declareAcquiredMethod("aq_putAttachment", "jio_putAttachment").declareAcquiredMethod("aq_ajax", "jio_ajax").declareAcquiredMethod("pleaseRedirectMyHash", "pleaseRedirectMyHash").declareAcquiredMethod("whoWantToDisplayThisDocumentPage", "whoWantToDisplayThisDocumentPage").declareMethod("render", function(options) {
        this.props.jio_key = options.id;
    }).declareMethod("startService", function() {
        var gadget = this;
        return new RSVP.Queue().push(function() {
            return promiseEventListener(gadget.props.element.getElementsByClassName("run_form")[0], "submit", false);
        }).push(function() {
            // Prevent double click
            gadget.props.element.getElementsByClassName("ui-btn")[0].disabled = true;
            return gadget.aq_getAttachment({
                _id: gadget.props.jio_key,
                _attachment: "body.json"
            });
        }).push(function(body_json) {
            $.mobile.loading("show");
            // XXX Hardcoded relative URL
            return gadget.aq_ajax({
                url: "../../runSimulation",
                type: "POST",
                data: body_json,
                headers: {
                    "Content-Type": "application/json"
                }
            });
        }).push(undefined, function(error) {
            // Always drop the loader
            $.mobile.loading("hide");
            throw error;
        }).push(function(evt) {
            $.mobile.loading("hide");
            var json_data = JSON.parse(evt.target.responseText);
            if (json_data.success !== true) {
                throw new Error(json_data.error);
            }
            return gadget.aq_putAttachment({
                _id: gadget.props.jio_key,
                _attachment: "simulation.json",
                _data: JSON.stringify(json_data.data, null, 2),
                _mimetype: "application/json"
            });
        }).push(function(result) {
            return gadget.whoWantToDisplayThisDocumentPage("debug_json", gadget.props.jio_key);
        }).push(function(url) {
            return gadget.pleaseRedirectMyHash(url);
        });
    });
})(window, rJS, RSVP, initDocumentPageMixin, jQuery);