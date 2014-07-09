(function (window) {
  "use strict";
  window.initGadgetMixin = function (gadget_klass) {

    gadget_klass
      /////////////////////////////////////////////////////////////////
      // ready
      /////////////////////////////////////////////////////////////////
      // Init local properties
      .ready(function (g) {
        g.props = {};
      })

      // Assign the element to a variable
      .ready(function (g) {
        return g.getElement()
          .push(function (element) {
            g.props.element = element;
          });
      });
  };

}(window));
