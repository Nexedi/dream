/*global console, rJS, RSVP, initDocumentPageMixin, jQuery */
/*jslint nomen: true */
(function (window, rJS, RSVP, initDocumentPageMixin, $) {
  "use strict";

  function queue_stat_widget(output_data) {
    /* FIXME: does not support more than one replic.
     * + see george email to integrate without the need of an EG
     */
    var series = [];
    $.each(output_data.elementList, function (idx, el) {
      if (el._class === 'Dream.Queue') {
        series.push({label: el.name || el.id,
                     data: el.wip_stat_list});
      }
    });
    return series;
  }

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
        "_id": gadget.props.jio_key,
        "_attachment": "simulation.json"
      })
        .push(function (simulation_json) {
          gadget.props.series = queue_stat_widget(
            // XXX Hardcoded result
            JSON.parse(simulation_json)[0].result
          );
        });
    })

    .declareMethod("startService", function () {
      // XXX Manually calculate width and height when resizing
      $.plot(
        this.props.element.querySelector(".graph_container"),
        this.props.series
      );
    });
}(window, rJS, RSVP, initDocumentPageMixin, jQuery));
