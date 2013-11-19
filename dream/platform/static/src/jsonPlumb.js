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
  scope.jsonPlumb = function (model) {
    var that = {}, priv = {};

    priv.initJsPlumb = function () {
      jsPlumb.setRenderMode(jsPlumb.SVG);
      var color = "#00f";
      jsPlumb.importDefaults({
        // default drag options
        DragOptions: {
          cursor: 'pointer',
          zIndex: 2000
        },
        EndpointStyles: [{
          fillStyle: '#225588'
        }, {
          fillStyle: '#558822'
        }],
        //PaintStyle : {strokeStyle:"#736AFF", lineWidth:2 },
        HoverPaintStyle: {
          strokeStyle: "#42a62c",
          lineWidth: 4
        },
        Endpoint: ["Dot", {
          radius: 2
        }],
        ConnectionOverlays: [
          ["Arrow", {
            location: 1,
            id: "arrow",
            length: 14,
            width: 12,
            foldback: 0.8
          }]
        ],
        PaintStyle: {
          lineWidth: 2,
          strokeStyle: color
        },
        Anchor: "Continuous",
        Connector: ["StateMachine", {
          curviness: 20
        }]
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

      jsPlumb.makeTarget(jsPlumb.getSelector(".w"), {
        dropOptions: {
          hoverClass: "dragHover"
        },
        anchor: "Continuous"
      });

      var updateConnectionData = function (connection, remove) {
        if (remove) {
          delete(priv.edge_container[connection.id]);
        } else {
          priv.edge_container[connection.id] = [
            connection.sourceId,
            connection.targetId,
            {}
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

    priv.updateElementCoordinate = function (element_id, coordinate) {
      var coordinates = priv.preference_container['coordinates'] || {}, element;
      if (coordinate === undefined) {
        coordinate = {};
        element = $("#" + element_id);
        var relative_position = priv.convertToRelativePosition(
          element.css('left'), element.css('top'));
        coordinate.top = relative_position[1];
        coordinate.left = relative_position[0];
      }
      coordinates[element_id] = coordinate;
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

    priv.convertToAbsolutePosition = function(x, y) {
      var canvas_size_x = $('#main').width();
      var canvas_size_y = $('#main').height();
      var node_style = priv.preference_container['node_style'];
      var size_x = node_style['width'].replace('px', '');
      var size_y = node_style['height'].replace('px', '');
      var top = Math.floor(y * (canvas_size_y - size_y)) + "px";
      var left = Math.floor(x * (canvas_size_x - size_x)) + "px";
      return [left, top];
    };

    priv.convertToRelativePosition = function(x, y) {
      var canvas_size_x = $('#main').width();
      var canvas_size_y = $('#main').height();
      var size_x = $('.window').width();
      var size_y = $('.window').height();
      var top = y.replace('px', '') / (canvas_size_y - size_y);
      var left = x.replace('px', '') / (canvas_size_y - size_y);
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
      var stop = function (el) {
        var element_id = el.target.id;
        priv.updateElementCoordinate(element_id);
      };
      jsPlumb.draggable(jsPlumb.getSelector(".window"), {
        grid: [10, 10],
        stop: stop
      });
    };
    priv.addElementToContainer = function (element) {
      // Now update the container of elements
      var element_data = {
        _class: element._class,
        id: element.id,
        name: element.id
      };
      priv.node_container[element.id] = element_data;
      priv.onDataChange();
    };

    priv.onDataChange = function () {
      $.publish("Dream.Gui.onDataChange", priv.getData());
    };

    priv.style_attr_list = ['width', 'height', 'font-size', 'padding-top',
                            'line-height'];

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
        var element = $('#' + node_id);
        element.css('top', absolute_position[1]);
        element.css('left', absolute_position[0]);
      });
      jsPlumb.repaintEverything();
    };

    priv.getData = function () {
      return {
        "nodes": priv.node_container,
        "edges": priv.edge_container,
        "preference": priv.preference_container,
        "general": priv.general_container
      };
    };

    priv.removeElement = function (element_id) {
      jsPlumb.removeAllEndpoints($("#" + element_id));
      $("#" + element_id).remove();
      delete(priv.node_container[element_id]);
      delete(priv.preference_container['coordinates'][element_id]);
      $.each(priv.edge_container, function (k, v) {
        if (element_id == v[0] || element_id == v[1]) {
          delete(priv.edge_container[k]);
        }
      });
      priv.onDataChange();
    };

    that.updateElementData = function (element_id, data) {
      $.extend(priv.node_container[element_id], data);
      if (data['name']) {
        $("#" + element_id).text(data["name"]);
      }
      priv.onDataChange();
    };

    that.start = function () {
      priv.node_container = {};
      priv.edge_container = {};
      priv.preference_container = {};
      priv.general_container = {};
      priv.initJsPlumb();
    };

    that.removeElement = function (element_id) {
      priv.removeElement(element_id);
    };

    that.getData = function () {
      return priv.getData();
    };

    that.clearAll = function () {
      $("[id=render]").children().remove();
      $.each(priv.node_container, function (element_id) {
        priv.removeElement(element_id);
      });
    };

    that.connect = function (source_id, target_id) {
      jsPlumb.connect({
        source: source_id,
        target: target_id
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
      var render_element, style_string = "",
        coordinate = element.coordinate,
        box;
      render_element = $("[id=render]");
      if (coordinate !== undefined) {
        coordinate = priv.updateElementCoordinate(element.id, coordinate);
      }
      render_element.append('<div class="window ' + element._class.replace('.', '-') + '" id="' +
        element.id + '">' + element.id + '</div>');
      box = $("#" + element.id);
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
        maxConnections: 3,
        isTarget: true
      };
      for (var key in option.anchor) {
        jsPlumb.addEndpoint(element.id, {
          anchor: key
        }, endpoint);
      }
      priv.addElementToContainer(element);
    };

    return that;
  };

}(window, jQuery, jsPlumb, console));
