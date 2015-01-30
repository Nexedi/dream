/*global rJS, RSVP, jQuery,
 promiseEventListener, initGadgetMixin */
(function(window, rJS, RSVP, $, promiseEventListener, initGadgetMixin) {
    "use strict";
    function disableAllButtons(gadget) {
        // Prevent double click
        var i, button_list = gadget.props.element.getElementsByClassName("ui-btn");
        for (i = 0; i < button_list.length; i += 1) {
            button_list[i].disabled = true;
        }
    }
    function waitForKnowledgeExtraction(gadget) {
        return new RSVP.Queue().push(function() {
            return promiseEventListener(gadget.props.element.getElementsByClassName("knowledge_form")[0], "submit", false);
        }).push(function() {
            disableAllButtons(gadget);
            return gadget.aq_getAttachment({
                _id: gadget.props.jio_key,
                _attachment: "body.json"
            });
        }).push(function(body_json) {
            $.mobile.loading("show");
            // XXX Hardcoded relative URL
            return gadget.aq_ajax({
                url: "../../runKnowledgeExtraction",
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
                _attachment: "body.json",
                _data: JSON.stringify(json_data.data, null, 2),
                _mimetype: "application/json"
            });
        }).push(function() {
            return gadget.whoWantsToDisplayThisDocument(gadget.props.jio_key);
        }).push(function(url) {
            return gadget.pleaseRedirectMyHash(url);
        });
    }
    function waitForDeletion(gadget) {
        return new RSVP.Queue().push(function() {
            return promiseEventListener(gadget.props.element.getElementsByClassName("delete_form")[0], "submit", false);
        }).push(function() {
            disableAllButtons(gadget);
            // Delete jIO document
            return gadget.aq_remove({
                _id: gadget.props.jio_key
            });
        }).push(function() {
            return gadget.whoWantsToDisplayHome();
        }).push(function(url) {
            return gadget.pleaseRedirectMyHash(url);
        });
    }
    var gadget_klass = rJS(window);
    initGadgetMixin(gadget_klass);
    gadget_klass.declareAcquiredMethod("aq_remove", "jio_remove").declareAcquiredMethod("aq_getAttachment", "jio_getAttachment").declareAcquiredMethod("aq_putAttachment", "jio_putAttachment").declareAcquiredMethod("aq_get", "jio_get").declareAcquiredMethod("aq_ajax", "jio_ajax").declareAcquiredMethod("pleaseRedirectMyHash", "pleaseRedirectMyHash").declareAcquiredMethod("whoWantsToDisplayThisDocument", "whoWantsToDisplayThisDocument").declareAcquiredMethod("whoWantsToDisplayHome", "whoWantsToDisplayHome").declareMethod("render", function(options) {
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
            // XXX this breaks promise chain
            $(export_link).click(function() {
                $("#export_json").val(result_list[1]);
                return $("#export_form").submit();
            });
        });
    }).declareMethod("startService", function() {
        return RSVP.all([ waitForDeletion(this), waitForKnowledgeExtraction(this) ]);
    });
})(window, rJS, RSVP, jQuery, promiseEventListener, initGadgetMixin);