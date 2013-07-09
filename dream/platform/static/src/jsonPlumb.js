/* ===========================================================================
 * Copyright 2013 Nexedi SARL and Contributors
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

(function (scope, $, jsPlumb, console, _) {
  "use strict";
  scope.jsonPlumb = function (model) {
    var that = {}, priv = {};

    priv.onError = function(error) {
       console.log("Error", error);
    };

    priv.initJsPlumb = function () {
      jsPlumb.setRenderMode(jsPlumb.SVG);
      var color = "#00f";
      var gradient_color = "#09098e";
      jsPlumb.importDefaults({
        // default drag options
        DragOptions : { cursor: 'pointer', zIndex:2000 },
        EndpointStyles : [{ fillStyle:'#225588' }, { fillStyle:'#558822' }],
        //PaintStyle : {strokeStyle:"#736AFF", lineWidth:2 },
        HoverPaintStyle : {strokeStyle:"#42a62c", lineWidth: 4},
        Endpoint : [ "Dot", {radius:2} ],
        ConnectionOverlays : [
          [ "Arrow", { 
            location:1,
            id:"arrow",
                      length:14,
                      foldback:0.8
          } ],
        ],
        PaintStyle : {
            gradient:{stops:[[0, color], [0.5, gradient_color], [1, color]]},
            lineWidth:5,
            strokeStyle:color,
          },
        Anchor: "Continuous",
        Connector: ["StateMachine", { curviness:20 }],
      });     

      // listen for clicks on connections, and offer to change values on click.
      jsPlumb.bind("click", function(conn) {
        console.log("user click connection", conn);
        //priv.dialog_connection = conn;
        jsPlumb.detach(conn);
      });

      jsPlumb.bind("beforeDetach", function(conn) {
        return confirm("Delete connection?");
      });
      
      jsPlumb.bind("connectionDrag", function(connection) {
        console.log("connection " + connection.id + " is being dragged");
      });   
      
      jsPlumb.bind("connectionDragStop", function(connection) {
        console.log("connection " + connection.id + " was dragged");
      });
      
      jsPlumb.makeTarget(jsPlumb.getSelector(".w"), {
        dropOptions:{ hoverClass:"dragHover" },
        anchor:"Continuous"
      });

      var updateConnectionData = function(connection, remove) {
        var source_element;
        source_element = priv.element_container[connection.sourceId];
        source_element.successorList = source_element.successorList || [];
        if (remove) {
          source_element.successorList.splice(source_element.successorList.indexOf(connection.targetId));
        } else {
          source_element.successorList.push(connection.targetId);
        }
        priv.onDataChange();
      };

      // bind to connection/connectionDetached events, and update the list of connections on screen.
      jsPlumb.bind("connection", function(info, originalEvent) {
        updateConnectionData(info.connection);
      });
      jsPlumb.bind("connectionDetached", function(info, originalEvent) {
        updateConnectionData(info.connection, true);
      });
      priv.onDataChange();
      priv.draggable();
    };

    priv.updateElementCoordinate = function(element_id, coordinate) {
      var preference = priv.preference_container[element_id] || {}, element;
      if (coordinate === undefined) {
        coordinate = {};
        element = $("#" + element_id);
        coordinate.top = element.css("top");
        coordinate.left = element.css("left");
      }
      preference["coordinate"] = coordinate;
      priv.preference_container[element_id] = preference;
      priv.onDataChange();
      return coordinate;
    };

    priv.draggable = function() {
      // make all the window divs draggable
      var stop = function(el) {
        var element_id = el.target.id;
        priv.updateElementCoordinate(element_id);
      }
      jsPlumb.draggable(jsPlumb.getSelector(".window"), { grid: [20, 20] ,
                                                          stop: stop,
      });
    };
    priv.addElementToContainer = function(element) {
      // Now update the container of elements
      var element_data = {_class: element._class,
          id: element.id,
          name: element.id,
      };
      priv.element_container[element.id] = element_data;
      priv.onDataChange();
    };

    priv.onDataChange = function() {
      $.publish("Dream.Gui.onDataChange", priv.getData());
    };

    priv.getData = function() {
      return { "element": priv.element_container,
               "preference": priv.preference_container,
               "general": priv.general_container };
    };

    priv.removeElement = function(element_id) {
      jsPlumb.removeAllEndpoints($("#" + element_id));
      $("#" + element_id).remove();
      delete(priv.element_container[element_id]);
      delete(priv.preference_container[element_id]);
      priv.onDataChange();
    };

    that.updateElementData = function (element_id, data) {
      _.extend(priv.element_container[element_id], data);
      priv.onDataChange();
    };

    that.start = function () {
      priv.element_container = {};
      priv.preference_container = {};
      priv.general_container = {};
      priv.initJsPlumb();
    };

    that.removeElement = function (element_id) {
      console.log("going to remove element", element_id);
      priv.removeElement(element_id);
    };

    that.getData = function () {
      return priv.getData();
    };

    that.clearAll = function () {
      $("[id=render]").children().remove()
      _.each(_.pairs(priv.element_container), function(element, index) {
        priv.removeElement(element[0]);
      });
    };

    that.connect = function (source_id, target_id) {
      jsPlumb.connect({source: source_id, target: target_id});
    };

    that.setGeneralProperties = function (properties) {
      priv.general_container = properties;
      priv.onDataChange();
    };

    that.newElement = function (element, option) {
      var render_element, style_string="", coordinate=element.coordinate,
          box;
      render_element = $("[id=render]");
      if (coordinate !== undefined) {
        coordinate = priv.updateElementCoordinate(element.id, coordinate)
      }
      render_element.append('<div class="window" id="' +
                        element.id + '">' + element.id + '</div>');
      box = $("#" + element.id);
      box.css("top", coordinate.top);
      box.css("left", coordinate.left);

      // Initial DEMO code : make all the window divs draggable
      priv.draggable();

      // Add endPoint to allow drawing connections
      var color = "#00f";
      var gradient_color = "#09098e";
      // Different endpoint color for Repairman
      if (element._class === "Dream.Repairman") {
        color = "rgb(189,11,11)";
        gradient_color = "rgb(255,0,0)";
      };
      var endpoint = {
        endpoint: "Rectangle",
        paintStyle:{ width:25, height:21, fillStyle:color },
        isSource:true,
        scope:"blue rectangle",
        /*connectorStyle : {
          gradient:{stops:[[0, color], [0.5, gradient_color], [1, color]]},
          lineWidth:5,
          strokeStyle:color,
          dashstyle:"2 2"
        },*/
        //connector: ["Bezier", { curviness:63 } ],
        maxConnections:3,
        isTarget:true,
        //dropOptions : exampleDropOptions
      };
      _.each(_.pairs(option.anchor), function(value, key, list) {
        var anchor = value[0],
            endpoint_configuration = value[1];
        jsPlumb.addEndpoint(element.id, { anchor: anchor }, endpoint);
      })
      priv.addElementToContainer(element);
    };

    return that;
  };

}(window, jQuery, jsPlumb, console, _));
