/*global console, rJS, RSVP, initDocumentPageMixin, initGadgetMixin */
(function (window, rJS, RSVP, initDocumentPageMixin, initGadgetMixin) {
  "use strict";

  var gadget_klass = rJS(window);
  initGadgetMixin(gadget_klass);
  initDocumentPageMixin(gadget_klass);
  gadget_klass
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("aq_getAttachment", "jio_getAttachment")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function (options) {
      var gadget = this;
      this.props.jio_key = options.id;

      return new RSVP.Queue()
        .push(function () {
          return RSVP.all([
            gadget.aq_getAttachment({
              "_id": gadget.props.jio_key,
              "_attachment": "body.json"
            }),
            gadget.aq_getAttachment({
              "_id": gadget.props.jio_key,
              "_attachment": "simulation.json"
            })
          ]);
        })
        .push(function (result_list) {
          gadget.props.element.querySelector(".json_input").textContent =
            result_list[0];
          // XXX Hardcoded result
          gadget.props.element.querySelector(".json_output").textContent =
            JSON.stringify(JSON.parse(result_list[1])[0].result);
        });

    });

}(window, rJS, RSVP, initDocumentPageMixin, initGadgetMixin));
