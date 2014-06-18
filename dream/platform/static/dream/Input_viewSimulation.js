/*global rJS, RSVP, jQuery, Handlebars,
  promiseEventListener, initGadgetMixin */
/*jslint nomen: true */
(function(window, rJS, RSVP, $, Handlebars, promiseEventListener, initGadgetMixin) {
    "use strict";
    function saveForm(gadget) {
        var general = {};
        return new RSVP.Queue().push(function() {
            var i, promise_list = [];
            for (i = 0; i < gadget.props.gadget_list.length; i += 1) {
                promise_list.push(gadget.props.gadget_list[i].getContent());
            }
            return RSVP.all(promise_list);
        }).push(function(result_list) {
            var i, result, key;
            for (i = 0; i < result_list.length; i += 1) {
                result = result_list[i];
                for (key in result) {
                    if (result.hasOwnProperty(key)) {
                        // Drop empty
                        if (result[key]) {
                            general[key] = result[key];
                        }
                    }
                }
            }
            // Always get a fresh version, to prevent deleting spreadsheet & co
            return gadget.aq_getAttachment({
                _id: gadget.props.jio_key,
                _attachment: "body.json"
            });
        }).push(function(body) {
            var data = JSON.parse(body);
            data.general = general;
            return gadget.aq_putAttachment({
                _id: gadget.props.jio_key,
                _attachment: "body.json",
                _data: JSON.stringify(data, null, 2),
                _mimetype: "application/json"
            });
        });
    }
    function runSimulation(gadget) {
        return new RSVP.Queue().push(function() {
            return gadget.aq_getAttachment({
                _id: gadget.props.jio_key,
                _attachment: "body.json"
            });
        }).push(function(body_json) {
            // XXX Hardcoded relative URL
            return gadget.aq_ajax({
                url: "../../runSimulation",
                type: "POST",
                data: body_json,
                headers: {
                    "Content-Type": "application/json"
                }
            });
        }).push(function(evt) {
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
        }).push(function() {
            return gadget.whoWantToDisplayThisDocument(gadget.props.jio_key, "view_result");
        }).push(function(url) {
            return gadget.pleaseRedirectMyHash(url);
        });
    }
    function waitForRunSimulation(gadget) {
        var submit_evt;
        return new RSVP.Queue().push(function() {
            return promiseEventListener(gadget.props.element.getElementsByClassName("save_form")[0], "submit", false);
        }).push(function(evt) {
            submit_evt = evt;
            // Prevent double click
            evt.target.getElementsByClassName("ui-btn")[0].disabled = true;
            $.mobile.loading("show");
            return saveForm(gadget);
        }).push(function() {
            return runSimulation(gadget);
        }).push(undefined, function(error) {
            // Always drop the loader
            $.mobile.loading("hide");
            throw error;
        }).push(function() {
            submit_evt.target.getElementsByClassName("ui-btn")[0].disabled = false;
            $.mobile.loading("hide");
        });
    }
    /////////////////////////////////////////////////////////////////
    // Handlebars
    /////////////////////////////////////////////////////////////////
    // Precompile the templates while loading the first gadget instance
    var gadget_klass = rJS(window), source = gadget_klass.__template_element.getElementById("label-template").innerHTML, label_template = Handlebars.compile(source);
    initGadgetMixin(gadget_klass);
    gadget_klass.declareAcquiredMethod("aq_getAttachment", "jio_getAttachment").declareAcquiredMethod("aq_putAttachment", "jio_putAttachment").declareAcquiredMethod("aq_ajax", "jio_ajax").declareAcquiredMethod("aq_getConfigurationDict", "getConfigurationDict").declareAcquiredMethod("pleaseRedirectMyHash", "pleaseRedirectMyHash").declareAcquiredMethod("whoWantToDisplayThisDocument", "whoWantToDisplayThisDocument").declareMethod("render", function(options) {
        var i, gadget = this, property, parent_element = gadget.props.element.querySelector(".simulation_parameters"), value, queue, data;
        this.props.jio_key = options.id;
        function addField(property, value) {
            var sub_gadget;
            queue.push(function() {
                parent_element.insertAdjacentHTML("beforeend", label_template({
                    label: property.name || property.id
                }));
                if (property.type === "number") {
                    return gadget.declareGadget("../number_field/index.html");
                }
                return gadget.declareGadget("../string_field/index.html");
            }).push(function(gg) {
                sub_gadget = gg;
                value = data[property.id] || value;
                return sub_gadget.render({
                    field_json: {
                        title: property.description || "",
                        key: property.id,
                        value: value
                    }
                });
            }).push(function() {
                return sub_gadget.getElement();
            }).push(function(sub_element) {
                parent_element.appendChild(sub_element);
                gadget.props.gadget_list.push(sub_gadget);
            });
        }
        queue = gadget.aq_getAttachment({
            _id: gadget.props.jio_key,
            _attachment: "body.json"
        }).push(function(json) {
            data = JSON.parse(json).general;
            return gadget.aq_getConfigurationDict();
        }).push(function(configuration_dict) {
            var property_list = configuration_dict["Dream-Configuration"].property_list;
            gadget.props.gadget_list = [];
            for (i = 0; i < property_list.length; i += 1) {
                property = property_list[i];
                if (property._class === "Dream.Property") {
                    value = property._default || "";
                    addField(property, value);
                }
            }
        });
        return queue;
    }).declareMethod("startService", function() {
        return waitForRunSimulation(this);
    });
})(window, rJS, RSVP, jQuery, Handlebars, promiseEventListener, initGadgetMixin);