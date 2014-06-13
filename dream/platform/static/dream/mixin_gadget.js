(function(window) {
    "use strict";
    window.initGadgetMixin = function(gadget_klass) {
        gadget_klass.ready(function(g) {
            g.props = {};
        }).ready(function(g) {
            return g.getElement().push(function(element) {
                g.props.element = element;
            });
        });
    };
})(window);