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
 * ==========================================================================*/

/*global RSVP, rJS, $, jsPlumb, console, confirm*/
(function ($, jsPlumb, console) {
  "use strict";

  rJS(window)
    .ready(function (g) {
      g.private = {
        getNodeId: function (element_id) {
          var node_id;
          $.each(g.private.node_container, function (k, v) {
            if (v.element_id === element_id) {
              node_id = k;
              return false;
            }
          });
          return node_id;
        },

        getElementId: function (node_id) {
          return g.private.node_container[node_id].element_id;
        },

        generateNodeId: function (element_type, option) {
          var n = 1;
          while (g.private.node_container[
              ((option.short_id || element_type) + n)
            ] !== undefined) {
            n += 1;
          }
          return (option.short_id || element_type) + n;
        },

        generateElementId: function () {
          var n = 1;
          while ($(g.private.element).find('#DreamNode_' + n).length > 0) {
            n += 1;
          }
          return 'DreamNode_' + n;
        },

        initJsPlumb: function () {
          g.private.jsplumb_instance.setRenderMode(
            g.private.jsplumb_instance.SVG
          );
          g.private.jsplumb_instance.importDefaults({
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

          // listen for clicks on connections,
          // and offer to change values on click.
          g.private.jsplumb_instance.bind("click", function (conn) {
            g.private.jsplumb_instance.detach(conn);
          });

          g.private.jsplumb_instance.bind("beforeDetach", function (conn) {
            return confirm("Delete connection?");
          });

          g.private.jsplumb_instance
            .bind("connectionDrag", function (connection) {
              return undefined;
            });

          g.private.jsplumb_instance
            .bind("connectionDragStop", function (connection) {
              return undefined;
            });
          // split in 2 methods ? one for events one for manip
          g.private.updateConnectionData
            = function (connection, remove, edge_data) {
              if (remove) {
                delete g.private.edge_container[connection.id];
              } else {
                g.private.edge_container[connection.id] = [
                  g.private.getNodeId(connection.sourceId),
                  g.private.getNodeId(connection.targetId), edge_data || {}
                ];
              }
              g.private.onDataChange();
            };

          // bind to connection/connectionDetached events,
          // and update the list of connections on screen.
          g.private.jsplumb_instance
            .bind("connection", function (info, originalEvent) {
              g.private.updateConnectionData(info.connection);
            });
          g.private.jsplumb_instance
            .bind("connectionDetached", function (info, originalEvent) {
              g.private.updateConnectionData(info.connection, true);
            });
          g.private.onDataChange();
          g.private.draggable();
        },

        updateElementCoordinate: function (node_id, coordinate) {
          var element_id = g.private.node_container[node_id].element_id,
            coordinates = g.private.preference_container.coordinates || {},
            element,
            relative_position;
          if (coordinate === undefined) {
            coordinate = {};
            element = $(g.private.element).find("#" + element_id);
            relative_position = g.private.convertToRelativePosition(
              element.css('left'),
              element.css('top')
            );
            coordinate.top = relative_position[1];
            coordinate.left = relative_position[0];
          }
          coordinates[node_id] = coordinate;
          g.private.preference_container.coordinates = coordinates;
          g.private.onDataChange();
          return coordinate;
        },

        updateNodeStyle: function (element_id) {
          var zoom_level = (g.private.preference_container.zoom_level || 1.0) *
              1.1111,
            element = $(g.private.element).find("#" + element_id),
            new_value;
          console.log(g.private.element);
          $.each(g.private.style_attr_list, function (i, j) {
            new_value = $(g.private.element).find('.dummy_window').css(j)
              .replace('px', '') * zoom_level + 'px';
            element.css(j, new_value);
          });
        },

        convertToAbsolutePosition: function (x, y) {
          var zoom_level = (g.private.preference_container.zoom_level || 1.0) *
              1.1111,
            canvas_size_x = $(g.private.element).find('#main').width(),
            canvas_size_y = $(g.private.element).find('#main').height(),
            size_x = $(g.private.element).find('.dummy_window').width() *
              zoom_level,
            size_y = $(g.private.element).find('.dummy_window').height() *
              zoom_level,
            top = Math.floor(y * (canvas_size_y - size_y)) + "px",
            left = Math.floor(x * (canvas_size_x - size_x)) + "px";
          return [left, top];
        },

        convertToRelativePosition: function (x, y) {
          var zoom_level = (g.private.preference_container.zoom_level || 1.0) *
              1.1111,
            canvas_size_x = $(g.private.element).find('#main').width(),
            canvas_size_y = $(g.private.element).find('#main').height(),
            size_x = $(g.private.element).find('.dummy_window').width() *
              zoom_level,
            size_y = $(g.private.element).find('.dummy_window').height() *
              zoom_level,
            top = Math.max(Math.min(y.replace('px', '') /
                                  (canvas_size_y - size_y), 1), 0),
            left = Math.max(Math.min(x.replace('px', '') /
                                   (canvas_size_x - size_x), 1), 0);
          return [left, top];
        },

        draggable: function () {
          var stop = function (element) {
            g.private.updateElementCoordinate(g.private.getNodeId(
              element.target.id
            ));
          };

          g.private.jsplumb_instance
            .draggable(g.private.jsplumb_instance.getSelector(".window"), {
              containment: 'parent',
              grid: [10, 10],
              stop: stop // FIXME: we should only accept if dropped in #main
            });

          g.private.jsplumb_instance
            .makeSource(g.private.jsplumb_instance.getSelector(".window"), {
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

          g.private.jsplumb_instance
            .makeTarget(g.private.jsplumb_instance.getSelector(".window"), {
              dropOptions: {
                hoverClass: "dragHover"
              },
              anchor: "Continuous"
            });
        },

        addElementToContainer: function (element) {
          // Now update the container of elements
          /*jslint nomen: true*/
          var element_data = {
            _class: element._class,
            element_id: element.element_id
          };
          g.private.node_container[element.id] = element_data;
        },

        onDataChange: function () {
          //$.publish("Dream.Gui.onDataChange", g.private.getData());
          return undefined;
        },

        style_attr_list: ['width', 'height', 'padding-top', 'line-height'],

        positionGraph: function () {
          $.ajax(
            '/positionGraph',
            {
              data: JSON.stringify(g.private.getData()),
              contentType: 'application/json',
              type: 'POST',
              success: function (data, textStatus, jqXHR) {
                $.each(data, function (node, pos) {
                  g.private.convertToAbsolutePosition(
                    pos.left,
                    pos.top
                  );
                  g.private.updateElementCoordinate(node, {
                    top: pos.top,
                    left: pos.left
                  });
                });
                g.private.redraw();
              }
            }
          );
        },

        setZoom: function (zoom_level) {
          $.each(g.private.style_attr_list, function (i, j) {
            var new_value = $(g.private.element).find('.dummy_window')
              .css(j).replace('px', '') * zoom_level + 'px';
            $(g.private.element).find('.window').css(j, new_value);
          });
        },

        zoom_in: function () {
          var zoom_level = (g.private.preference_container.zoom_level || 1.0) *
            1.1111;
          g.private.setZoom(zoom_level);
          g.private.preference_container.zoom_level = zoom_level;
          g.private.onDataChange();
          g.private.redraw();
        },

        zoom_out: function () {
          var zoom_level = (g.private.preference_container.zoom_level || 1.0) *
            0.9;
          g.private.setZoom(zoom_level);
          g.private.preference_container.zoom_level = zoom_level;
          g.private.onDataChange();
          g.private.redraw();
        },

        redraw: function () {
          var coordinates = g.private.preference_container.coordinates || {},
            absolute_position,
            element;
          $.each(coordinates, function (node_id, v) {
            absolute_position = g.private.convertToAbsolutePosition(
              v.left,
              v.top
            );
            element = $(g.private.element).find('#' + g.private.getElementId(
              node_id
            ));
            element.css('top', absolute_position[1]);
            element.css('left', absolute_position[0]);
            g.private.jsplumb_instance.repaint(element);
          });
        },

        getData: function () {
          var data = {
            "nodes": g.private.node_container,
            "edges": g.private.edge_container,
            "preference": g.private.preference_container,
            "general": g.private.general_container
          },
            wip_spreadsheet = $(g.private.element).find('#wip_spreadsheet'),
            wip_part_spreadsheet = $(g.private.element)
            .find('#wip_part_spreadsheet'),
            shift_spreadsheet = $(g.private.element)
            .find('#shift_spreadsheet');
          if (wip_spreadsheet.length > 0) {
            data.wip_spreadsheet = wip_spreadsheet.handsontable('getData');
          }
          if (wip_part_spreadsheet.length > 0) {
            data.wip_part_spreadsheet = wip_part_spreadsheet
              .handsontable('getData');
          }
          if (shift_spreadsheet.length > 0) {
            data.shift_spreadsheet = shift_spreadsheet.handsontable('getData');
          }
          return data;
        },

        removeElement: function (node_id) {
          var element_id = g.private.node_container[node_id].element_id;
          g.private.jsplumb_instance.removeAllEndpoints($(g.private.element)
                                     .find("#" + element_id));
          $(g.private.element).find("#" + element_id).remove();
          delete g.private.node_container[node_id];
          delete g.private.preference_container.coordinates[node_id];
          $.each(g.private.edge_container, function (k, v) {
            if (node_id === v[0] || node_id === v[1]) {
              delete g.private.edge_container[k];
            }
          });
          g.private.onDataChange();
        },

        updateElementData: function (node_id, data) {
          var element_id = g.private.node_container[node_id].element_id,
            new_id = data.id;
          if (data.name) {
            $(g.private.element).find("#" + element_id).text(data.name)
              .append('<div class="ep"></div></div>');
            g.private.node_container[node_id].name = data.name;
          }
          delete data.id;
          $.extend(g.private.node_container[node_id], data.data);
          if (new_id && new_id !== node_id) {
            g.private.node_container[new_id]
              = g.private.node_container[node_id];
            delete g.private.node_container[node_id];
            $.each(g.private.edge_container, function (k, v) {
              if (v[0] === node_id) {
                v[0] = new_id;
              }
              if (v[1] === node_id) {
                v[1] = new_id;
              }
            });
            g.private.preference_container.coordinates[new_id]
              = g.private.preference_container.coordinates[node_id];
            delete g.private.preference_container.coordinates[node_id];
          }
          g.private.onDataChange();
        },

        start: function () {
          g.private.node_container = {};
          g.private.edge_container = {};
          g.private.preference_container = {};
          g.private.general_container = {};
          g.private.initJsPlumb();
        },

        clearAll: function () {
          $.each(g.private.node_container, function (node_id) {
            g.private.removeElement(node_id);
          });
          // delete anything if still remains
          $(g.private.element).find("#main").children().remove();
          g.private.node_container = {};
          g.private.edge_container = {};
          g.private.preference_container = {};
          g.private.general_container = {};
          g.private.initGeneralProperties();
          g.private.prepareDialogForGeneralProperties();
        },

        addEdge: function (edge_id, edge_data) {
          var source_id = edge_data[0],
            target_id = edge_data[1],
            data = edge_data[2],
            overlays = [],
            connection;
          if (data && data.title) {
            overlays = [["Label", {
              cssClass: "l1 component label",
              label: data.title
            }]];
          }
          connection = g.private.jsplumb_instance.connect({
            source: g.private.getElementId(source_id),
            target: g.private.getElementId(target_id),
            Connector: [ "Bezier", {curviness: 75} ],
            overlays: overlays
          });
          // call again updateConnectionData to set the connection data that
          // was not passed to the connection hook
          g.private.updateConnectionData(connection, 0, data);
        },

        setPreferences: function (preferences) {
          g.private.preference_container = preferences;
          var zoom_level = g.private.preference_container.zoom_level || 1.0;
          g.private.setZoom(zoom_level);
        },

        setGeneralProperties: function (properties) {
          g.private.general_container = properties;
          g.private.onDataChange();
        },

        updateGeneralProperties: function (properties) {
          $.extend(g.private.general_container, properties);
          g.private.onDataChange();
        },

        newElement: function (element, option) {
          element.name = element.name || option.name;
          g.private.addElementToContainer(element);
          var render_element,
            coordinate = element.coordinate,
            box,
            absolute_position;
          render_element = $(g.private.element).find("#main");
          if (coordinate !== undefined) {
            coordinate = g.private.updateElementCoordinate(
              element.id,
              coordinate
            );
          }
          /*jslint nomen: true*/
          render_element.append('<div class="window ' + element._class
                                .replace('.', '-') + '" id="' +
                                element.element_id + '" title="' +
                                (element.name || element.id) + '">' +
                                element.id +
                                '<div class="ep"></div></div>');
          box = $(g.private.element).find("#" + element.element_id);
          absolute_position = g.private.convertToAbsolutePosition(
            coordinate.left,
            coordinate.top
          );
          box.css("top", absolute_position[1]);
          box.css("left", absolute_position[0]);
          g.private.updateNodeStyle(element.element_id);
          g.private.draggable();
          g.private.onDataChange();
        }
      };
    })

    .ready(function (g) {
      window.g = g;
      return g.getElement(function (el) {
        g.private.element = el;
      });
    })

    .declareMethod('render', function (data) {
      this.private.data = JSON.parse(data);
      this.private.jsplumb_instance = jsPlumb.getInstance();
    })

    .declareMethod('startService', function () {
      var g = this;
      return this.getElement()
        .push(function (element) {
          g.private.element = element;
          g.private.start();
          var preference = g.private.data.preference !== undefined ?
                g.private.data.preference : {},
            coordinates = preference.coordinates;
          $.each(g.private.data.nodes, function (key, value) {
            if (coordinates === undefined || coordinates[key] === undefined) {
              value.coordinate = {
                'top': 0.0,
                'left': 0.0
              };
            } else {
              value.coordinate = coordinates[key];
            }
            value.id = key;
            g.private.newElement(value);
            if (value.data) { // backward compatibility
              g.private.updateElementData(key, {
                data: value.data
              });
            }
          });
          $.each(g.private.data.edges, function (key, value) {
            g.private.addEdge(key, value);
          });
          g.private.redraw();
        })
        .push(function () {
          // Infinite wait, until cancelled
          return new RSVP.defer().promise;
        })
        .push(undefined, function (error) {
          $(g.private.element).find("#main").html("");
          throw error;
        });
    });
}($, jsPlumb, console));
