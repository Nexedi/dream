/*global window, rJS, RSVP */
(function (window, rJS, RSVP) {
  "use strict";
  var gadget_klass = rJS(window);
  gadget_klass

    .ready(function (g) {
      g.props = {};
    })

    .ready(function (g) {
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
        });
    })

    .declareAcquiredMethod("aq_getAttachment", "jio_getAttachment")

    .declareMethod("render", function (options) {
      var jio_key = options.id, gadget = this;
      gadget.props.jio_key = jio_key;
      return new RSVP.Queue()
        .push(function () {
          /*jslint nomen: true*/
          return RSVP.all([
            gadget.aq_getAttachment({
              _id: jio_key,
              _attachment: "body.json"
            }), gadget.getDeclaredGadget("productionline") ]);
        })
        .push(function (result_list) {
          return result_list[1].render(result_list[0]);
        });
    })

    .declareMethod("startService", function () {
      return this.getDeclaredGadget("productionline")
        .push(function (productionline) {
          return productionline.startService();
        });
    });
}(window, rJS, RSVP));
