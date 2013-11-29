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

    that.generateNodeId = function (element_type) {
      var n = 1;
      while ((element_type + '_' + n) in priv.node_container) {
        n += 1;
      }
      return element_type + '_' + n;
    }

    that.generateElementId = function () {
      var n = 1;
      while ($('#DreamNode_' + n).length > 0) {
        n += 1;
      }
      return 'DreamNode_' + n;
    }

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
        Container: "render"
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

      var updateConnectionData = function (connection, remove) {
        if (remove) {
          delete(priv.edge_container[connection.id]);
        } else {
          priv.edge_container[connection.id] = [
            that.getNodeId(connection.sourceId),
            that.getNodeId(connection.targetId), {}
          ];
        }
        priv.onDataChange();
      };

      // bind to connection/connectionDetached events, and update the list of connections on screen.
      jsPlumb.bind("connection", function (info, originalEvent) {
        updateConnectionData(info.connection);
      });
      jsPlumb.bind("connectionDetached", function (info, originalEvent) {
        updateConnectionData(info.connection, true);
      });
      priv.onDataChange();
      priv.draggable();
    };

    priv.initSpreadSheet = function () {
      var sheet = $('.jQuerySheet');
      $.get('spreadsheet_template.html', function (data) {
        sheet.html(data).sheet({
          autoAddCells: false
        });
        sheet.getSheet().setNav(false);
        // Here we bind on the parent object because bind will be
        // reset when we replace the contents by using html().
        $('#spreadsheet').on('sheetCellEdited', function () {
          priv.onDataChange();
        });
        // When we click outside of the
        // spreadsheet, keyevent should not be taken by spreadsheet.
        $(document).mousedown(function () {
          $('.jQuerySheet').getSheet().setNav(false);
        });
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
      var node_style = priv.preference_container['node_style'];
      var element = $("#" + element_id);
      if (node_style !== undefined) {
        element.css(node_style);
      } else {
        var style_dict = {};
        $.each(priv.style_attr_list, function (i, j) {
          style_dict[j] = $('.window').css(j);
        });
        priv.saveNodeStyle(style_dict);
      }
    };

    priv.convertToAbsolutePosition = function (x, y) {
      var canvas_size_x = $('#main').width();
      var canvas_size_y = $('#main').height();
      var node_style = priv.preference_container['node_style'];
      var size_x, size_y;
      if (node_style === undefined) {
        size_x = $('.window').css('width').replace('px', '');
        size_y = $('.window').css('height').replace('px', '');
      } else {
        size_x = node_style['width'].replace('px', '');
        size_y = node_style['height'].replace('px', '');
      }
      var top = Math.floor(y * (canvas_size_y - size_y)) + "px";
      var left = Math.floor(x * (canvas_size_x - size_x)) + "px";
      return [left, top];
    };

    that.convertToRelativePosition = function (x, y) {
      var canvas_size_x = $('#main').width();
      var canvas_size_y = $('#main').height();
      var node_style = priv.preference_container['node_style'];
      var size_x, size_y;
      if (node_style === undefined) {
        size_x = $('.window').width();
        size_y = $('.window').height();
      } else {
        size_x = node_style['width'].replace('px', '');
        size_y = node_style['height'].replace('px', '');
      }
      var top = Math.max(Math.min(y.replace('px', '') / (canvas_size_y - size_y), 1), 0);
      var left = Math.max(Math.min(x.replace('px', '') / (canvas_size_x - size_x), 1), 0);
      return [left, top];
    };

    priv.saveNodeStyle = function (style_dict) {
      var node_style = priv.preference_container['node_style'] || {};
      $.each(style_dict, function (k, v) {
        node_style[k] = v;
      });
      priv.preference_container['node_style'] = node_style;
      priv.onDataChange();
    };

    priv.draggable = function () {
      // make all the window divs draggable
      var stop = function (element) {
        priv.updateElementCoordinate(that.getNodeId(element.target.id));
      };

      jsPlumb.draggable(jsPlumb.getSelector(".window"), {
        containment: 'parent',
        grid: [10, 10],
        stop: stop
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
        },
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
        name: element.name
      };
      priv.node_container[element.id] = element_data;
    };

    priv.onDataChange = function () {
      $.publish("Dream.Gui.onDataChange", priv.getData());
    };

    priv.style_attr_list = ['width', 'height', 'font-size', 'padding-top',
      'line-height'
    ];

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

    that.zoom_in = function () {
      var style_dict = {};
      $.each(priv.style_attr_list, function (i, j) {
        var new_value = $('.window').css(j).replace('px', '') * 1.1111 + 'px';
        $('.window').css(j, new_value);
        style_dict[j] = new_value;
      });
      priv.saveNodeStyle(style_dict);
      that.redraw();
    };

    that.zoom_out = function () {
      var style_dict = {};
      $.each(priv.style_attr_list, function (i, j) {
        var new_value = $('.window').css(j).replace('px', '') * 0.9 + 'px';
        $('.window').css(j, new_value);
        style_dict[j] = new_value;
      });
      priv.saveNodeStyle(style_dict);
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
      var spreadsheet = $('.jQuerySheet').getSheet();
      if (spreadsheet !== undefined) {
        data['spreadsheet'] = $.sheet.dts.fromTables.json(spreadsheet);
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
        $("#" + element_id).text(data["name"]);
      }
      var new_id = data['id'];
      delete(data['id']);
      $.extend(priv.node_container[node_id], data);
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
      $("#render").children().remove();
      priv.initSpreadSheet();
    };

    that.connect = function (source_id, target_id) {
      jsPlumb.connect({
        source: that.getElementId(source_id),
        target: that.getElementId(target_id)
      });
    };

    that.setPreferences = function (preferences) {
      priv.preference_container = preferences;
    };

    that.setGeneralProperties = function (properties) {
      priv.general_container = properties;
      priv.onDataChange();
    };

    that.newElement = function (element, option) {
      priv.addElementToContainer(element);
      var render_element, style_string = "",
        coordinate = element.coordinate,
        box;
      render_element = $("#render");
      if (coordinate !== undefined) {
        coordinate = priv.updateElementCoordinate(element.id, coordinate);
      }
      render_element.append('<div class="window ' + element._class.replace('.', '-') + '" id="' +
        element.element_id + '">' + (element.name || element.id) + '<div class="ep"></div></div>');
      box = $("#" + element.element_id);
      var absolute_position = priv.convertToAbsolutePosition(
        coordinate.left, coordinate.top);
      box.css("top", absolute_position[1]);
      box.css("left", absolute_position[0]);
      priv.updateNodeStyle(element.id);

      // Initial DEMO code : make all the window divs draggable
      priv.draggable();

      // Add endPoint to allow drawing connections
      var color = "#00f";
      // Different endpoint color for Repairman
      if (element._class === "Dream.Repairman") {
        color = "rgb(189,11,11)";
      }
      var endpoint = {
        endpoint: "Rectangle",
        paintStyle: {
          width: 25,
          height: 21,
          fillStyle: color
        },
        isSource: true,
        scope: "blue rectangle",
        isTarget: true
      };
      priv.onDataChange();
    };

    return that;
  };

}(window, jQuery, jsPlumb, console));
