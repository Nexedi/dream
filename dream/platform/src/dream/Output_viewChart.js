/*global rJS, jQuery, initGadgetMixin, console */
/*jslint unparam: true */
(function (window, rJS, $, initGadgetMixin) {
  "use strict";

  var gadget_klass = rJS(window);
  initGadgetMixin(gadget_klass);
  gadget_klass
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("aq_getAttachment", "jio_getAttachment")

    /**
     * Stacked flot graph widget, as seen on http://www.flotcharts.org/flot/examples/stacking/index.html
     * The data is an object with two attributes "series" ( a list ) and "options" (a mapping of flot options).
     */

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
        "_attachment": "body.json"
      })
        .push(function (simulation_json) {
          var json_data = JSON.parse(simulation_json);
          gadget.props.data = json_data.result.result_list[options.result][
            options.action_definition.configuration.output_id];
        });
    })

    .declareMethod("startService", function () {

      // XXX Manually calculate width and height when resizing
      $.plot(
        this.props.element.querySelector(".graph_container"),
        this.props.data.series,
        this.props.data.options
      );
    });
}(window, rJS, jQuery, initGadgetMixin));
