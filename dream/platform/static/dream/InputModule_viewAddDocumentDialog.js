/*global rJS, RSVP, promiseEventListener, promiseReadAsText,
         initGadgetMixin, prompt */
(function(window, rJS, RSVP, promiseEventListener, promiseReadAsText, initGadgetMixin) {
    "use strict";
    function createDocument(gadget, name) {
        var now = new Date();
        // Create jIO document
        return gadget.aq_post({
            title: name,
            type: "Dream",
            format: "application/json",
            modified: now.toUTCString(),
            date: now.getFullYear() + "-" + (now.getMonth() + 1) + "-" + now.getDate()
        });
    }
    function waitForImport(gadget) {
        var json_data, name;
        return new RSVP.Queue().push(function() {
            return promiseEventListener(gadget.props.element.getElementsByClassName("import_form")[0], "submit", false);
        }).push(function(evt) {
            // Prevent double click
            evt.target.getElementsByClassName("ui-btn")[0].disabled = true;
            var file = evt.target.dream_import.files[0];
            name = file.name;
            return promiseReadAsText(file);
        }).push(function(json) {
            var data = JSON.parse(json);
            data.general.name = name;
            json_data = JSON.stringify(data);
            return createDocument(gadget, name);
        }).push(function(jio_document) {
            // Add JSON as attachment
            return gadget.aq_putAttachment({
                _id: jio_document.id,
                _attachment: "body.json",
                _data: json_data,
                _mimetype: "application/json"
            });
        });
    }
    function waitForCreateNew(gadget) {
        var json_data, name;
        return new RSVP.Queue().push(function() {
            return promiseEventListener(gadget.props.element.getElementsByClassName("create_new_form")[0], "submit", false);
        }).push(function(evt) {
            // Prevent double click
            evt.target.getElementsByClassName("ui-btn")[0].disabled = true;
            return gadget.aq_ajax({
                url: "../DefaultConfiguration.json",
                type: "GET"
            });
        }).push(function(evt) {
            name = prompt("Name for this model");
            var data = JSON.parse(evt.target.responseText);
            data.general.name = name;
            json_data = JSON.stringify(data);
            return createDocument(gadget, name);
        }).push(function(jio_document) {
            // Add JSON as attachment
            return gadget.aq_putAttachment({
                _id: jio_document.id,
                _attachment: "body.json",
                _data: json_data,
                _mimetype: "application/json"
            });
        });
    }
    var gadget_klass = rJS(window);
    initGadgetMixin(gadget_klass);
    gadget_klass.declareAcquiredMethod("aq_post", "jio_post").declareAcquiredMethod("aq_ajax", "jio_ajax").declareAcquiredMethod("aq_putAttachment", "jio_putAttachment").declareAcquiredMethod("pleaseRedirectMyHash", "pleaseRedirectMyHash").declareAcquiredMethod("whoWantsToDisplayThisDocument", "whoWantsToDisplayThisDocument").declareMethod("startService", function() {
        var gadget = this;
        return new RSVP.Queue().push(function() {
            return RSVP.any([ waitForImport(gadget), waitForCreateNew(gadget) ]);
        }).push(function(result) {
            return gadget.whoWantsToDisplayThisDocument(result.id);
        }).push(function(url) {
            return gadget.pleaseRedirectMyHash(url);
        });
    });
})(window, rJS, RSVP, promiseEventListener, promiseReadAsText, initGadgetMixin);