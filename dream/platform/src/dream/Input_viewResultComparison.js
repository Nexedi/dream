/*global rJS, RSVP, initGadgetMixin, jQuery */
/*jslint nomen: true */
(function (window, rJS, RSVP, initGadgetMixin, $) {
  "use strict";

  var gadget_klass = rJS(window);
  
  initGadgetMixin(gadget_klass);
  gadget_klass

    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("aq_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("whoWantsToDisplayThisResult",
                           "whoWantsToDisplayThisResult")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function (options) {
      var gadget = this, order_lateness = {}, general_json;
      this.props.jio_key = options.id;

      return gadget.aq_getAttachment({
        "_id": gadget.props.jio_key,
        "_attachment": "body.json"
      })
        .push(undefined, function (error) {
          if (error.status_code === 404) {
            // Simulation not yet generated
            return JSON.stringify([]);
          }
          throw error;
        })
        .push(function (sim_json) {
          var json = JSON.parse(sim_json),
            result = json.result,
            result_list = [],
            document_list = [],
            i;
          general_json = result;
          if (result && result.result_list) {
            document_list = result.result_list;
          }
          for (i = 0; i < document_list.length; i += 1) {
            result_list.push(RSVP.all([
              gadget.whoWantsToDisplayThisResult(gadget.props.jio_key, i),
              document_list[i]
            ]));
          }
          return RSVP.all(result_list);
        })
        .push(function (result_list) {
          var i, link, result, scenario_id,
            calculateOrderLateness = function(order_id) {
              var order = result.order_lateness[order_id];
              order.link = link;
              if (!order_lateness[order_id]){
                order_lateness[order_id] = {};
              }
              order_lateness[order_id][scenario_id] = order;
          };
          for (i=0; i<result_list.length; i+=1) {
            scenario_id = result_list[i][1].name || i;
            link = result_list[i][0];
            result = result_list[i][1];
            Object.keys(result.order_lateness).forEach(calculateOrderLateness);
          }
          return gadget.getDeclaredGadget("tableeditor");
        })
        .push(function(tableeditor) {
          var i,
            data = {}, data_list = [],
            colHeaders = ["Project"],
            columns = [{data: "id"}];
          
          Object.keys(order_lateness).forEach(function(order_id) {
            var order = order_lateness[order_id];
            order.id = order_id;
            data[order_id] = order;
          });

          /*jslint unparam: true */
          function orderHtmlRenderer(instance, td, row, col, prop, value, cellProperties) {
            var a, color = "yellow";
            if (value) {
              if (value.delay < 0.5) {
                color = "green";
              }
              if (value.delay > 0.5) {
                color = "red";
              }
              if ( value.color ) { // if color passed in plugin, we use it as is.
                color = value.color;
              }
              $(td).text("").css({"background-color": color});
              a = $("<a>").attr("href", value.link)
                .text(value.completionDate + "\n" + (value.delayText || (value.delay || 0).toFixed(0)))
                .css({color: "black", "text-shadow": "none"});
              a.appendTo(td);
            }
            return td;
          }
          
          for (i=0; i < general_json.result_list.length; i+=1) {
            colHeaders.push(general_json.result_list[i].name || ("Solution #" + (i+1)));
            columns.push({data: general_json.result_list[i].name || i, renderer: orderHtmlRenderer});
          }
          
          Object.keys(data).forEach(function(order_id) {
            data_list.push(order_lateness[order_id]);
          });
          
          return tableeditor.render(
            JSON.stringify(data_list),
            {
              colHeaders: colHeaders,
              columns: columns,
              readOnly: true
            }
          );
        });
      })
      .declareMethod("startService", function () {
        return this.getDeclaredGadget("tableeditor")
          .push(function (tableeditor) {
            return tableeditor.startService();
        });
    });
}(window, rJS, RSVP, initGadgetMixin, jQuery));
