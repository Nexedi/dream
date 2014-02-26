/* ===========================================================================
 * Copyright 2013 Nexedi SA and Contributors
 *
 * This file is part of DREAM.
 *
 * DREAM is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Lesser General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * DREAM is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with DREAM.  If not, see <http://www.gnu.org/licenses/>.
 * =========================================================================== */

/*jslint indent: 2, maxlen: 80, nomen: true */

(function (scope, $, jsPlumb, console) {
  "use strict";
  scope.Dream = function (configuration) {
    var that = jsonPlumb(),
      priv = {};

    that.initGeneralProperties = function () {
      var general_properties = {};
      $.each(configuration["Dream-Configuration"].property_list, function (
        idx, element) {
        general_properties[element.id] = element._default;
      });
      that.setGeneralProperties(general_properties);
    };

    priv.displayTool = function () {
      var render_element = $("#tools-container");
      $.each(configuration, function(key, val) {
        var name = val["name"] || key.split('-')[1];
        if (key !== 'Dream-Configuration') {
          render_element.append('<div id="' + key + '" class="tool ' + key + '">' +
            name + "<ul/></div>");
        }
      });
    };

    priv.initDialog = function () {
      $("#dialog-form").dialog({
        autoOpen: false
      });
    };

    that.prepareDialogForGeneralProperties = function () {
      var fieldset = $("#general-fieldset"),
        previous_data = that.getData()['general'],
        previous_value = "",
        prefix = "General-";
      fieldset.children().remove();
      $.each(configuration['Dream-Configuration']['property_list'],
        function (idx, property) {
          if (property._class === "Dream.Property") {
            previous_value = previous_data[property.id] || "";
            if (previous_value.length > 0 || typeof previous_value == "number") {
              previous_value = ' value="' + previous_value + '"';
            }
            fieldset.append("<label>" + (property.name || property.id) + "</label>" +
              '<input title="' +  (property.description || '') + '" type="text" name="' + prefix + property.id + '"' +
              previous_value + ' id="' + prefix + property.id + '"' +
              ' class="text ui-widget-content ui-corner-all"/>');
          }
        });
    };

    priv.prepareDialogForElement = function (title, element_id) {
      // code to allow changing values on connections. For now we assume
      // that it is throughput. But we will need more generic code
      //var throughput = $( "#throughput" ),
      //  allFields = $( [] ).add( throughput );
      $(function () {
        $("input[type=submit]")
          .button()
          .click(function (event) {
            event.preventDefault();
          });
      });

      // Render fields for that particular element
      var fieldset = $("#dialog-fieldset");
      var node_dict = that.getData()["nodes"];
      var node_id = that.getNodeId(element_id);
      $("#dialog-fieldset").children().remove();
      var element_type = node_dict[node_id]._class.replace('.', '-');
      var property_list = configuration[element_type].property_list || [];

      fieldset.append(
        '<label>ID</label><input type="text" name="id" id="id" value="' +
        node_id + '" class="text ui-widget-content ui-corner-all"/>');
      var element_name = node_dict[node_id]['name'] || node_id;
      fieldset.append(
        '<label>Name</label><input type="text" name="name" id="name" value="' +
        element_name + '" class="text ui-widget-content ui-corner-all"/>');

      var previous_data = node_dict[node_id] || {};
      var previous_value;
      var renderField = function (property_list, previous_data, prefix) {
        if (prefix === undefined) {
          prefix = "";
        }
        $.each(property_list, function (key, property) {
          if (property._class === "Dream.Property") {
            previous_value = previous_data[property.id] == undefined ? "" : previous_data[property.id];

            if (previous_value.length > 0 || typeof previous_value == "number") {
              previous_value = ' value="' + previous_value + '"';
            }
            fieldset.append("<label>" + (property.name || property.id) + "</label>" +
              '<input title="' + (property.description || '') + '" type="text" name="' + prefix + property.id + '"' +
              previous_value +
              ' id="' + prefix + property.id + '"' +
              ' class="text ui-widget-content ui-corner-all"/>');
          } else if (property._class === "Dream.PropertyList") {
            var next_prefix = prefix + property.id + "-";
            var next_previous_data = previous_data[property.id] || {};
            renderField(property.property_list, next_previous_data,
              next_prefix);
          }
        });
      };
      renderField(property_list, previous_data);

      $("#dialog-form").dialog({
        autoOpen: false,
        width: 350,
        modal: true,
        title: node_dict[node_id]._class + " " + title || "",
        buttons: {
          Cancel: function () {
            $(this).dialog("close");
          },
          Delete: function () {
            if (confirm("Are you sure you want to delete " + node_id +
              " ?")) {
              that.removeElement(node_id);
            }
            $(this).dialog("close");
          },
          Validate: function () {
            var new_id = $("#id").val();
            if (new_id !== node_id && new_id in node_dict) {
              alert('This ID is already used.');
              return;
            }
            var data = {}, prefixed_property_id, property_element;
            var updateDataPropertyList = function (property_list, data,
              prefix) {
              if (prefix === undefined) {
                prefix = "";
              }

              $.each(property_list, function (key, property) {
                if (property._class === "Dream.Property") {
                  prefixed_property_id = prefix + property.id;
                  property_element = $("#" + prefixed_property_id);
                  data[property.id] = property_element.val();
                  if (property.type === "number") {
                    data[property.id] = parseFloat(data[property.id])
                  }
                } else if (property._class === "Dream.PropertyList") {
                  var next_prefix = prefix + property.id + "-";
                  data[property.id] = {};
                  updateDataPropertyList(property.property_list, data[
                    property.id], next_prefix);
                }
              });
            };

            updateDataPropertyList(property_list, data);
            that.updateElementData(node_id, {
              data: data,
              name: $("#name").val() || node_id,
              id: $("#id").val() || node_id
            });

            $(this).dialog("close");
          }
        },
        close: function () {
          //allFields.val( "" ).removeClass( "ui-state-error" );
        }
      });
    };

    priv.super_newElement = that.newElement;
    that.newElement = function (element) {
      var element_type = element._class.replace('.', '-');
      element.element_id = that.generateElementId();
      if (!element.id) {
        element.id = that.generateNodeId(element_type, configuration[element_type]);
      }
      priv.super_newElement(element, configuration[element_type]);
      $("#" + element.element_id).on('dblclick', function () {
        $("#dialog-form").dialog("destroy");
        priv.prepareDialogForElement(element.id, element.element_id);
        $("#dialog-form").dialog("open");
      });
      // Store default values
      var data = {}, property_list = configuration[element_type][
          "property_list"
        ] || [];
      var updateDefaultData = function (data, property_list) {
        $.each(property_list, function (idx, value) {
          if (value) {
            if (element[value.id]) {
              data[value.id] = element[value.id];
            } else if (value._class === "Dream.Property") {
              data[value.id] = value._default;
            } else if (value._class === "Dream.PropertyList") {
              data[value.id] = {};
              var next_data = data[value.id];
              var next_property_list = value.property_list || [];
              updateDefaultData(next_data, next_property_list);
            }
          }
        });
      };
      updateDefaultData(data, property_list);
      that.updateElementData(element.id, {
        data: data
      });
    };

    priv.super_start = that.start;
    that.start = function () {
      priv.super_start();
      priv.displayTool();
      priv.initDialog();
      that.initGeneralProperties();
      that.prepareDialogForGeneralProperties();
    };

    /** Runs the simulation, and call the callback with results once the
     * simulation is finished.
     */
    that.runSimulation = function (callback) {
      // handle Dream.General properties (in another function maybe ?)
      var prefix = "General-",
        properties = {}, prefixed_property_id;

      $.each(configuration['Dream-Configuration']['property_list'],
        function (idx, property) {
          if (property._class === "Dream.Property") {
            prefixed_property_id = prefix + property.id;
            properties[property.id] = $("#" + prefixed_property_id).val();
            if (property.type === "number") {
              properties[property.id] = parseFloat(properties[property.id])
            }
          }
        });
      that.setGeneralProperties(properties);

      $.ajax(
        '/runSimulation', {
          data: JSON.stringify({
            json: that.getData()
          }),
          contentType: 'application/json',
          type: 'POST',
          success: function (data, textStatus, jqXHR) {
            callback(data);
          }
        });
    };

    that.displayResult = function (idx) {
      $('li.result').removeClass('active');
      $($('li.result')[idx]).addClass('active');
      var result = JSON.parse($("#json_result").val())[idx]['result'];
      if (configuration['Dream-Configuration'].gui.debug_json){
        $("#debug_json").show();
      }
      if (configuration['Dream-Configuration'].gui.station_utilisation_graph){
        $("#graph_zone").show();
      }
      if (configuration['Dream-Configuration'].gui.job_schedule_spreadsheet){
        $("#job_schedule_spreadsheet").show();
      }
      if (configuration['Dream-Configuration'].gui.job_gantt){
        $("#job_gantt").show();
      }

      // temporary hack
      var now = new Date();
      now.setHours(0);
      now.setMinutes(0);
      now.setSeconds(0);

      var blockage_data = [],
        waiting_data = [],
        failure_data = [],
        working_data = [],
        ticks = [],
        counter = 1,
        spreadsheet_data = [],
        spreadsheet_header = [
          [
            "Jobs",
            "ID",
            "Due Date",
            "Priority",
            "Entrance Time",
            "Processing Time",
            "Station ID",
            "Step No."
          ]
        ],
        start_date = new Date(now.getTime()),
        gantt_data = {
          data: [
          {
            id: "by_job",
            text: "By Job",
            start_date: start_date,
            duration: 0,
            project: 1,
            open: true
          },
          {
            id: "by_station",
            text: "By Station",
            start_date: start_date,
            duration: 0,
            project: 1,
            open: true
          }
          ],
          link: []
        };

      $.each(result.elementList.sort(function(a,b) {return a.id < b.id ? -1 : 1}),
        function (idx, obj) {
        if (obj.results !== undefined && obj.results.working_ratio !== undefined) {
          /* when there is only one replication, the ratio is given as a float,
              otherwise we have a mapping avg, min max */
          var blockage_ratio = 0.0;
          if (obj.results.blockage_ratio !== undefined) {
            if (obj.results.blockage_ratio.avg !== undefined) {
              blockage_ratio = obj.results.blockage_ratio.avg;
            } else {
              blockage_ratio = obj.results.blockage_ratio;
            }
          }
          blockage_data.push([counter, blockage_ratio]);

          var working_ratio = 0.0;
          if (obj.results.working_ratio !== undefined) {
            if (obj.results.working_ratio.avg !== undefined) {
              working_ratio = obj.results.working_ratio.avg;
            } else {
              working_ratio = obj.results.working_ratio;
            }
          }
          working_data.push([counter, working_ratio]);

          var waiting_ratio = 0.0;
          if (obj.results.waiting_ratio !== undefined) {
            if (obj.results.waiting_ratio.avg !== undefined) {
              waiting_ratio = obj.results.waiting_ratio.avg;
            } else {
              waiting_ratio = obj.results.waiting_ratio;
            }
          }
          waiting_data.push([counter, waiting_ratio]);

          var failure_ratio = 0.0;
          if (obj.results.failure_ratio !== undefined) {
            if (obj.results.failure_ratio.avg !== undefined) {
              failure_ratio = obj.results.failure_ratio.avg;
            } else {
              failure_ratio = obj.results.failure_ratio;
            }
          }
          failure_data.push([counter, failure_ratio]);

          ticks.push([counter, obj.id]);
          counter++;
        }

        var isVisibleStation = function (station) {
          // we should be able to define in the backend which station is visible
          return  ["CAM", "CAD", "MILL", "EDM", "MASS", "IM"].indexOf(
            station.substring(0, station.length - 1)) !== -1;
        };

        if (obj._class === 'Dream.Job') {
          // find the corresponding input
          var data = that.getData(),
              input_job, input_order;
          var job_index = parseInt(obj["id"]);
          input_job = data.wip_part_spreadsheet[job_index];
          var i = job_index;
          while (data.wip_part_spreadsheet[i][0] === null || data.wip_part_spreadsheet[i][0] === "") {
            i = i-1;
          }
          input_order = data.wip_part_spreadsheet[i];

          var duration = 0;
          if (input_job == input_order) { // if we are on the order definition
            gantt_data.data.push({
              id: input_order[0],
              text: input_order[0],
              project: 1,
              open: false,
              parent: "by_job"
            });
          }

          $.each(obj['results']['schedule'], function (i, schedule) {
            // Filter intermediate steps in part job shop
            if (isVisibleStation(schedule['stationId'])) {
              var entrance_date = new Date(start_date.getTime());
              entrance_date.setTime(entrance_date.getTime() + schedule['entranceTime']*1000*3600);
              spreadsheet_data.push([
                input_order[0] + "-" + input_job[4],
                obj['id'],
                input_order[1], // dueDate
                input_order[2], // priority
                moment(entrance_date).format("MMM/DD HH:mm"),
                input_job[7].split('-')[schedule['stepNumber']] || 0, // processing time
                schedule['stationId'],
                schedule['stepNumber']
              ]);
              if (obj['results']['schedule'][i + 1]) {
                duration = obj['results']['schedule'][i + 1]['entranceTime'] - schedule['entranceTime'];
              } else {
                duration = obj['results'].completionTime - schedule['entranceTime'];
              }
              if (duration > 0.0) {
                var task_start_date = new Date(start_date.getTime());
                // for simulation time unit as days
                // task_start_date.setDate(task_start_date.getDate() + schedule['entranceTime']);
                // for simulation time unit as days hours
                task_start_date.setTime(task_start_date.getTime() + schedule['entranceTime']*1000*3600);
                gantt_data.data.push({
                  id: input_order[0] + '.' + idx + '_' + i,
                  text: schedule['stationId'],
                  start_date: task_start_date,
                  duration: duration,
                  parent: input_order[0]
                });
                gantt_data.data.push({
                  id: 'job.' + obj['id'] + '.' + idx + '_' + i,
                  text: input_order[0] + "-" + input_job[4],
                  start_date: task_start_date,
                  duration: duration,
                  parent: schedule['stationId'],
                  by_station:1
                });
              }
            }
          });
        } else {
          if (isVisibleStation(obj['id'])) {
            gantt_data.data.push({
              id: obj['id'],
              text: obj['id'],
              project: 1,
              open: false,
              parent: "by_station"
            });
          };
        }
      });

      var series = [{
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

      var options = {
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
      if (configuration['Dream-Configuration'].gui.station_utilisation_graph){
        // XXX no need to prepare data
        $.plot("#graph", series, options);
      }

      if (configuration['Dream-Configuration'].gui.exit_stat){
        var exit_stat = $("#exit_stat").show().text("Exit Metrics");
        $.each(result.elementList, function(idx, el){
          if (el._class == 'Dream.Exit'){
            var text = exit_stat.html() + "<table><tr><th colspan='2'>" + (
                    el.name || el.id) + "</th></tr>";
            $.each(el.results, function(metric, value){
              if (metric == 'intervalThroughputList') {
                var attainment_list = [],
                    general = that.getData().general,
                    throughputTarget = parseFloat(general.throughputTarget),
                    desiredPercentageOfSuccess = parseFloat(general.desiredPercentageOfSuccess);
                  text += "<tr><td>Daily Attainment</td><td>"
                  $.each(value, function(i, intervalValue) {
                    var icon = "fa-frown-o";
                    attainment_list.push((intervalValue/throughputTarget));
                    if ((intervalValue/throughputTarget) > desiredPercentageOfSuccess) {
                      icon = "fa-smile-o"
                    }
                    text += intervalValue + ' <i class="fa ' + icon + '"/><br/>';
                  })
                  text += "</td></tr>";

                  text += "<tr><td>Average Daily Line Attainment</td><td>" + (
                    (attainment_list.reduce(function(a, b){return a+b}) / attainment_list.length ) * 100).toFixed(2) + "%</td></tr>";
              } else {
                if (typeof value == "number") {
                   value = value.toFixed(2)
                }
                text += "<tr><td>" + metric + "</td><td>" + value + "</td></tr>";
              }
            })
            exit_stat.html(text + "</table>");
          }
        })
      }

      if (spreadsheet_data.length > 1) {
        var job_schedule_spreadsheet = $('#job_schedule_spreadsheet');
        // Sort the spreadsheet data to an order convenient for end users
        spreadsheet_data.sort( function(a, b) {
          var result = 0,
              order_id_a, order_id_b, entrance_a, entrance_b;
          order_id_a = a[0].split('-')[0];
          order_id_b = b[0].split('-')[0];
          if (order_id_a !== order_id_b) {
            if (order_id_a > order_id_b) {
              result = 1;
            } else {
              result = -1;
            }
          } else {
            entrance_a = a[6];
            entrance_b = b[6];
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
        if (configuration['Dream-Configuration'].gui.job_schedule_spreadsheet){
          job_schedule_spreadsheet.show();
          job_schedule_spreadsheet.handsontable({
            data: spreadsheet_header.concat(spreadsheet_data),
            readOnly: true
          });
          job_schedule_spreadsheet.find('.htCore').width(job_schedule_spreadsheet.width());
        }
        gantt.templates.task_class = function (start, end, obj) {
          return obj.parent ? "sub_task" : "";
        };
        try {
          gantt.clearAll();
        } catch (e) {}

        var gantt_output_height = 35 * (gantt_data.data.length + 1) + 1;
        gantt_data.data.sort(function (a, b) {
          // sort gantt data in a chronological order
          var result;
          if (a.start_date === undefined && b.start_date !== undefined) {
            result = 1;
          } else if (a.start_date !== undefined && b.start_date === undefined) {
            result = - 1;
          } else if (a.start_date === undefined && b.start_date === undefined) {
            result = 0;
          } else if (a.start_date > b.start_date) {
            result = 1;
          } else if (a.start_date < b.start_date) {
            result = -1;
          } else {
            result = 0;
          }
          return result;
        });
        if (configuration['Dream-Configuration'].gui.job_gantt){
          $('#job_gantt').show().dhx_gantt({
            data: gantt_data,
            readonly: true,
            /* for days has simulation time unit
            scale_unit: 'day',
            step: 7
            */
            // for hours has simulation time unit
            scale_unit: 'day',
            duration_unit: 60*60*1000,
            //date_grid: "%H:%i",
            date_scale: "%M/%d",
            step: 1,
            subscales: [{unit:"hour", step:4, date:"%H:%i" }]
          });
          //$('#gantt_grid').width(1000);
        }
      }
    };
    return that;
  };

}(window, jQuery, jsPlumb, console));
