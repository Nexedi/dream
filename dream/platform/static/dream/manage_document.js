/*global console, rJS, RSVP, initDocumentPageMixin */
(function(window, rJS, RSVP, initDocumentPageMixin) {
    "use strict";
    function datatouri(data, mime_type) {
        var result = "data:";
        if (mime_type !== undefined) {
            result += mime_type;
        }
        return result + ";base64," + window.btoa(data);
    }
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
    }).declareAcquiredMethod("aq_remove", "jio_remove").declareAcquiredMethod("aq_getAttachment", "jio_getAttachment").declareAcquiredMethod("aq_get", "jio_get").declareAcquiredMethod("pleaseRedirectMyHash", "pleaseRedirectMyHash").declareAcquiredMethod("whoWantToDisplayHome", "whoWantToDisplayHome").declareMethod("render", function(options) {
        this.props.jio_key = options.id;
        var gadget = this;
        return new RSVP.Queue().push(function() {
            return RSVP.all([ gadget.aq_get({
                _id: options.id
            }), gadget.aq_getAttachment({
                _id: options.id,
                _attachment: "body.json"
            }) ]);
        }).push(function(result_list) {
            var export_link = gadget.props.element.querySelector(".export_link");
            export_link.download = result_list[0].data.title;
            export_link.href = datatouri(result_list[1], "application/json");
        });
    }).declareMethod("startService", function() {
        var gadget = this;
        return new RSVP.Queue().push(function() {
            return promiseEventListener(gadget.props.element.getElementsByClassName("delete_form")[0], "submit", false);
        }).push(function() {
            // Prevent double click
            gadget.props.element.getElementsByClassName("ui-btn")[0].disabled = true;
            // Delete jIO document
            return gadget.aq_remove({
                _id: gadget.props.jio_key
            });
        }).push(function(result) {
            return gadget.whoWantToDisplayHome();
        }).push(function(url) {
            return gadget.pleaseRedirectMyHash(url);
        });
    });
})(window, rJS, RSVP, initDocumentPageMixin);