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

<<<<<<< HEAD
  function capacity_utilisation_graph_widget(input_data, output_data) {
    var available_capacity_by_station = {},
        capacity_usage_by_station = {};

    $("#capacity_graphs").empty();

    // Compute availability by station
    $.each(input_data.nodes, function(idx, obj){
      var available_capacity = [];
      if (obj.intervalCapacity !== undefined) {
        $.each(obj.intervalCapacity, function(i, capacity){
          available_capacity.push([i, capacity]);
        });
        available_capacity_by_station[obj.id] = available_capacity;
      }
    });
    
    // Compute used capacity by station
    $.each(output_data.elementList.sort(
            function(a,b) {return a.id < b.id ? -1 : 1}),
      function (idx, obj) {
      if (obj.results !== undefined && obj.results.capacityUsed !== undefined) {
        var capacity_usage = [];

        $.each(obj.results.capacityUsed, function(i, step){
          var period = 0, usage = 0;
          $.each(step, function(k, v){
            if (k === 'period') {
               period = v;
            }
          });
          $.each(step, function(k, v){
            if (k !== 'utilization' && k !== 'period'){
              usage += v;
            }
          });
          capacity_usage.push([period, usage]) 
        });
        capacity_usage_by_station[obj.id] = capacity_usage;
      }
    });

    for (var station_id in available_capacity_by_station) {
      var series = [{
        label: "Capacity",
        data: available_capacity_by_station[station_id],
        color: "green",
      }, {
        label: "Utilisation",
        data: capacity_usage_by_station[station_id],
        color: "red",
      }];

      var options = {
        series: {
          lines: {
            show: true,
            fill: true
          }
        }
      };
      var h2 = $("<h2>").html(input_data.nodes[station_id].name || station_id);
      var graph = $("<div class='capacity_graph'></div>");
      $("#capacity_graphs").append(h2).append(graph);
      $.plot(graph, series, options);
    }
  };

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
      // XXX Migrate this part now!
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

    that.displayResult = function (idx, result) {
      // the list of available widgets, in the same order that in html
      var available_widget_list = [
        'station_utilisation_graph',
        'capacity_utilisation_graph',
        'exit_stat',
        'queue_stat',
        'job_schedule_spreadsheet',
        'job_gantt',
        'debug_json',
      ];

      // The active tab is the one that is selected or the first one that is
      // enabled
      var active_tab;
      if ($("#reports").data("ui-tabs")) {
        active_tab = $("#reports").tabs("option", "active");
      } else {
        for (var i in available_widget_list) {
          if (configuration['Dream-Configuration'].gui[available_widget_list[i]]) {
            active_tab = i;
            break;
          }
        }
      }

      $('li.result').removeClass('active');
      $($('li.result')[idx]).addClass('active');
      if ($("#reports").data("ui-tabs")) {
        $("#reports").tabs("destroy"); 
      }

      for (var i in available_widget_list) {
        var widget_name = available_widget_list[i];
        if (configuration['Dream-Configuration'].gui[widget_name]) {
          $("li > a[href='#" + widget_name  + "']").parent().show();
        } else {
          $("li > a[href='#" + widget_name  + "']").parent().hide();
        }
      }

      var input = result.input;
      result = result.result;

      // display each of the enabled widget
      if (configuration['Dream-Configuration'].gui.station_utilisation_graph){
        station_utilisation_graph_widget(input, result);
      }
      if (configuration['Dream-Configuration'].gui.capacity_utilisation_graph){
        capacity_utilisation_graph_widget(input, result);
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
      if (configuration['Dream-Configuration'].gui.debug_json){
        debug_json_widget(input, result);
      }

      // hack: make the tabs full width
      $("#reports li").width((100/$("#reports li:visible").length) - 1 +'%');
      $("#reports li a").width('100%').css({'text-align': 'left'});

      $("#reports").show().tabs({ active: active_tab });
    }

    return that;
  };
}(window, jQuery, jsPlumb, console));


