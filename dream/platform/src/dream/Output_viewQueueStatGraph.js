/*global rJS, jQuery, initGadgetMixin */
/*jslint nomen: true, unparam: true */
(function (window, rJS, $, initGadgetMixin) {
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
  initGadgetMixin(gadget_klass);
  gadget_klass
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
      gadget.props.result = options.result;

      return gadget.aq_getAttachment({
        "_id": gadget.props.jio_key,
        "_attachment": "simulation.json"
      })
        .push(function (simulation_json) {
          gadget.props.series = queue_stat_widget(
            JSON.parse(simulation_json)[gadget.props.result].result
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
}(window, rJS, jQuery, initGadgetMixin));
