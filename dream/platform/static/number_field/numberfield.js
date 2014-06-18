/*global window, rJS */
(function(window, rJS) {
    "use strict";
    rJS(window).ready(function(gadget) {
        return gadget.getElement().push(function(element) {
            gadget.element = element;
        });
    }).declareMethod("render", function(options) {
        var input = this.element.querySelector("input"), field_json = options.field_json || {};
        input.setAttribute("value", field_json.value);
        input.setAttribute("name", field_json.key);
        input.setAttribute("title", field_json.title);
    }).declareMethod("getContent", function() {
        var input = this.element.querySelector("input"), result = {};
        if (input.value !== "") {
            result[input.getAttribute("name")] = parseFloat(input.value);
        } else {
            result[input.getAttribute("name")] = null;
        }
        return result;
    });
})(window, rJS);