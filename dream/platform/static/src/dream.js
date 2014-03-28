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

  function station_utilisation_graph_widget(input_data, output_data) {
    var blockage_data = [],
      waiting_data = [],
      failure_data = [],
      working_data = [],
      ticks = [],
      counter = 1;

    // XXX output is still elementList ???
    $.each(output_data.elementList.sort(
            function(a,b) {return a.id < b.id ? -1 : 1}),
      function (idx, obj) {
        // add each object that has a working ratio
      if (obj.results !== undefined && obj.results.working_ratio !== undefined) {
        /* when there is only one replication, the ratio is given as a float,
            otherwise we have a mapping avg, ub lb */
        var blockage_ratio = 0.0;
        if (obj.results.blockage_ratio !== undefined) {
          if (obj.results.blockage_ratio.avg !== undefined) {
            blockage_ratio = obj.results.blockage_ratio.avg;
          } else {
            blockage_ratio = obj.results.blockage_ratio;
          }
        }
        blockage_data.push([counter, blockage_ratio]);

        // XXX merge setup & loading ratio in working ratio for now
        var working_ratio = 0.0;
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
    $.plot("#graph", series, options);
  };

  function queue_stat_widget(input_data, output_data) {
    /* FIXME: does not support more than one replic.
     * + see george email to integrate without the need of an EG
     */
    var queue_stat = $("#queue_stat");
    var series = [];
    $.each(output_data.elementList, function(idx, el){
      if (el._class == 'Dream.Queue'){
        series.push({label: el.name || el.id,
                     data: el.wip_stat_list})
      }
    })
    $.plot("#queue_stat_graph", series);
  }

  function exit_stat_widget(input_data, output_data) {
    var exit_stat = $("#exit_stat").find('div').empty();
    $.each(output_data.elementList, function(idx, el){
      if (el._class == 'Dream.Exit'){
        var text = exit_stat.html() + "<table><tr><th colspan='2'>" + (
                el.name || el.id) + "</th></tr>";
        $.each(el.results, function(metric, value){
          if (metric == 'intervalThroughputList') {
            var attainment_list = [],
                general = that.getData().general,
                throughputTarget = parseFloat(general.throughputTarget);
              text += "<tr><td>Daily Attainment</td><td>"
              $.each(value, function(i, intervalValue) {
                var icon = "fa-frown-o";
                attainment_list.push((intervalValue/throughputTarget));
                if (intervalValue > throughputTarget) {
                  icon = "fa-smile-o"
                }
                text += intervalValue + ' <i class="fa ' + icon + '"/><br/>';
              })
              text += "</td></tr>";

              text += "<tr><td>Average Daily Line Attainment</td><td>" + (
                (attainment_list.reduce(function(a, b){return a+b}) / attainment_list.length ) * 100).toFixed(2) + "%</td></tr>";
          } else {
            if (typeof value == "object") {
               if (value.ub == value.lb) {
                  value = value.ub;
               } else {
                 var ci_text = "<table width='100%'><tbody>"
                 ci_text += "<tr><td>Average</td><td>" + value.avg.toFixed(2) + "</td></tr>"
                 ci_text += "<tr><td>Lower Bound</td><td>" + value.lb.toFixed(2) + "</td></tr>"
                 ci_text += "<tr><td>Upper Bound</td><td>" + value.ub.toFixed(2) + "</td></tr>"
                 ci_text += "</tbody></table>"
                 value = ci_text;
               }
            }
            if (typeof value == "number") {
               value = value.toFixed(2)
            }
            // Rename some metric to something more meaningful
            if (metric == "lifespan" ){
              metric = "Cycle Time"
            }
            if (metric == "takt_time" ){
              metric = "Average Departure Rate"
            }
            text += "<tr><td>" + metric + "</td><td>" + value + "</td></tr>";
          }
        })
        exit_stat.html(text + "</table>");
      }
    })
  }
  
  function job_schedule_spreadsheet_widget(input_data, output_data) {
    var now = new Date();
    // XXX why ?
    now.setHours(0);
    now.setMinutes(0);
    now.setSeconds(0);

    var spreadsheet_data = [],
      spreadsheet_header = [
        [
          "Jobs",
          "ID",
          "Project Manager",
          "Due Date",
          "Priority",
          "Entrance Time",
          "Processing Time",
          "Station ID",
          "Step No."
        ]
      ],
      simulation_start_date = new Date(input_data.general.currentDate || now.getTime());
      // TODO: time unit for later 
      //       or an utility function to map sim time to real time & vice
      //       versa.

      $.each(output_data.elementList, function(idx, obj) {
        if (obj._class === 'Dream.Job') {
          var input_job, input_order, job_index = parseInt(obj["id"]);

          // TODO: do not read spreadsheet, use input JSON to get data
          // ... afterall why ?
          
          input_job = input_data.wip_part_spreadsheet[job_index];
          // If this line is an order component, find the order.
          var i = job_index;
          while (input_data.wip_part_spreadsheet[i][0] === null ||
                 input_data.wip_part_spreadsheet[i][0] === "") {
            i = i-1;
          }
          input_order = input_data.wip_part_spreadsheet[i];
          $.each(obj['results']['schedule'], function (i, schedule) {
            var entrance_date = new Date(simulation_start_date.getTime() +
                                          // TODO: time unit
                                         schedule['entranceTime'] * 1000 * 3600);

            spreadsheet_data.push([
              input_order[0] + "-" + input_job[4],
              obj['id'],
              input_order[3], // operator
              input_order[1], // dueDate
              input_order[2], // priority
              moment(entrance_date).format("MMM/DD HH:mm"),
              input_job[7].split('-')[i] || 0, // processing time
              schedule['stationId'],
              i
            ]);
          });
        }
      });

      if (spreadsheet_data.length > 1) {
        var job_schedule_spreadsheet = $('#job_schedule_spreadsheet');
        // Sort the spreadsheet data to an order convenient for end users
        // TODO: search for a default cmp in javascript
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

      job_schedule_spreadsheet.show();
      job_schedule_spreadsheet.handsontable({
        data: spreadsheet_header.concat(spreadsheet_data),
        width: function () {
            return $(window).width() -
                  job_schedule_spreadsheet.offset().left +
                  $(window).scrollLeft();
        },
        readOnly: true
      });
      job_schedule_spreadsheet.find('.htCore').width(job_schedule_spreadsheet.width());
    }
  }

  function job_gantt_widget(input_data, output_data) {

      // temporary hack
      var now = new Date();
      now.setHours(0);
      now.setMinutes(0);
      now.setSeconds(0);

      var start_date,
        gantt_data = {
          data: [
          {
            id: "by_order",
            text: "By Order",
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

      start_date = input_data.general.currentDate;
      if (start_date !== undefined && start_date !== "") {
        start_date = new Date(start_date);
      } else {
        start_date =  new Date(now.getTime())
      }

      $.each(output_data.elementList.sort(function(a,b) {return a.id < b.id ? -1 : 1}),
        function (idx, obj) {

        var isVisibleStation = function (station) {
          // we should be able to define in the backend which station is visible
          return input_data.nodes[station]._class != "Dream.QueueManagedJob";
        };

        if (obj._class === 'Dream.Job') {
          // find the corresponding input
          var input_job, input_order;
          var job_index = parseInt(obj["id"]);
          // TODO: do not read spreadsheet, use input JSON to get data
          input_job = input_data.wip_part_spreadsheet[job_index];
          var i = job_index;
          while (input_data.wip_part_spreadsheet[i][0] === null ||
                 input_data.wip_part_spreadsheet[i][0] === "") {
            i = i-1;
          }
          input_order = input_data.wip_part_spreadsheet[i];

          var duration = 0;
          if (input_job == input_order) { // if we are on the order definition
            gantt_data.data.push({
              id: input_order[0],
              text: input_order[0],
              project: 1,
              open: false,
              parent: "by_order"
            });
          }

          var seen_parts = {};
          $.each(obj['results']['schedule'], function (i, schedule) {
            // Filter intermediate steps in part job shop
            if (isVisibleStation(schedule['stationId'])) {
              var entrance_date = new Date(start_date.getTime());
              entrance_date.setTime(entrance_date.getTime() + schedule['entranceTime']*1000*3600);
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
                if (seen_parts[input_job[4] + "." + input_order[0]] === undefined){
                  gantt_data.data.push({
                    id: input_job[4] + "." + input_order[0],
                    text: input_job[4],
                    parent: input_order[0]
                  });
                  seen_parts[input_job[4] + "." + input_order[0]] = 1;
                }
                gantt_data.data.push({
                  id: input_order[0] + '.' + idx + '_' + i,
                  text: schedule['stationId'],
                  start_date: task_start_date,
                  duration: duration,
                  parent: input_job[4] + "." + input_order[0]
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
  }


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
            if (!property.non_editable){
              fieldset.append($("<label>").text(property.name || property.id));
              var input =  $("<input type='text'>")
              if (property.choice) {
                input = $("<select/>");
                input.append("<option/>");
                $.each(property.choice, function(idx, option) {
                  input.append($("<option/>").val(option[1]).text(option[0]));
                });
                
              }
              input.attr({
                'name':  prefix + property.id,
                'title': (property.description || ''),
                'id': prefix + property.id,
                'class': 'text ui-widget-content ui-corner-all',
              })

              previous_value = previous_data[property.id];
              input.val(previous_value);

              fieldset.append(input);
            }
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
                  if (property.type === "number" && data[property.id] !== "") {
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
      var update_dict = {data: data}
      if (element.name) {
        update_dict["name"] = element.name;
      }
      that.updateElementData(element.id, update_dict);
    };

    priv.super_start = that.start;
    that.start = function () {
      priv.super_start();
      priv.displayTool();
      priv.initDialog();
      that.initGeneralProperties();
      that.prepareDialogForGeneralProperties();
    };

    that.readGeneralPropertiesDialog = function () {
      // handle Dream.General properties
      var prefix = "General-",
        properties = {}, prefixed_property_id;

      $.each(configuration['Dream-Configuration']['property_list'],
        function (idx, property) {
          if (property._class === "Dream.Property") {
            prefixed_property_id = prefix + property.id;
            properties[property.id] = $("#" + prefixed_property_id).val();
            if (property.type === "number" && properties[property.id] !== "") {
              properties[property.id] = parseFloat(properties[property.id])
            }
          }
        });
      that.setGeneralProperties(properties);
    }

    /** Runs the simulation, and call the callback with results once the
     * simulation is finished.
     */
    that.runSimulation = function (callback) {
      that.readGeneralPropertiesDialog()
      $.ajax(
          '../runSimulation', {
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

    /** Runs the knowledge extraction, and call the callback with results once the
     * KE is finished.
     */
    that.runKnowledgeExtraction = function (callback) {
      that.readGeneralPropertiesDialog()
      $.ajax(
          '../runKnowledgeExtraction', {
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
      var active_tab = $("#reports").data("ui-tabs") ?
        $("#reports").tabs("option", "active") : 0; // XXX should not be 0, but the first enabled one
      var result = JSON.parse($("#json_result").val())[idx]['result'];

      $('li.result').removeClass('active');
      $($('li.result')[idx]).addClass('active');
      if ($("#reports").data("ui-tabs")) {
        $("#reports").tabs("destroy"); 
      }

      var available_widget_list = [
        'debug_json',
        'station_utilisation_graph',
        'job_schedule_spreadsheet',
        'job_gantt',
        'exit_stat',
        'queue_stat',
      ];

      for (var i in available_widget_list) {
        var widget_name = available_widget_list[i];
        if (configuration['Dream-Configuration'].gui[widget_name]) {
          $("li > a[href='#" + widget_name  + "']").parent().show();
        } else {
          $("li > a[href='#" + widget_name  + "']").parent().hide();
        }
      }

      var input = that.getData(); // XXX how to get input json ?

      // display each of the enabled widget
      if (configuration['Dream-Configuration'].gui.station_utilisation_graph){
        station_utilisation_graph_widget(input, result);
      }
      if (configuration['Dream-Configuration'].gui.queue_stat){
        queue_stat_widget(input, result);
      }
      if (configuration['Dream-Configuration'].gui.exit_stat){
        exit_stat_widget(input, result);
      }
      if (configuration['Dream-Configuration'].gui.job_schedule_spreadsheet){
        job_schedule_spreadsheet_widget(input, result);
      }
      if (configuration['Dream-Configuration'].gui.job_gantt){
        job_gantt_widget(input, result);
      }

      // hack: make the tabs full width
      $("#reports li").width((100/$("#reports li:visible").length) - 1 +'%');
      $("#reports li a").width('100%').css({'text-align': 'left'});

      $("#reports").show().tabs({ active: active_tab });
    }

    return that;
  };
}(window, jQuery, jsPlumb, console));


