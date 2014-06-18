/*global window, rJS, Handlebars */
/*jslint nomen: true */
(function(window, rJS, Handlebars) {
    "use strict";
    /////////////////////////////////////////////////////////////////
    // Handlebars
    /////////////////////////////////////////////////////////////////
    // Precompile the templates while loading the first gadget instance
    var gadget_klass = rJS(window), option_source = gadget_klass.__template_element.getElementById("option-template").innerHTML, option_template = Handlebars.compile(option_source), selected_option_source = gadget_klass.__template_element.getElementById("option-template").innerHTML, selected_option_template = Handlebars.compile(selected_option_source);
    gadget_klass.ready(function(g) {
        return g.getElement().push(function(element) {
            g.element = element;
        });
    }).declareMethod("render", function(options) {
        var select = this.element.getElementsByTagName("select")[0], i, template, field_json = options.field_json, tmp = "";
        select.setAttribute("name", field_json.key);
        for (i = 0; i < field_json.items.length; i += 1) {
            if (field_json.items[i][1] === field_json.default[0]) {
                template = selected_option_template;
            } else {
                template = option_template;
            }
            tmp += template({
                value: field_json.items[i][1],
                text: field_json.items[i][0]
            });
        }
        select.innerHTML += tmp;
    });
})(window, rJS, Handlebars);