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
/*global RSVP, rJS, $, jsPlumb, Handlebars*/
/*jslint unparam: true */
(function(RSVP, rJS, $, jsPlumb, Handlebars) {
    "use strict";
    /*jslint nomen: true*/
    var gadget_klass = rJS(window), node_template_source = gadget_klass.__template_element.getElementById("node-template").innerHTML, node_template = Handlebars.compile(node_template_source);
    function getNodeId(node_container, element_id) {
        var node_id;
        $.each(node_container, function(k, v) {
            if (v.element_id === element_id) {
                node_id = k;
                return false;
            }
        });
        return node_id;
    }
    function getElementId(node_container, node_id) {
        return node_container[node_id].element_id;
    }
    // function generateNodeId(node_container, element_type, option) {
    //   var n = 1;
    //   while (node_container[
    //       ((option.short_id || element_type) + n)
    //     ] !== undefined) {
    //     n += 1;
    //   }
    //   return (option.short_id || element_type) + n;
    // }
    // function generateElementId(gadget_element) {
    //   var n = 1;
    //   while ($(gadget_element).find('#DreamNode_' + n).length > 0) {
    //     n += 1;
    //   }
    //   return 'DreamNode_' + n;
    // }
    function onDataChange() {
        //$.publish("Dream.Gui.onDataChange", g.private.getData());
        return undefined;
    }
    function convertToAbsolutePosition(gadget, x, y) {
        var zoom_level = (gadget.private.preference_container.zoom_level || 1) * 1.1111, canvas_size_x = $(gadget.private.element).find("#main").width(), canvas_size_y = $(gadget.private.element).find("#main").height(), size_x = $(gadget.private.element).find(".dummy_window").width() * zoom_level, size_y = $(gadget.private.element).find(".dummy_window").height() * zoom_level, top = Math.floor(y * (canvas_size_y - size_y)) + "px", left = Math.floor(x * (canvas_size_x - size_x)) + "px";
        return [ left, top ];
    }
    function convertToRelativePosition(gadget, x, y) {
        var zoom_level = (gadget.private.preference_container.zoom_level || 1) * 1.1111, canvas_size_x = $(gadget.private.element).find("#main").width(), canvas_size_y = $(gadget.private.element).find("#main").height(), size_x = $(gadget.private.element).find(".dummy_window").width() * zoom_level, size_y = $(gadget.private.element).find(".dummy_window").height() * zoom_level, top = Math.max(Math.min(y.replace("px", "") / (canvas_size_y - size_y), 1), 0), left = Math.max(Math.min(x.replace("px", "") / (canvas_size_x - size_x), 1), 0);
        return [ left, top ];
    }
    function updateElementCoordinate(gadget, node_id, coordinate) {
        var element_id = gadget.private.node_container[node_id].element_id, coordinates = gadget.private.preference_container.coordinates || {}, element, relative_position;
        if (coordinate === undefined) {
            coordinate = {};
            element = $(gadget.private.element).find("#" + element_id);
            relative_position = convertToRelativePosition(gadget, element.css("left"), element.css("top"));
            coordinate.top = relative_position[1];
            coordinate.left = relative_position[0];
        }
        coordinates[node_id] = coordinate;
        gadget.private.preference_container.coordinates = coordinates;
        onDataChange();
        return coordinate;
    }
    function draggable(gadget) {
        var jsplumb_instance = gadget.private.jsplumb_instance, stop = function(element) {
            updateElementCoordinate(gadget, getNodeId(gadget.private.node_container, element.target.id));
        };
        jsplumb_instance.draggable(jsplumb_instance.getSelector(".window"), {
            containment: "parent",
            grid: [ 10, 10 ],
            stop: stop
        });
        jsplumb_instance.makeSource(jsplumb_instance.getSelector(".window"), {
            filter: ".ep",
            anchor: "Continuous",
            connector: [ "StateMachine", {
                curviness: 20
            } ],
            connectorStyle: {
                strokeStyle: "#5c96bc",
                lineWidth: 2,
                outlineColor: "transparent",
                outlineWidth: 4
            }
        });
        jsplumb_instance.makeTarget(jsplumb_instance.getSelector(".window"), {
            dropOptions: {
                hoverClass: "dragHover"
            },
            anchor: "Continuous"
        });
    }
    function initJsPlumb(gadget) {
        var jsplumb_instance = gadget.private.jsplumb_instance;
        jsplumb_instance.setRenderMode(jsplumb_instance.SVG);
        jsplumb_instance.importDefaults({
            HoverPaintStyle: {
                strokeStyle: "#1e8151",
                lineWidth: 2
            },
            Endpoint: [ "Dot", {
                radius: 2
            } ],
            ConnectionOverlays: [ [ "Arrow", {
                location: 1,
                id: "arrow",
                length: 14,
                foldback: .8
            } ] ],
            Container: "main"
        });
        // listen for clicks on connections,
        // and offer to change values on click.
        // jsplumb_instance.bind("click", function (conn) {
        //   jsplumb_instance.detach(conn);
        // });
        // jsplumb_instance.bind("beforeDetach", function (conn) {
        //   return confirm("Delete connection?");
        // });
        // jsplumb_instance
        //   .bind("connectionDrag", function (connection) {
        //     return undefined;
        //   });
        // jsplumb_instance
        //   .bind("connectionDragStop", function (connection) {
        //     return undefined;
        //   });
        // split in 2 methods ? one for events one for manip
        gadget.private.updateConnectionData = function(connection, remove, edge_data) {
            if (remove) {
                delete gadget.private.edge_container[connection.id];
            } else {
                gadget.private.edge_container[connection.id] = [ getNodeId(gadget.private.node_container, connection.sourceId), getNodeId(gadget.private.node_container, connection.targetId), edge_data || {} ];
            }
            onDataChange();
        };
        // bind to connection/connectionDetached events,
        // and update the list of connections on screen.
        // jsplumb_instance
        //   .bind("connection", function (info, originalEvent) {
        //     gadget.private.updateConnectionData(info.connection);
        //   });
        // jsplumb_instance
        //   .bind("connectionDetached", function (info, originalEvent) {
        //     gadget.private.updateConnectionData(info.connection, true);
        //   });
        onDataChange();
        draggable(gadget);
    }
    function updateNodeStyle(gadget, element_id) {
        var zoom_level = (gadget.private.preference_container.zoom_level || 1) * 1.1111, element = $(gadget.private.element).find("#" + element_id), new_value;
        $.each(gadget.private.style_attr_list, function(i, j) {
            new_value = $(gadget.private.element).find(".dummy_window").css(j).replace("px", "") * zoom_level + "px";
            element.css(j, new_value);
        });
    }
    function addElementToContainer(node_container, element) {
        // Now update the container of elements
        /*jslint nomen: true*/
        var element_data = {
            _class: element._class,
            element_id: element.element_id
        };
        node_container[element.id] = element_data;
    }
    function redraw(gadget) {
        var coordinates = gadget.private.preference_container.coordinates || {}, absolute_position, element;
        $.each(coordinates, function(node_id, v) {
            absolute_position = convertToAbsolutePosition(gadget, v.left, v.top);
            element = $(gadget.private.element).find("#" + getElementId(gadget.private.node_container, node_id));
            element.css("top", absolute_position[1]);
            element.css("left", absolute_position[0]);
            gadget.private.jsplumb_instance.repaint(element);
        });
    }
    // function positionGraph(gadget) {
    //   $.ajax(
    //     '/positionGraph',
    //     {
    //       data: JSON.stringify(getData()),
    //       contentType: 'application/json',
    //       type: 'POST',
    //       success: function (data, textStatus, jqXHR) {
    //         $.each(data, function (node, pos) {
    //           convertToAbsolutePosition(
    //             gadget,
    //             pos.left,
    //             pos.top
    //           );
    //           updateElementCoordinate(gadget, node, {
    //             top: pos.top,
    //             left: pos.left
    //           });
    //         });
    //         redraw(gadget);
    //       }
    //     }
    //   );
    // }
    // function setZoom(gadget, zoom_level) {
    //   $.each(gadget.private.style_attr_list, function (i, j) {
    //     var new_value = $(gadget.private.element).find('.dummy_window')
    //       .css(j).replace('px', '') * zoom_level + 'px';
    //     $(gadget.private.element).find('.window').css(j, new_value);
    //   });
    // }
    // function zoom_in(gadget) {
    // var zoom_level = (gadget.private.preference_container.zoom_level || 1.0) *
    //       1.1111;
    //   setZoom(gadget, zoom_level);
    //   gadget.private.preference_container.zoom_level = zoom_level;
    //   onDataChange();
    //   redraw(gadget);
    // }
    // function zoom_out(gadget) {
    // var zoom_level = (gadget.private.preference_container.zoom_level || 1.0) *
    //     0.9;
    //   setZoom(gadget, zoom_level);
    //   gadget.private.preference_container.zoom_level = zoom_level;
    //   onDataChange();
    //   redraw(gadget);
    // }
    // function removeElement(gadget, node_id) {
    //   var element_id = gadget.private.node_container[node_id].element_id;
    //   gadget.private.jsplumb_instance.removeAllEndpoints(
    //     $(gadget.private.element).find("#" + element_id)
    //   );
    //   $(gadget.private.element).find("#" + element_id).remove();
    //   delete gadget.private.node_container[node_id];
    //   delete gadget.private.preference_container.coordinates[node_id];
    //   $.each(gadget.private.edge_container, function (k, v) {
    //     if (node_id === v[0] || node_id === v[1]) {
    //       delete gadget.private.edge_container[k];
    //     }
    //   });
    //   onDataChange();
    // }
    function updateElementData(gadget, node_id, data) {
        var element_id = gadget.private.node_container[node_id].element_id, new_id = data.id;
        if (data.name) {
            $(gadget.private.element).find("#" + element_id).text(data.name).append('<div class="ep"></div></div>');
            gadget.private.node_container[node_id].name = data.name;
        }
        delete data.id;
        $.extend(gadget.private.node_container[node_id], data.data);
        if (new_id && new_id !== node_id) {
            gadget.private.node_container[new_id] = gadget.private.node_container[node_id];
            delete gadget.private.node_container[node_id];
            $.each(gadget.private.edge_container, function(k, v) {
                if (v[0] === node_id) {
                    v[0] = new_id;
                }
                if (v[1] === node_id) {
                    v[1] = new_id;
                }
            });
            gadget.private.preference_container.coordinates[new_id] = gadget.private.preference_container.coordinates[node_id];
            delete gadget.private.preference_container.coordinates[node_id];
        }
        onDataChange();
    }
    // function clearAll(gadget) {
    //   $.each(gadget.private.node_container, function (node_id) {
    //     removeElement(gadget, node_id);
    //   });
    //   // delete anything if still remains
    //   $(gadget.private.element).find("#main").children().remove();
    //   gadget.private.node_container = {};
    //   gadget.private.edge_container = {};
    //   gadget.private.preference_container = {};
    //   gadget.private.general_container = {};
    //   gadget.private.initGeneralProperties();
    //   gadget.private.prepareDialogForGeneralProperties();
    // }
    function addEdge(gadget, edge_id, edge_data) {
        var source_id = edge_data[0], target_id = edge_data[1], data = edge_data[2], overlays = [], connection;
        if (data && data.title) {
            overlays = [ [ "Label", {
                cssClass: "l1 component label",
                label: data.title
            } ] ];
        }
        connection = gadget.private.jsplumb_instance.connect({
            source: getElementId(gadget.private.node_container, source_id),
            target: getElementId(gadget.private.node_container, target_id),
            Connector: [ "Bezier", {
                curviness: 75
            } ],
            overlays: overlays
        });
        // call again updateConnectionData to set the connection data that
        // was not passed to the connection hook
        gadget.private.updateConnectionData(connection, 0, data);
    }
    // function setPreferences(gadget, preferences) {
    //   gadget.private.preference_container = preferences;
    //   var zoom_level = gadget.private.preference_container.zoom_level || 1.0;
    //   setZoom(gadget, zoom_level);
    // }
    // function setGeneralProperties(gadget, properties) {
    //   gadget.private.general_container = properties;
    //   onDataChange();
    // }
    // function updateGeneralProperties(gadget, properties) {
    //   $.extend(gadget.private.general_container, properties);
    //   onDataChange();
    // }
    function newElement(gadget, element, option) {
        element.name = element.name || option.name;
        addElementToContainer(gadget.private.node_container, element);
        var render_element = $(gadget.private.element).find("#main"), coordinate = element.coordinate, box, absolute_position;
        if (coordinate !== undefined) {
            coordinate = updateElementCoordinate(gadget, element.id, coordinate);
        }
        /*jslint nomen: true*/
        render_element.append(node_template({
            "class": element._class.replace(".", "-"),
            element_id: element.element_id,
            title: element.name || element.id,
            id: element.id
        }));
        box = $(gadget.private.element).find("#" + element.element_id);
        absolute_position = convertToAbsolutePosition(gadget, coordinate.left, coordinate.top);
        box.css("top", absolute_position[1]);
        box.css("left", absolute_position[0]);
        updateNodeStyle(gadget, element.element_id);
        draggable(gadget);
        onDataChange();
    }
    gadget_klass.ready(function(g) {
        g.private = {
            node_container: {},
            edge_container: {},
            preference_container: {},
            style_attr_list: [ "width", "height", "padding-top", "line-height" ]
        };
    }).declareMethod("render", function(data) {
        this.private.data = JSON.parse(data);
        this.private.jsplumb_instance = jsPlumb.getInstance();
    }).declareMethod("getData", function() {
        return JSON.stringify({
            nodes: this.private.node_container,
            edges: this.private.edge_container,
            preference: this.private.preference_container
        });
    }).declareMethod("startService", function() {
        var gadget = this, preference = gadget.private.data.preference !== undefined ? gadget.private.data.preference : {}, coordinates = preference.coordinates;
        return gadget.getElement().then(function(el) {
            gadget.private.element = el;
            initJsPlumb(gadget);
            $.each(gadget.private.data.nodes, function(key, value) {
                if (coordinates === undefined || coordinates[key] === undefined) {
                    value.coordinate = {
                        top: 0,
                        left: 0
                    };
                } else {
                    value.coordinate = coordinates[key];
                }
                value.id = key;
                newElement(gadget, value);
                if (value.data) {
                    // backward compatibility
                    updateElementData(gadget, key, {
                        data: value.data
                    });
                }
            });
            $.each(gadget.private.data.edges, function(key, value) {
                addEdge(gadget, key, value);
            });
            redraw(gadget);
        });
    });
})(RSVP, rJS, $, jsPlumb, Handlebars);