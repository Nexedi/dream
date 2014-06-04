/*global console, rJS, RSVP, initDocumentPageMixin */
(function (window, rJS, RSVP, initDocumentPageMixin) {
  "use strict";

  var gadget_klass = rJS(window);
  initDocumentPageMixin(gadget_klass);
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
    })

    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("aq_getAttachment", "jio_getAttachment")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function (options) {
      var jio_key = options.id,
        gadget = this;
      gadget.props.jio_key = jio_key;
      return gadget.aq_getAttachment({
        "_id": jio_key,
        "_attachment": "body.json"
      })
        .push(function (result) {
          gadget.props.element.textContent = result;
        });
    });
}(window, rJS, RSVP, initDocumentPageMixin));
