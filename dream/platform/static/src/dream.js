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

    priv.displayTool = function () {
      var render_element = $("#tools-container");
      for (var key in configuration) {
        if (key !== 'Dream-Configuration') {
          render_element.append('<div id="' + key + '" class="tool ' + key + '">' +
            key.split('-')[1] + "<ul/></div>");
        }
      }
    };

    priv.initDialog = function () {
      $("#dialog-form").dialog({
        autoOpen: false
      });
    };

    that.initGeneralProperties = function () {
      var fieldset = $("#general-fieldset"),
        previous_data = that.getData()['general'],
        previous_value = "",
        prefix = "General-";
      fieldset.children().remove();
      $.each(configuration['Dream-Configuration']['property_list'],
        function (idx, property) {
          if (property._class === "Dream.Property") {
            previous_value = previous_data[property.id] || "";
            if (previous_value.length > 0) {
              previous_value = ' value="' + previous_value + '"';
            }
            fieldset.append("<label>" + property.id + "</label>" +
              '<input type="text" name="' + prefix + property.id + '"' +
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
      var previous_data = that.getData()["nodes"];
      $("#dialog-fieldset").children().remove();
      var element_type = previous_data[element_id]._class.replace('.', '-');
      var property_list = configuration[element_type].property_list || [];

      fieldset.append(
        '<label>ID</label><input type="text" name="id" id="id" value="' +
        element_id + '" class="text ui-widget-content ui-corner-all"/>');
      var element_name = previous_data[element_id]['name'] || element_id;
      fieldset.append(
        '<label>Name</label><input type="text" name="name" id="name" value="' +
        element_name + '" class="text ui-widget-content ui-corner-all"/>');

      previous_data = previous_data[element_id] || {};
      previous_data = previous_data.data || {};
      var previous_value;
      var renderField = function (property_list, previous_data, prefix) {
        if (prefix === undefined) {
          prefix = "";
        }
        $.each(property_list, function (key, property) {
          if (property._class === "Dream.Property") {
            previous_value = previous_data[property.id] || "";
            if (previous_value.length > 0) {
              previous_value = ' value="' + previous_value + '"';
            }
            fieldset.append("<label>" + prefix + property.id + "</label>" +
              '<input type="text" name="' + prefix + property.id + '"' +
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
        title: title || "",
        buttons: {
          Cancel: function () {
            $(this).dialog("close");
          },
          Delete: function () {
            if (confirm("Are you sure you want to delete " + element_id +
              " ?")) {
              that.removeElement(element_id);
            }
            $(this).dialog("close");
          },
          Validate: function () {
            var new_id = $("#id").val();
            if (new_id !== element_id && $('#' + new_id).length > 0) {
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
                } else if (property._class === "Dream.PropertyList") {
                  var next_prefix = prefix + property.id + "-";
                  data[property.id] = {};
                  updateDataPropertyList(property.property_list, data[
                    property.id], next_prefix);
                }
              });
            };

            updateDataPropertyList(property_list, data);
            that.updateElementData(element_id, {
              data: data,
              name: $("#name").val() || element_id,
              id: $("#id").val() || element_id
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
      priv.super_newElement(element, configuration[element_type]);
      $("#" + element.id).on('click', function () {
        $("#dialog-form").dialog("destroy");
        priv.prepareDialogForElement(element.id, element.id);
        $("#dialog-form").dialog("open");
      });
      // Store default values
      var data = {}, property_list = configuration[element_type][
          "property_list"
        ] || [];
      var updateDefaultData = function (data, property_list) {
        $.each(property_list, function (key, element) {
          if (element) {
            if (element._class === "Dream.Property") {
              data[element.id] = element._default;
            } else if (element._class === "Dream.PropertyList") {
              data[element.id] = {};
              var next_data = data[element.id];
              var next_property_list = element.property_list || [];
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
      // save general configuration default values
      var general_properties = {};
      $.each(configuration["Dream-Configuration"].property_list, function (
        idx, element) {
        general_properties[element.id] = element._default;
      });
      that.setGeneralProperties(general_properties);
      that.initGeneralProperties();
    };

    priv.formatForManpy = function (data) {
      var manpy_dict = {}, nodes = {}, edges = {}, edge_id = 0;
      $.each(data['nodes'], function (idx, node) {
        var clone_node = {};
        /* clone the node and put content of 'data' at the top level. */
        $.each(node, function (k, v) {
          if (k == 'data') {
            $.each(v, function (kk, vv) {
              clone_node[kk] = vv;
            });
          } else if (k == 'id') {
            true; // no need to output
          } else {
            clone_node[k] = v;
          }
        });
        nodes[node['id']] = clone_node;
      });

      manpy_dict['nodes'] = nodes;
      manpy_dict['edges'] = data['edges'];
      manpy_dict['general'] = data['general'];
      manpy_dict['spreadsheet'] = data['spreadsheet'];
      return manpy_dict;
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
          }
        });
      that.setGeneralProperties(properties);

      var model = priv.formatForManpy(that.getData());
      $.ajax(
        '/runSimulation', {
          data: JSON.stringify({
            json: model
          }),
          contentType: 'application/json',
          type: 'POST',
          success: function (data, textStatus, jqXHR) {
            callback(data);
          }
        });
    };

    return that;
  };

}(window, jQuery, jsPlumb, console));
