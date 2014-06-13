/*global console, rJS, RSVP, initDocumentPageMixin, moment, initGadgetMixin */
/*jslint nomen: true */
(function (window, rJS, RSVP, initDocumentPageMixin, moment, initGadgetMixin) {
  "use strict";

  function job_schedule_spreadsheet_widget(all_data) {
    var now = new Date(),
      input_data = all_data.input,
      output_data = all_data.result,
      spreadsheet_data = [],
      spreadsheet_header = [[
        "Jobs",
        "ID",
        "Project Manager",
        "Due Date",
        "Priority",
        "Entrance Time",
        "Processing Time",
        "Station ID",
        "Step No."
      ]],
      simulation_start_date = new Date(
        input_data.general.currentDate || now.getTime()
      ),
      i,
      j,
      k,
      obj,
      node,
      component,
      order,
      node_id,
      due_date,
      entrance_date,
      duration,
      schedule,
      input_job = null,
      input_order = null;

    // XXX why ?
    now.setHours(0);
    now.setMinutes(0);
    now.setSeconds(0);

    // XXX: time unit for later
    //      or an utility function to map sim time to real time & vice
    //      versa.

    for (i = 0; i < output_data.elementList.length; i += 1) {
      obj = output_data.elementList[i];

      if (obj._class === 'Dream.Job') {
        input_job = null;
        input_order = null;

        // find the input order and order component for this job
        for (node_id in input_data.nodes) {
          if (input_data.nodes.hasOwnProperty(node_id)) {
            node = input_data.nodes[node_id];
            if (node.wip) {
              for (j = 0; j < node.wip.length; j += 1) {
                order = node.wip[j];
                if (order.id === obj.id) {
                  input_job = input_order = order;
                }
                if (input_job === null) {
                  for (k = 0; k < order.componentsList.length; k += 1) {
                    component = order.componentsList[k];
                    if (component.id === obj.id) {
                      input_order = order;
                      input_job = component;
                    }
                  }
                }
              }
            }
          }
        }

        due_date = new Date(simulation_start_date.getTime() +
                            input_order.dueDate * 1000 * 3600);
        for (j = 0; j < obj.results.schedule.length; j += 1) {
          schedule = obj.results.schedule[j];
          entrance_date = new Date(simulation_start_date.getTime() +
                                    // XXX: time unit
                                   schedule.entranceTime * 1000 * 3600);
          duration = 0;
          // Duration is calculated by difference of entranceTime of this
          // step and entranceTime of the next step, or completionTime when
          // this is the last step
          if (j + 1 === obj.results.schedule.length) {
            duration = obj.results.completionTime - schedule.entranceTime;
          } else {
            duration = obj.results.schedule[j + 1].entranceTime -
                       schedule.entranceTime;
          }

          spreadsheet_data.push([
            // XXX this label is incorrect for design step, during design
            // phase we still have an order and not an order component.
            input_order.name + "-" + input_job.name,
            obj.id,
            input_order.manager,
            moment(due_date).format("YYYY/MM/DD"),
            input_order.priority,
            moment(entrance_date).format("MMM/DD HH:mm"),
            duration,
            schedule.stationId,
            j
          ]);
        }
      }
    }

    if (spreadsheet_data.length > 1) {
      // Sort the spreadsheet data to an order convenient for end users
      // XXX: search for a default cmp in javascript
      spreadsheet_data.sort(function (a, b) {
        var result = 0,
          order_id_a,
          order_id_b,
          entrance_a,
          entrance_b;

        order_id_a = a[0].split('-')[0];
        order_id_b = b[0].split('-')[0];
        if (order_id_a !== order_id_b) {
          if (order_id_a > order_id_b) {
            result = 1;
          } else {
            result = -1;
          }
        } else {
          entrance_a = a[4];
          entrance_b = b[4];
          if (entrance_a > entrance_b) {
            result = 1;
          } else if (entrance_a < entrance_b) {
            result = -1;
          } else {
            result = 0;
          }
        }
        return result;
      });
    }

    return spreadsheet_header.concat(spreadsheet_data);
  }

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
      var jio_key = options.id,
        gadget = this;
      gadget.props.jio_key = jio_key;

      return new RSVP.Queue()
        .push(function () {
          return RSVP.all([
            gadget.aq_getAttachment({
              "_id": jio_key,
              "_attachment": "simulation.json"
            }),
            gadget.getDeclaredGadget("tableeditor")
          ]);
        })
        .push(function (result_list) {
          return result_list[1].render(
            JSON.stringify(
              job_schedule_spreadsheet_widget(
                // XXX Hardcoded result
                JSON.parse(result_list[0])[0]
              )
            )
          );
//       job_schedule_spreadsheet.show();
//       job_schedule_spreadsheet.handsontable({
//         data: spreadsheet_header.concat(spreadsheet_data),
//         width: function () {
//             return $(window).width() -
//                   job_schedule_spreadsheet.offset().left +
//                   $(window).scrollLeft();
//         },
//         readOnly: true
//       });
//       job_schedule_spreadsheet.find('.htCore')
//         .width(job_schedule_spreadsheet.width());
        });
    })

    .declareMethod("startService", function () {
      return this.getDeclaredGadget("tableeditor")
        .push(function (tableeditor) {
          return tableeditor.startService();
        });
    });
}(window, rJS, RSVP, initDocumentPageMixin, moment, initGadgetMixin));
