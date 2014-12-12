/*global rJS, RSVP, jQuery, Handlebars,
  promiseEventListener, initGadgetMixin, console */
/*jslint nomen: true */
(function(window, rJS, RSVP, Handlebars, initGadgetMixin) {
    "use strict";
    /////////////////////////////////////////////////////////////////
    // Handlebars
    /////////////////////////////////////////////////////////////////
    // Precompile the templates while loading the first gadget instance
    var gadget_klass = rJS(window), source = gadget_klass.__template_element.getElementById("label-template").innerHTML, label_template = Handlebars.compile(source);
    initGadgetMixin(gadget_klass);
    gadget_klass.declareMethod("render", function(options, node_id) {
        // XXX node_id is added like a property so that one can change the node
        // id
        var gadget = this, queue;
        console.log("FIELDSET RENDER 1");
        console.log(options);
        console.log(node_id);
        gadget.props.key = options.key;
        // used for recursive fieldsets
        gadget.props.field_gadget_list = [];
        function addField(property_id, property_definition, value) {
            var sub_gadget;
            queue.push(function() {
                // XXX this is incorrect for recursive fieldsets.
                // we should use nested fieldset with legend
                console.log("insertingAdjacentHTML for:" + property_id);
                gadget.props.element.insertAdjacentHTML("beforeend", label_template({
                    "for": property_id,
                    name: property_definition.name || property_id
                }));
                console.log("....................");
                console.log(property_id);
                console.log(property_definition);
                console.log(value);
                // XXX maybe type should be used instead
                if (property_definition.allOf) {
                    // if there is type property then remove it
                    if (property_definition.allOf[0].type) {
                        delete property_definition.allOf[0].type;
                    }
                    return gadget.declareGadget("../expandable_field/index.html");
                }
                if (property_definition.type === "object") {
                    // Create a recursive fieldset for this key.
                    return gadget.declareGadget("../fieldset/index.html");
                }
                if (property_definition.type === "number") {
                    return gadget.declareGadget("../number_field/index.html");
                }
                if (property_definition.enum) {
                    return gadget.declareGadget("../list_field/index.html");
                }
                return gadget.declareGadget("../string_field/index.html");
            }).push(function(gg) {
                sub_gadget = gg;
                return sub_gadget.render({
                    key: property_id,
                    value: value,
                    property_definition: property_definition
                });
            }).push(function() {
                return sub_gadget.getElement();
            }).push(function(sub_element) {
                gadget.props.element.appendChild(sub_element);
                gadget.props.field_gadget_list.push(sub_gadget);
            });
        }
        queue = new RSVP.Queue().push(function() {
            if (node_id) {
                addField("id", {
                    type: "string"
                }, node_id);
            }
            Object.keys(options.property_definition.properties).forEach(function(property_name) {
                var property_definition = options.property_definition.properties[property_name], value = property_definition.default, i = 0, property;
                if (property_definition.allOf) {
                    if (property_definition.allOf[0].properties) {
                        for (property in property_definition.allOf[0].properties) {
                            if (property_definition.allOf[0].properties.hasOwnProperty(property)) {
                                i += 1;
                                if (i > 1) {
                                    console.log("something is wrong!");
                                }
                                value = property_definition.allOf[0].properties[property].default;
                            }
                        }
                    }
                }
                console.log("TRYING TO FIND A VALUE!!!!");
                console.log(options);
                console.log(options.value);
                console.log(property_name);
                value = (options.value || {})[property_name] === undefined ? value : options.value[property_name];
                if (property_name !== "coordinate" && property_name !== "_class" && property_name !== "id") {
                    console.log("ADDING FIELD FOR " + property_name + "!!!!!!!");
                    addField(property_name, property_definition, value);
                }
            });
        });
        return queue;
    }).declareMethod("getContent", function() {
        console.log("GET CONTENT SIMPLE FIELDSET");
        var i, promise_list = [], gadget = this;
        for (i = 0; i < this.props.field_gadget_list.length; i += 1) {
            promise_list.push(this.props.field_gadget_list[i].getContent());
        }
        return RSVP.Queue().push(function() {
            return RSVP.all(promise_list);
        }).push(function(result_list) {
            var name, result = {}, content = result;
            if (gadget.props.key) {
                content = result[gadget.props.key] = {};
            }
            for (i = 0; i < result_list.length; i += 1) {
                for (name in result_list[i]) {
                    if (result_list[i].hasOwnProperty(name)) {
                        content[name] = result_list[i][name];
                    }
                }
            }
            console.log("GET CONTENT SIMPLE FIELDSET 2");
            console.log(result);
            return result;
        });
    }).declareMethod("startService", function() {
        console.log("startservice FIElDSET 1");
        var gadget = this, i, promise_list = [];
        for (i = 0; i < gadget.props.field_gadget_list.length; i += 1) {
            if (gadget.props.field_gadget_list[i].startService) {
                promise_list.push(gadget.props.field_gadget_list[i].startService());
            }
        }
        console.log("there are " + promise_list.length + " subgadget promises");
        return RSVP.all(promise_list);
    });
})(window, rJS, RSVP, Handlebars, initGadgetMixin);