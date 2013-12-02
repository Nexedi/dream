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

(function ($) {
  "use strict";
  jsPlumb.bind("ready", function () {
    var dream_instance, jio;
    jio = new jIO.newJio({
      type: "local",
      username: "dream",
      applicationname: "dream"
    });

    var property_container = {
      entity: {
        id: "entity",
        type: "string",
        _class: "Dream.Property",
        _default: "Part"
      },
      // XXX is it possible not to repeat id ?
      mean: {
        id: "mean",
        type: "string",
        _class: "Dream.Property",
        _default: "0.9"
      },
      distributionType: {
        id: "distributionType",
        type: "string",
        _class: "Dream.Property",
        _default: "Fixed"
      },
      stdev: {
        id: "stdev",
        type: "string",
        _class: "Dream.Property",
        _default: "0.1"
      },
      min: {
        id: "min",
        type: "string",
        _class: "Dream.Property",
        _default: "0.1"
      },
      max: {
        id: "max",
        type: "string",
        _class: "Dream.Property",
        _default: "1"
      },
      failureDistribution: {
        id: "failureDistribution",
        type: "string",
        _class: "Dream.Property",
        _default: "No"
      },
      MTTF: {
        id: "MTTF",
        type: "string",
        _class: "Dream.Property",
        _default: "40"
      },
      MTTR: {
        id: "MTTR",
        type: "string",
        _class: "Dream.Property",
        _default: "10"
      },
      repairman: {
        id: "repairman",
        type: "string",
        _class: "Dream.Property",
        _default: "None"
      },
      isDummy: {
        id: "isDummy",
        type: "string",
        _class: "Dream.Property",
        _default: "0"
      },
      capacity: {
        id: "capacity",
        type: "string",
        _class: "Dream.Property",
        _default: "1"
      },
      simulationClass: {
        id: "simulationClass",
        type: "string",
        _class: "Dream.Property",
        _default: "Default"
      },
      numberOfReplications: {
        id: "numberOfReplications",
        type: "string",
        _class: "Dream.Property",
        _default: "10"
      },
      maxSimTime: {
        id: "maxSimTime",
        type: "string",
        _class: "Dream.Property",
        _default: "100"
      },
      confidenceLevel: {
        id: "confidenceLevel",
        type: "string",
        _class: "Dream.Property",
        _default: "0.5"
      },
      processTimeout: {
        id: "processTimeout",
        type: "string",
        _class: "Dream.Property",
        _default: "0.5"
      }
    };
    property_container["interarrivalTime"] = {
      id: "interarrivalTime",
      property_list: [property_container["mean"], property_container[
        "distributionType"]],
      _class: "Dream.PropertyList"
    };
    property_container["processingTime"] = {
      id: "processingTime",
      property_list: [property_container["mean"], property_container[
          "distributionType"],
        property_container["stdev"], property_container["min"],
        property_container["max"]
      ],
      _class: "Dream.PropertyList"
    };
    property_container["failures"] = {
      id: "failures",
      property_list: [property_container["failureDistribution"],
        property_container["MTTF"],
        property_container["MTTR"], property_container["repairman"]
      ],
      _class: "Dream.PropertyList"
    };

    var configuration = {
      "Dream-Source": {
        property_list: [property_container["interarrivalTime"],
          property_container["entity"]
        ],
        _class: 'Dream.Source'
      },
      "Dream-Machine": {
        property_list: [property_container["processingTime"],
          property_container["failures"]
        ],
        _class: 'Dream.Machine'
      },
      "Dream-Queue": {
        property_list: [property_container["capacity"], property_container[
          "isDummy"]],
        _class: 'Dream.Queue'
      },
      "Dream-Exit": {
        _class: 'Dream.Exit'
      },
      "Dream-MachineJobShop": {
        property_list: [property_container["processingTime"],
          property_container["failures"]
        ],
        _class: 'Dream.MachineJobShop'
      },
      "Dream-QueueJobShop": {
        property_list: [property_container["capacity"], property_container[
          "isDummy"]],
        _class: 'Dream.QueueJobShop'
      },
      "Dream-ExitJobShop": {
        _class: 'Dream.ExitJobShop'
      },
      "Dream-Repairman": {
        property_list: [property_container["capacity"]],
        _class: 'Dream.Repairman'
      },
      "Dream-Configuration": {
        property_list: [
          property_container["simulationClass"],
          property_container["numberOfReplications"],
          property_container["maxSimTime"],
          property_container["confidenceLevel"],
          property_container["processTimeout"]
        ],
        _class: 'Dream.Repairman'
      }
    };

    dream_instance = Dream(configuration);
    dream_instance.start();
    $(".tool").draggable({
      containment: '#main',
      opacity: 0.7,
      helper: "clone",
      cursorAt: {
        top: 0,
        left: 0
      },
      stop: function (tool) {
        var box_top, box_left, _class;
        var offset = $("#main").offset();
        box_top = tool.clientY - offset.top + "px";
        box_left = tool.clientX - offset.left + "px";
        var relative_position = dream_instance.convertToRelativePosition(
          box_left, box_top);
        _class = tool.target.id.replace('-', '.'); // XXX - vs .
        dream_instance.newElement({
          coordinate: {
            top: relative_position[1],
            left: relative_position[0]
          },
          _class: _class
        });
      }
    });

    var loadData = function (data) {
      // spreadsheet
      var spreadsheet_data = data.spreadsheet;
      if (spreadsheet_data !== undefined) {
        var spreadsheet = $('#spreadsheet_input');
        spreadsheet.handsontable('populateFromArray', 0, 0, spreadsheet_data);
      }

      var preference = data.preference !== undefined ?
        data.preference : {};
      dream_instance.setPreferences(preference);

      // Add all elements
      var coordinates = preference['coordinates'];
      $.each(data.nodes, function (key, value) {
        if (coordinates === undefined || coordinates[key] === undefined) {
          value['coordinate'] = {
            'top': 0.0,
            'left': 0.0
          };
        } else {
          value['coordinate'] = coordinates[key];
        }
        value['id'] = key;
        dream_instance.newElement(value);
        dream_instance.updateElementData(key, {
          data: value.data || {}
        });
      });
      $.each(data.edges, function (key, value) {
        dream_instance.connect(value[0], value[1]);
      });

      dream_instance.setGeneralProperties(data.general);
      dream_instance.initGeneralProperties(); // XXX
      $("#json_output").val(JSON.stringify(dream_instance.getData(),
        undefined, " "));
      if ($.isEmptyObject(coordinates)) {
        dream_instance.positionGraph();
      } else {
        dream_instance.redraw();
      }
    };
    // Check if there is already data when we first load the page, if yes, then build graph from it
    jio.get({
      _id: "dream_demo"
    }, function (err, response) {
      if (response !== undefined && response.data !== undefined) {
        loadData(response.data);
      }
      // once the data is read, we can subscribe to every changes
      $.subscribe("Dream.Gui.onDataChange", function (event, data) {
        $("#json_output").val(JSON.stringify(data, undefined, " "));
        jio.put({
          _id: "dream_demo",
          data: data
        }, function (err, response) {});
      });
    });



    // Enable "Run Simulation" button
    $("#run_simulation").button().click(
      function (e) {
        dream_instance.runSimulation(
          function (data) {
            if (data['success']) {
              $("#json_result").val(JSON.stringify(data['success'],
                undefined, " "));

              // display demo graph.
              $("#graph_zone").show();
              var blockage_data = [],
                waiting_data = [],
                failure_data = [],
                working_data = [],
                ticks = [],
                counter = 1;
              $.each(data['success'].elementList, function (idx, obj) {
                if (obj.results.working_ratio !== undefined) {
                  /* when there is only one replication, the ratio is given as a float,
                      otherwise we have a mapping avg, min max */
                  if (obj.results.blockage_ratio !== undefined) {
                    blockage_data.push([counter, obj.results.blockage_ratio
                      .avg || obj.results.blockage_ratio
                    ]);
                  } else {
                    blockage_data.push([counter, 0.0]);
                  }
                  waiting_data.push([counter, obj.results.waiting_ratio.avg ||
                    obj.results.waiting_ratio
                  ]);
                  if (obj.results.failure_ratio !== undefined) {
                    failure_data.push([counter, obj.results.failure_ratio
                      .avg || obj.results.failure_ratio
                    ]);
                  } else {
                    failure_data.push([counter, 0.0]);
                  }
                  working_data.push([counter, obj.results.working_ratio.avg ||
                    obj.results.working_ratio
                  ]);
                  ticks.push([counter, dream_instance.getData().nodes[
                    obj.id].name || obj.id]);
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
                    barWidth: 0.9,
                    align: "center"
                  },
                  stack: true
                }
              };
              $.plot("#graph", series, options);

            } else {
              $("#json_result").effect('shake', 50).val(data['error']);
            }
          });
        e.preventDefault();
        return false;
      });

    // Enable "Layout Graph" button
    $("#layout_graph").button().click(
      function (e) {
        dream_instance.positionGraph();
      });

    // Enable "Clear All" button
    $("#clear_all").button().click(
      function (e) {
        dream_instance.clearAll();
        e.preventDefault();
        return false;
      });

    // Enable "Zoom +" button
    $("#zoom_in").button().click(
      function (e) {
        dream_instance.zoom_in();
      });

    // Enable "Zoom -" button
    $("#zoom_out").button().click(
      function (e) {
        dream_instance.zoom_out();
      });

    // Enable "Export" button
    $("#export").button().click(
      function (e) {
        $('#export_json').val(JSON.stringify(dream_instance.getData()));
        $('#export_form').submit();
        return false;
      });

    // Enable "Import" button
    $("#import").button().click(
      function (e) {
        $('#import_file').click();
      });
    $("#import_file").change(function () {
      var form = $(this).parent('form')[0];
      var form_data = new FormData(form);
      dream_instance.clearAll();
      $.ajax('/postJSONFile', {
        type: 'POST',
        contentType: false,
        processData: false,
        data: form_data,
        dataType: 'json',
        error: function () {
          console.log('error');
        },
        success: function (data, textStatus, jqXHR) {
          form.reset();
          $("#json_output").val(JSON.stringify(data));
          loadData(data);
        }
      });
      return false;
    });

    // Redraw if the graph area or the window is resized
    $('#main').resizable().resize(function () {
      dream_instance.redraw();
    });
    $(window).resize(function () {
      dream_instance.redraw();
    });

    $("#graph_zone").hide();

  });
})(jQuery);
