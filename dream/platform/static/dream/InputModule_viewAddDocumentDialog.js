/*global rJS, RSVP, promiseEventListener, promiseReadAsText,
         initGadgetMixin */
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
            json_data = json;
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
    function waitForNew(gadget) {
        var json_data = {
            nodes: {},
            edges: {},
            preference: {},
            general: {},
            wip_part_spreadsheet: [ [ "Order ID", "Due Date", "Priority", "Project Manager", "Part", "Part Type", "Sequence", "Processing Times", "Prerequisites Parts" ] ],
            shift_spreadsheet: [ [ "Day", "Machines", // XXX more generic name ?
            "Start", "End" ] ],
            capacity_by_project_spreadsheet: [ [ "Project Name", "Sequence", "Capacity Requirements" ] ],
            capacity_by_station_spreadsheet: [ [ "Day", "CS1" ] ]
        }, name = "FromScratch";
        return new RSVP.Queue().push(function() {
            return promiseEventListener(gadget.props.element.getElementsByClassName("new_form")[0], "submit", false);
        }).push(function(evt) {
            // Prevent double click
            evt.target.getElementsByClassName("ui-btn")[0].disabled = true;
            return createDocument(gadget, name);
        }).push(function(jio_document) {
            // Add JSON as attachment
            return gadget.aq_putAttachment({
                _id: jio_document.id,
                _attachment: "body.json",
                _data: JSON.stringify(json_data),
                _mimetype: "application/json"
            });
        });
    }
    var gadget_klass = rJS(window);
    initGadgetMixin(gadget_klass);
    gadget_klass.declareAcquiredMethod("aq_post", "jio_post").declareAcquiredMethod("aq_putAttachment", "jio_putAttachment").declareAcquiredMethod("pleaseRedirectMyHash", "pleaseRedirectMyHash").declareAcquiredMethod("whoWantToDisplayThisDocument", "whoWantToDisplayThisDocument").declareMethod("startService", function() {
        var gadget = this;
        return new RSVP.Queue().push(function() {
            return RSVP.any([ waitForImport(gadget), waitForNew(gadget) ]);
        }).push(function(result) {
            return gadget.whoWantToDisplayThisDocument(result.id);
        }).push(function(url) {
            return gadget.pleaseRedirectMyHash(url);
        });
    });
})(window, rJS, RSVP, promiseEventListener, promiseReadAsText, initGadgetMixin);