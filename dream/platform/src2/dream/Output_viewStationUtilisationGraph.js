/*global rJS, jQuery, initGadgetMixin */
/*jslint unparam: true */
(function (window, rJS, $, initGadgetMixin) {
  "use strict";

  function station_utilisation_graph_widget(output_data) {
    var blockage_data = [],
      waiting_data = [],
      failure_data = [],
      working_data = [],
      ticks = [],
      counter = 1,
      series,
      options;

    // XXX output is still elementList ???
    $.each(
      output_data.elementList.sort(
        function (a, b) {
          return a.id < b.id ? -1 : 1;
        }
      ),
      function (idx, obj) {
        // add each object that has a working ratio
        if ((obj.results !== undefined) &&
            (obj.results.working_ratio !== undefined)) {
          /* when there is only one replication, the ratio is given as a float,
              otherwise we have a mapping avg, ub lb */
          var blockage_ratio = 0.0,
            working_ratio = 0.0,
            waiting_ratio = 0.0,
            failure_ratio = 0.0;

          if (obj.results.blockage_ratio !== undefined) {
            if (obj.results.blockage_ratio.avg !== undefined) {
              blockage_ratio = obj.results.blockage_ratio.avg;
            } else {
              blockage_ratio = obj.results.blockage_ratio;
            }
          }
          blockage_data.push([counter, blockage_ratio]);

          // XXX merge setup & loading ratio in working ratio for now

          if (obj.results.setup_ratio !== undefined) {
            if (obj.results.setup_ratio.avg !== undefined) {
              working_ratio += obj.results.setup_ratio.avg;
            } else {
              working_ratio += obj.results.setup_ratio;
            }
          }
          if (obj.results.loading_ratio !== undefined) {
            if (obj.results.loading_ratio.avg !== undefined) {
              working_ratio += obj.results.loading_ratio.avg;
            } else {
              working_ratio += obj.results.loading_ratio;
            }
          }
          if (obj.results.working_ratio !== undefined) {
            if (obj.results.working_ratio.avg !== undefined) {
              working_ratio += obj.results.working_ratio.avg;
            } else {
              working_ratio += obj.results.working_ratio;
            }
          }
          working_data.push([counter, working_ratio]);

          if (obj.results.waiting_ratio !== undefined) {
            if (obj.results.waiting_ratio.avg !== undefined) {
              waiting_ratio = obj.results.waiting_ratio.avg;
            } else {
              waiting_ratio = obj.results.waiting_ratio;
            }
          }
          waiting_data.push([counter, waiting_ratio]);

          if (obj.results.failure_ratio !== undefined) {
            if (obj.results.failure_ratio.avg !== undefined) {
              failure_ratio = obj.results.failure_ratio.avg;
            } else {
              failure_ratio = obj.results.failure_ratio;
            }
          }
          failure_data.push([counter, failure_ratio]);

          ticks.push([counter, obj.id]);
          counter += 1;
        }
      }
    );

    series = [{
      label: "Working",
      data: working_data
    }, {
      label: "Waiting",
      data: waiting_data
    }, {
      label: "Failures",
      data: failure_data
    }, {
      label: "Blockage",
      data: blockage_data
    }];

    options = {
      xaxis: {
        minTickSize: 1,
        ticks: ticks
      },
      yaxis: {
        max: 100
      },
      series: {
        bars: {
          show: true,
          barWidth: 0.8,
          align: "center"
        },
        stack: true
      }
    };
    return [series, options];
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
          gadget.props.result_list = station_utilisation_graph_widget(
            JSON.parse(simulation_json)[gadget.props.result].result
          );
        });
    })

    .declareMethod("startService", function () {
      // XXX Manually calculate width and height when resizing
      $.plot(
        this.props.element.querySelector(".graph_container"),
        this.props.result_list[0],
        this.props.result_list[1]
      );
    });
}(window, rJS, jQuery, initGadgetMixin));
