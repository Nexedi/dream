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

(function (scope, $, jsPlumb, console) {
  "use strict";
  scope.jsonPlumb = function () {
    var that = {}, priv = {};

    that.getNodeId = function (element_id) {
      var node_id;
      $.each(priv.node_container, function (k, v) {
        if (v['element_id'] === element_id) {
          node_id = k;
          return false;
        }
      });
      return node_id;
    };

    that.getElementId = function (node_id) {
      return priv.node_container[node_id].element_id;
    };

    that.generateNodeId = function (element_type, option) {
      var n = 1;
      while (((option['short_id'] || element_type) + n) in priv.node_container) {
        n += 1;
      }
      return (option['short_id'] || element_type) + n;
    };

    that.generateElementId = function () {
      var n = 1;
      while ($('#DreamNode_' + n).length > 0) {
        n += 1;
      }
      return 'DreamNode_' + n;
    };

    priv.initJsPlumb = function () {
      jsPlumb.setRenderMode(jsPlumb.SVG);
      var color = "#00f";
      jsPlumb.importDefaults({
        HoverPaintStyle: {
          strokeStyle: "#1e8151",
          lineWidth: 2
        },
        Endpoint: ["Dot", {
          radius: 2
        }],
        ConnectionOverlays: [
          ["Arrow", {
            location: 1,
            id: "arrow",
            length: 14,
            foldback: 0.8
          }]
        ],
        Container: "main"
      });

      // listen for clicks on connections, and offer to change values on click.
      jsPlumb.bind("click", function (conn) {
        jsPlumb.detach(conn);
      });

      jsPlumb.bind("beforeDetach", function (conn) {
        return confirm("Delete connection?");
      });

      jsPlumb.bind("connectionDrag", function (connection) {});

      jsPlumb.bind("connectionDragStop", function (connection) {});

      // split in 2 methods ? one for events one for manip
      that.updateConnectionData = function (connection, remove, edge_data) {
        if (remove) {
          delete(priv.edge_container[connection.id]);
        } else {
          priv.edge_container[connection.id] = [
            that.getNodeId(connection.sourceId),
            that.getNodeId(connection.targetId), edge_data || {}
          ];
        }
        priv.onDataChange();
      };

      // bind to connection/connectionDetached events, and update the list of connections on screen.
      jsPlumb.bind("connection", function (info, originalEvent) {
        that.updateConnectionData(info.connection);
      });
      jsPlumb.bind("connectionDetached", function (info, originalEvent) {
        that.updateConnectionData(info.connection, true);
      });
      priv.onDataChange();
      priv.draggable();
    };

    priv.initSpreadSheet = function () {
      var wip_part_spreadsheet = $('#wip_part_spreadsheet');
      var data = [
        [
          "Order ID",
          "Due Date",
          "Priority",
          "Project Manager",
          "Part",
          "Part Type",
          "Sequence",
          "Processing Times",
          "Prerequisites Parts"
        ]
      ];
      wip_part_spreadsheet.handsontable({
        data: data,
        minSpareRows: 1,
        stretchH: 'all',
        width: function () {
            return $(window).width() -
                  wip_part_spreadsheet.offset().left +
                  $(window).scrollLeft();
        },
        afterChange: function () {
          priv.onDataChange();
        },
      });

      var shift_spreadsheet = $('#shift_spreadsheet');
      var data = [
        [
          "Day",
          "Machines", // XXX more generic name ?
          "Start",
          "End"
        ]
      ];
      shift_spreadsheet.handsontable({
        data: data,
        minSpareRows: 1,
        stretchH: 'all',
        width: function () {
            return $(window).width() -
                  shift_spreadsheet.offset().left +
                  $(window).scrollLeft();
        },
        afterChange: function () {
          priv.onDataChange();
        }
      });

    };

    priv.updateElementCoordinate = function (node_id, coordinate) {
      var element_id = priv.node_container[node_id].element_id;
      var coordinates = priv.preference_container['coordinates'] || {}, element;
      if (coordinate === undefined) {
        coordinate = {};
        element = $("#" + element_id);
        var relative_position = that.convertToRelativePosition(
          element.css('left'), element.css('top'));
        coordinate.top = relative_position[1];
        coordinate.left = relative_position[0];
      }
      coordinates[node_id] = coordinate;
      priv.preference_container['coordinates'] = coordinates;
      priv.onDataChange();
      return coordinate;
    };

    priv.updateNodeStyle = function (element_id) {
      var zoom_level = (priv.preference_container['zoom_level'] || 1.0) * 1.1111;
      var element = $("#" + element_id);
      $.each(priv.style_attr_list, function (i, j) {
        var new_value = $('.dummy_window').css(j).replace('px', '') * zoom_level + 'px';
        element.css(j, new_value);
      });
    };

    priv.convertToAbsolutePosition = function (x, y) {
      var zoom_level = (priv.preference_container['zoom_level'] || 1.0) * 1.1111;
      var canvas_size_x = $('#main').width();
      var canvas_size_y = $('#main').height();
      var size_x = $('.dummy_window').width() * zoom_level;
      var size_y = $('.dummy_window').height() * zoom_level;
      var top = Math.floor(y * (canvas_size_y - size_y)) + "px";
      var left = Math.floor(x * (canvas_size_x - size_x)) + "px";
      return [left, top];
    };

    that.convertToRelativePosition = function (x, y) {
      var zoom_level = (priv.preference_container['zoom_level'] || 1.0) * 1.1111;
      var canvas_size_x = $('#main').width();
      var canvas_size_y = $('#main').height();
      var size_x = $('.dummy_window').width() * zoom_level;
      var size_y = $('.dummy_window').height() * zoom_level;
      var top = Math.max(Math.min(y.replace('px', '') / (canvas_size_y - size_y), 1), 0);
      var left = Math.max(Math.min(x.replace('px', '') / (canvas_size_x - size_x), 1), 0);
      return [left, top];
    };

    priv.draggable = function () {
      var stop = function (element) {
        priv.updateElementCoordinate(that.getNodeId(element.target.id));
      };

      jsPlumb.draggable(jsPlumb.getSelector(".window"), {
        containment: 'parent',
        grid: [10, 10],
        stop: stop // FIXME: we should only accept if dropped in #main
      });

      jsPlumb.makeSource(jsPlumb.getSelector(".window"), {
        filter: ".ep",
        anchor: "Continuous",
        connector: ["StateMachine", {
          curviness: 20
        }],
        connectorStyle: {
          strokeStyle: "#5c96bc",
          lineWidth: 2,
          outlineColor: "transparent",
          outlineWidth: 4
        }
      });

      jsPlumb.makeTarget(jsPlumb.getSelector(".window"), {
        dropOptions: {
          hoverClass: "dragHover"
        },
        anchor: "Continuous"
      });

    };
    priv.addElementToContainer = function (element) {
      // Now update the container of elements
      var element_data = {
        _class: element._class,
        element_id: element.element_id,
      };
      priv.node_container[element.id] = element_data;
    };

    priv.onDataChange = function () {
      $.publish("Dream.Gui.onDataChange", priv.getData());
    };

    priv.style_attr_list = ['width', 'height', 'padding-top', 'line-height'];

    that.positionGraph = function () {
      $.ajax(
        '/positionGraph', {
          data: JSON.stringify(priv.getData()),
          contentType: 'application/json',
          type: 'POST',
          success: function (data, textStatus, jqXHR) {
            $.each(data, function (node, pos) {
              var absolute_position = priv.convertToAbsolutePosition(
                pos.left, pos.top);
              priv.updateElementCoordinate(node, {
                top: pos.top,
                left: pos.left
              });
            });
            that.redraw();
          }
        });

    };

    that.setZoom = function (zoom_level) {
      $.each(priv.style_attr_list, function (i, j) {
        var new_value = $('.dummy_window').css(j).replace('px', '') * zoom_level + 'px';
        $('.window').css(j, new_value);
      });
    };

    that.zoom_in = function () {
      var zoom_level = (priv.preference_container['zoom_level'] || 1.0) * 1.1111;
      that.setZoom(zoom_level);
      priv.preference_container['zoom_level'] = zoom_level;
      priv.onDataChange();
      that.redraw();
    };

    that.zoom_out = function () {
      var zoom_level = (priv.preference_container['zoom_level'] || 1.0) * 0.9;
      that.setZoom(zoom_level);
      priv.preference_container['zoom_level'] = zoom_level;
      priv.onDataChange();
      that.redraw();
    };

    that.redraw = function () {
      var coordinates = priv.preference_container['coordinates'] || {};
      $.each(coordinates, function (node_id, v) {
        var absolute_position = priv.convertToAbsolutePosition(
          v['left'], v['top']);
        var element = $('#' + that.getElementId(node_id));
        element.css('top', absolute_position[1]);
        element.css('left', absolute_position[0]);
        jsPlumb.repaint(element);
      });
    };

    priv.getData = function () {
      var data = {
        "nodes": priv.node_container,
        "edges": priv.edge_container,
        "preference": priv.preference_container,
        "general": priv.general_container
      };
      var wip_spreadsheet = $('#wip_spreadsheet');
      if (wip_spreadsheet.length > 0) {
        data['wip_spreadsheet'] = wip_spreadsheet.handsontable('getData');
      }
      var wip_part_spreadsheet = $('#wip_part_spreadsheet');
      if (wip_part_spreadsheet.length > 0) {
        data['wip_part_spreadsheet'] = wip_part_spreadsheet.handsontable('getData');
      }
      var shift_spreadsheet = $('#shift_spreadsheet');
      if (shift_spreadsheet.length > 0) {
        data['shift_spreadsheet'] = shift_spreadsheet.handsontable('getData');
      }
      return data;
    };

    priv.removeElement = function (node_id) {
      var element_id = priv.node_container[node_id].element_id;
      jsPlumb.removeAllEndpoints($("#" + element_id));
      $("#" + element_id).remove();
      delete(priv.node_container[node_id]);
      delete(priv.preference_container['coordinates'][node_id]);
      $.each(priv.edge_container, function (k, v) {
        if (node_id == v[0] || node_id == v[1]) {
          delete(priv.edge_container[k]);
        }
      });
      priv.onDataChange();
    };

    that.updateElementData = function (node_id, data) {
      var element_id = priv.node_container[node_id].element_id;
      if (data['name']) {
        $("#" + element_id).text(data["name"]).append('<div class="ep"></div></div>');
        priv.node_container[node_id].name = data['name'];
      }
      var new_id = data['id'];
      delete(data['id']);
      $.extend(priv.node_container[node_id], data.data);
      if (new_id && new_id !== node_id) {
        priv.node_container[new_id] = priv.node_container[node_id];
        delete(priv.node_container[node_id]);
        $.each(priv.edge_container, function (k, v) {
          if (v[0] === node_id) {
            v[0] = new_id;
          }
          if (v[1] === node_id) {
            v[1] = new_id;
          }
        });
        priv.preference_container['coordinates'][new_id] = priv.preference_container['coordinates'][node_id];
        delete(priv.preference_container['coordinates'][node_id]);
      }
      priv.onDataChange();
    };

    that.start = function () {
      priv.node_container = {};
      priv.edge_container = {};
      priv.preference_container = {};
      priv.general_container = {};
      priv.initJsPlumb();
      priv.initSpreadSheet();
    };

    that.removeElement = function (node_id) {
      priv.removeElement(node_id);
    };

    that.getData = function () {
      return priv.getData();
    };

    that.clearAll = function () {
      $.each(priv.node_container, function (node_id) {
        priv.removeElement(node_id);
      });
      // delete anything if still remains
      $("#main").children().remove();
      priv.node_container = {};
      priv.edge_container = {};
      priv.preference_container = {};
      priv.general_container = {};
      priv.initSpreadSheet();
      that.initGeneralProperties();
      that.prepareDialogForGeneralProperties();
    };

    that.addEdge = function (edge_id, edge_data) {
      var source_id = edge_data[0],
          target_id = edge_data[1],
          data = edge_data[2],
          overlays = []

      if (data && data.title){
        overlays = [ ["Label", { cssClass:"l1 component label",
                                label: data.title,
                            }] ]

      }
      var connection = jsPlumb.connect({
        source: that.getElementId(source_id),
        target: that.getElementId(target_id),
        Connector: [ "Bezier", { curviness:75 } ],
        overlays:overlays

      });
      // call again updateConnectionData to set the connection data that
      // was not passed to the connection hook
      that.updateConnectionData(connection, 0, data)
    };

    that.setPreferences = function (preferences) {
      priv.preference_container = preferences;
      var zoom_level = priv.preference_container['zoom_level'] || 1.0;
      that.setZoom(zoom_level);
    };

    that.setGeneralProperties = function (properties) {
      priv.general_container = properties;
      priv.onDataChange();
    };

    that.updateGeneralProperties = function (properties) {
      $.extend(priv.general_container, properties);
      priv.onDataChange();
    };

    that.newElement = function (element, option) {
      element.name = element.name || option.name;
      priv.addElementToContainer(element);
      var render_element, style_string = "",
        coordinate = element.coordinate,
        box;
      render_element = $("#main");
      if (coordinate !== undefined) {
        coordinate = priv.updateElementCoordinate(element.id, coordinate);
      }
      render_element.append('<div class="window ' + element._class.replace('.', '-') + '" id="' +
        element.element_id + '" title="' + (element.name || element.id) + '">' + element.id + '<div class="ep"></div></div>');
      box = $("#" + element.element_id);
      var absolute_position = priv.convertToAbsolutePosition(
        coordinate.left, coordinate.top);
      box.css("top", absolute_position[1]);
      box.css("left", absolute_position[0]);
      priv.updateNodeStyle(element.element_id);

      priv.draggable();

      priv.onDataChange();
    };

    return that;
  };

}(window, jQuery, jsPlumb, console));
