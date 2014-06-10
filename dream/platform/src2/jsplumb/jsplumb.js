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

(function ($, jsPlumb, console) {
  "use strict";
  
  var that = {}, priv = {}, gadget_element;
  
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
    while ($(gadget_element).find('#DreamNode_' + n).length > 0) {
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
  
  priv.updateElementCoordinate = function (node_id, coordinate) {
    var element_id = priv.node_container[node_id].element_id;
    var coordinates = priv.preference_container['coordinates'] || {}, element;
    if (coordinate === undefined) {
      coordinate = {};
      element = $(gadget_element).find("#" + element_id);
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
    var element = $(gadget_element).find("#" + element_id);
    console.log(gadget_element);
    $.each(priv.style_attr_list, function (i, j) {
      var new_value = $(gadget_element).find('.dummy_window').css(j).replace('px', '') * zoom_level + 'px';
      element.css(j, new_value);
    });
  };
  
  priv.convertToAbsolutePosition = function (x, y) {
    var zoom_level = (priv.preference_container['zoom_level'] || 1.0) * 1.1111;
    var canvas_size_x = $(gadget_element).find('#main').width();
    var canvas_size_y = $(gadget_element).find('#main').height();
    var size_x = $(gadget_element).find('.dummy_window').width() * zoom_level;
    var size_y = $(gadget_element).find('.dummy_window').height() * zoom_level;
    var top = Math.floor(y * (canvas_size_y - size_y)) + "px";
    var left = Math.floor(x * (canvas_size_x - size_x)) + "px";
    return [left, top];
  };
  
  that.convertToRelativePosition = function (x, y) {
    var zoom_level = (priv.preference_container['zoom_level'] || 1.0) * 1.1111;
    var canvas_size_x = $(gadget_element).find('#main').width();
    var canvas_size_y = $(gadget_element).find('#main').height();
    var size_x = $(gadget_element).find('.dummy_window').width() * zoom_level;
    var size_y = $(gadget_element).find('.dummy_window').height() * zoom_level;
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
    //$.publish("Dream.Gui.onDataChange", priv.getData());
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
      var new_value = $(gadget_element).find('.dummy_window').css(j).replace('px', '') * zoom_level + 'px';
      $(gadget_element).find('.window').css(j, new_value);
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
      var element = $(gadget_element).find('#' + that.getElementId(node_id));
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
    var wip_spreadsheet = $(gadget_element).find('#wip_spreadsheet');
    if (wip_spreadsheet.length > 0) {
      data['wip_spreadsheet'] = wip_spreadsheet.handsontable('getData');
    }
    var wip_part_spreadsheet = $(gadget_element).find('#wip_part_spreadsheet');
    if (wip_part_spreadsheet.length > 0) {
      data['wip_part_spreadsheet'] = wip_part_spreadsheet.handsontable('getData');
    }
    var shift_spreadsheet = $(gadget_element).find('#shift_spreadsheet');
    if (shift_spreadsheet.length > 0) {
      data['shift_spreadsheet'] = shift_spreadsheet.handsontable('getData');
    }
    return data;
  };
  
  priv.removeElement = function (node_id) {
    var element_id = priv.node_container[node_id].element_id;
    jsPlumb.removeAllEndpoints($(gadget_element).find("#" + element_id));
    $(gadget_element).find("#" + element_id).remove();
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
      $(gadget_element).find("#" + element_id).text(data["name"]).append('<div class="ep"></div></div>');
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
    $(gadget_element).find("#main").children().remove();
    priv.node_container = {};
    priv.edge_container = {};
    priv.preference_container = {};
    priv.general_container = {};
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
    render_element = $(gadget_element).find("#main");
    if (coordinate !== undefined) {
      coordinate = priv.updateElementCoordinate(element.id, coordinate);
    }
    render_element.append('<div class="window ' + element._class.replace('.', '-') + '" id="' +
                          element.element_id + '" title="' + (element.name || element.id) + '">' + element.id + '<div class="ep"></div></div>');
    box = $(gadget_element).find("#" + element.element_id);
    var absolute_position = priv.convertToAbsolutePosition(
      coordinate.left, coordinate.top);
    box.css("top", absolute_position[1]);
    box.css("left", absolute_position[0]);
    priv.updateNodeStyle(element.element_id);
    priv.draggable();
    priv.onDataChange();
  };
  
  window.data_sample = {
    "edges": {
      "con_10": [
        "CAD2", 
        "Decomposition", 
        {}
      ], 
      "con_15": [
        "Decomposition", 
        "QCAM", 
        {}
      ], 
      "con_20": [
        "QMILL", 
        "MILL2", 
        {}
      ], 
      "con_25": [
        "QMILL", 
        "MILL1", 
        {}
      ], 
      "con_30": [
        "QStart", 
        "CAD2", 
        {}
      ], 
      "con_35": [
        "QCAM", 
        "CAM1", 
        {}
      ], 
      "con_40": [
        "QCAM", 
        "CAM2", 
        {}
      ], 
      "con_45": [
        "QStart", 
        "CAD1", 
        {}
      ], 
      "con_5": [
        "CAD1", 
        "Decomposition", 
        {}
      ], 
      "con_50": [
        "QEDM", 
        "EDM", 
        {}
      ], 
      "con_55": [
        "QIM", 
        "IM1", 
        {}
      ], 
      "con_60": [
        "QIM", 
        "IM2", 
        {}
      ], 
      "con_65": [
        "MASS3", 
        "QIM", 
        {}
      ], 
      "con_70": [
        "MASS2", 
        "QIM", 
        {}
      ], 
      "con_75": [
        "MASS1", 
        "QIM", 
        {}
      ], 
      "con_80": [
        "QMASS", 
        "MASS1", 
        {}
      ], 
      "con_85": [
        "QMASS", 
        "MASS2", 
        {}
      ], 
      "con_90": [
        "QMASS", 
        "MASS3", 
        {}
      ]
    }, 
    "general": {
      "confidenceLevel": 0.95, 
      "currentDate": "2014/03/12", 
      "maxSimTime": -1, 
      "numberOfAntsPerGenerations": 2, 
      "numberOfGenerations": 10, 
      "numberOfReplications": 1, 
      "numberOfSolutions": 4, 
      "processTimeout": 2000, 
      "trace": "Yes"
    }, 
    "nodes": {
      "CAD1": {
        "_class": "Dream.MachineManagedJob", 
        "element_id": "DreamNode_1", 
        "failures": {
          "MTTF": 40, 
          "MTTR": 10, 
          "failureDistribution": "No", 
          "repairman": "None"
        }, 
        "name": "CAD1", 
        "operationType": "MT-Load-Processing", 
        "processingTime": {
          "distributionType": "Fixed", 
          "max": 1, 
          "mean": 0.9, 
          "min": 0.1, 
          "stdev": 0.1
        }
      }, 
      "CAD2": {
        "_class": "Dream.MachineManagedJob", 
        "element_id": "DreamNode_2", 
        "failures": {
          "MTTF": 40, 
          "MTTR": 10, 
          "failureDistribution": "No", 
          "repairman": "None"
        }, 
        "name": "CAD2", 
        "operationType": "MT-Load-Processing", 
        "processingTime": {
          "distributionType": "Fixed", 
          "max": 1, 
          "mean": 0.9, 
          "min": 0.1, 
          "stdev": 0.1
        }
      }, 
      "CAM1": {
        "_class": "Dream.MachineManagedJob", 
        "element_id": "DreamNode_3", 
        "failures": {
          "MTTF": 40, 
          "MTTR": 10, 
          "failureDistribution": "No", 
          "repairman": "None"
        }, 
        "name": "CAM1", 
        "operationType": "MT-Load-Processing", 
        "processingTime": {
          "distributionType": "Fixed", 
          "max": 1, 
          "mean": 0.9, 
          "min": 0.1, 
          "stdev": 0.1
        }
      }, 
      "CAM2": {
        "_class": "Dream.MachineManagedJob", 
        "element_id": "DreamNode_4", 
        "failures": {
          "MTTF": 40, 
          "MTTR": 10, 
          "failureDistribution": "No", 
          "repairman": "None"
        }, 
        "name": "CAM2", 
        "operationType": "MT-Load-Processing", 
        "processingTime": {
          "distributionType": "Fixed", 
          "max": 1, 
          "mean": 0.9, 
          "min": 0.1, 
          "stdev": 0.1
        }
      }, 
      "Decomposition": {
        "_class": "Dream.OrderDecomposition", 
        "element_id": "DreamNode_5", 
        "name": "Decomposition"
      }, 
      "E1": {
        "_class": "Dream.ExitJobShop", 
        "element_id": "DreamNode_6", 
        "name": "Exit"
      }, 
      "EDM": {
        "_class": "Dream.MachineManagedJob", 
        "element_id": "DreamNode_22", 
        "failures": {
          "MTTF": 40, 
          "MTTR": 10, 
          "failureDistribution": "No", 
          "repairman": "None"
        }, 
        "name": "EDM", 
        "operationType": "MT-Load-Setup", 
        "processingTime": {
          "distributionType": "Fixed", 
          "max": 1, 
          "mean": 0.9, 
          "min": 0.1, 
          "stdev": 0.1
        }
      }, 
      "IM1": {
        "_class": "Dream.MachineManagedJob", 
        "element_id": "DreamNode_7", 
        "failures": {
          "MTTF": 40, 
          "MTTR": 10, 
          "failureDistribution": "No", 
          "repairman": "None"
        }, 
        "name": "IM1", 
        "operationType": "MT-Load-Setup", 
        "processingTime": {
          "distributionType": "Fixed", 
          "max": 1, 
          "mean": 0.9, 
          "min": 0.1, 
          "stdev": 0.1
        }
      }, 
      "IM2": {
        "_class": "Dream.MachineManagedJob", 
        "element_id": "DreamNode_8", 
        "failures": {
          "MTTF": 40, 
          "MTTR": 10, 
          "failureDistribution": "No", 
          "repairman": "None"
        }, 
        "name": "IM2", 
        "operationType": "MT-Load-Setup", 
        "processingTime": {
          "distributionType": "Fixed", 
          "max": 1, 
          "mean": 0.9, 
          "min": 0.1, 
          "stdev": 0.1
        }
      }, 
      "MASS1": {
        "_class": "Dream.MouldAssembly", 
        "element_id": "DreamNode_9", 
        "failures": {
          "MTTF": 40, 
          "MTTR": 10, 
          "failureDistribution": "No", 
          "repairman": "None"
        }, 
        "name": "MASS1", 
        "operationType": "MT-Load-Processing", 
        "processingTime": {
          "distributionType": "Fixed", 
          "max": 1, 
          "mean": 0.9, 
          "min": 0.1, 
          "stdev": 0.1
        }
      }, 
      "MASS2": {
        "_class": "Dream.MouldAssembly", 
        "element_id": "DreamNode_10", 
        "failures": {
          "MTTF": 40, 
          "MTTR": 10, 
          "failureDistribution": "No", 
          "repairman": "None"
        }, 
        "name": "MASS2", 
        "operationType": "MT-Load-Processing", 
        "processingTime": {
          "distributionType": "Fixed", 
          "max": 1, 
          "mean": 0.9, 
          "min": 0.1, 
          "stdev": 0.1
        }
      }, 
      "MASS3": {
        "_class": "Dream.MouldAssembly", 
        "element_id": "DreamNode_11", 
        "failures": {
          "MTTF": 40, 
          "MTTR": 10, 
          "failureDistribution": "No", 
          "repairman": "None"
        }, 
        "name": "MASS3", 
        "operationType": "MT-Load-Processing", 
        "processingTime": {
          "distributionType": "Fixed", 
          "max": 1, 
          "mean": 0.9, 
          "min": 0.1, 
          "stdev": 0.1
        }
      }, 
      "MILL1": {
        "_class": "Dream.MachineManagedJob", 
        "element_id": "DreamNode_12", 
        "failures": {
          "MTTF": 40, 
          "MTTR": 10, 
          "failureDistribution": "No", 
          "repairman": "None"
        }, 
        "name": "MILL1", 
        "operationType": "MT-Load-Setup", 
        "processingTime": {
          "distributionType": "Fixed", 
          "max": 1, 
          "mean": 0.9, 
          "min": 0.1, 
          "stdev": 0.1
        }
      }, 
      "MILL2": {
        "_class": "Dream.MachineManagedJob", 
        "element_id": "DreamNode_13", 
        "failures": {
          "MTTF": 40, 
          "MTTR": 10, 
          "failureDistribution": "No", 
          "repairman": "None"
        }, 
        "name": "MILL2", 
        "operationType": "MT-Load-Setup", 
        "processingTime": {
          "distributionType": "Fixed", 
          "max": 1, 
          "mean": 0.9, 
          "min": 0.1, 
          "stdev": 0.1
        }
      }, 
      "PM1": {
        "_class": "Dream.OperatorManagedJob", 
        "element_id": "DreamNode_14", 
        "name": "PM1"
      }, 
      "PM2": {
        "_class": "Dream.OperatorManagedJob", 
        "element_id": "DreamNode_15", 
        "name": "PM2"
      }, 
      "QCAM": {
        "_class": "Dream.ConditionalBuffer", 
        "capacity": "1", 
        "element_id": "DreamNode_16", 
        "isDummy": "0", 
        "name": "QCAM", 
        "schedulingRule": "FIFO"
      }, 
      "QEDM": {
        "_class": "Dream.QueueManagedJob", 
        "capacity": "1", 
        "element_id": "DreamNode_17", 
        "isDummy": "0", 
        "name": "QEDM", 
        "schedulingRule": "FIFO"
      }, 
      "QIM": {
        "_class": "Dream.QueueManagedJob", 
        "capacity": -1, 
        "element_id": "DreamNode_18", 
        "isDummy": "0", 
        "name": "QIM", 
        "schedulingRule": "FIFO"
      }, 
      "QMASS": {
        "_class": "Dream.MouldAssemblyBuffer", 
        "capacity": -1, 
        "element_id": "DreamNode_19", 
        "isDummy": "0", 
        "name": "QMASS", 
        "schedulingRule": "FIFO"
      }, 
      "QMILL": {
        "_class": "Dream.QueueManagedJob", 
        "capacity": "-1", 
        "element_id": "DreamNode_20", 
        "isDummy": "0", 
        "name": "QMILL", 
        "schedulingRule": "FIFO"
      }, 
      "QStart": {
        "_class": "Dream.QueueManagedJob", 
        "capacity": "1", 
        "element_id": "DreamNode_21", 
        "isDummy": "0", 
        "name": "QStart", 
        "schedulingRule": "FIFO"
      }
    }, 
    "preference": {
      "coordinates": {
        "CAD1": {
          "left": 0.32935725427514356, 
          "top": 0.2673741799067207
        }, 
        "CAD2": {
          "left": 0.358715003959836, 
          "top": 0.02212751833710792
        }, 
        "CAM1": {
          "left": 0.8156850502215475, 
          "top": 0.03770447816866011
        }, 
        "CAM2": {
          "left": 0.796328960197283, 
          "top": 0.3079412968580852
        }, 
        "Decomposition": {
          "left": 0.5277238535086819, 
          "top": 0.10475955623433687
        }, 
        "E1": {
          "left": 0.967876137039781, 
          "top": 0.39355726466863505
        }, 
        "EDM": {
          "left": 0.18899051359520772, 
          "top": 0.92197993071283
        }, 
        "IM1": {
          "left": 0.8743104827972474, 
          "top": 0.6048188345476164
        }, 
        "IM2": {
          "left": 0.8845462397808385, 
          "top": 0.8560412718675537
        }, 
        "MASS1": {
          "left": 0.5486473277825593, 
          "top": 0.5247930837013548
        }, 
        "MASS2": {
          "left": 0.5441103624829352, 
          "top": 0.7115787006319392
        }, 
        "MASS3": {
          "left": 0.5495403769103371, 
          "top": 0.9090722116828504
        }, 
        "MILL1": {
          "left": 0.1877564659501795, 
          "top": 0.6841812972040019
        }, 
        "MILL2": {
          "left": 0.18401596464596484, 
          "top": 0.44453459509694726
        }, 
        "PM1": {
          "left": 0.001216264249816622, 
          "top": 0.021371774115389482
        }, 
        "PM2": {
          "left": 0.002151852134290946, 
          "top": 0.2275242854939252
        }, 
        "QCAM": {
          "left": 0.6798946482505993, 
          "top": 0.04336252204503648
        }, 
        "QEDM": {
          "left": 0.05041752133280548, 
          "top": 0.9193157852349616
        }, 
        "QIM": {
          "left": 0.7084640625588505, 
          "top": 0.7069073434280151
        }, 
        "QMASS": {
          "left": 0.39359833360679664, 
          "top": 0.7621221762426658
        }, 
        "QMILL": {
          "left": 0.024330940806924675, 
          "top": 0.571934442232598
        }, 
        "QStart": {
          "left": 0.15404040948036557, 
          "top": 0.05376099760119495
        }
      }, 
      "zoom_level": 0.8099919000000001
    }, 
    "shift_spreadsheet": [
      [
        "Day", 
        "Machines", 
        "Start", 
        "End"
      ], 
      [
        null, 
        null, 
        null, 
        null
      ]
    ], 
    "wip_part_spreadsheet": [
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
      ], 
      [
        "Order 1", 
        "2014/03/15", 
        "1", 
        "PM1", 
        "Design", 
        "Design", 
        "CAD", 
        "6", 
        null
      ], 
      [
        null, 
        null, 
        null, 
        null, 
        "Part1", 
        "Basic", 
        "CAM-MILL-EDM-MILL-MASS", 
        "8-4-2-8-0", 
        ""
      ], 
      [
        null, 
        null, 
        null, 
        null, 
        "Part2", 
        "Basic", 
        "CAM-MILL-EDM-MILL-EDM-MASS", 
        "10-7-8-4-13-8-0", 
        ""
      ], 
      [
        "", 
        "", 
        "", 
        "", 
        "Assemble", 
        "Mould", 
        "MASS-IM", 
        "2-12", 
        ""
      ], 
      [
        "Order 2", 
        "2014/03/14", 
        "1", 
        "PM1", 
        "Design", 
        "Design", 
        "CAD", 
        "6", 
        ""
      ], 
      [
        "", 
        "", 
        "", 
        "", 
        "Part1", 
        "Basic", 
        "CAM-MILL-EDM-MILL-MASS", 
        "8-4-2-8-0", 
        ""
      ], 
      [
        "", 
        "", 
        "", 
        "", 
        "Part2", 
        "Basic", 
        "CAM-MILL-EDM-MASS", 
        "20-15-8-8-0", 
        ""
      ], 
      [
        "", 
        "", 
        "", 
        "", 
        "Assemble", 
        "Mould", 
        "MASS-IM", 
        "1-12", 
        ""
      ], 
      [
        "Order 3", 
        "2014/03/15", 
        "1", 
        "PM1", 
        "Design", 
        "Design", 
        "CAD", 
        "6", 
        ""
      ], 
      [
        "", 
        "", 
        "", 
        "", 
        "Part1", 
        "Basic", 
        "CAM-MILL-EDM-MASS", 
        "8-4-2-0", 
        ""
      ], 
      [
        "", 
        "", 
        "", 
        "", 
        "Part2", 
        "Basic", 
        "CAM-MILL-EDM-MASS", 
        "7-15-8-8-0", 
        ""
      ], 
      [
        "", 
        "", 
        "", 
        "", 
        "Assemble", 
        "Mould", 
        "MASS-IM", 
        "1-3", 
        ""
      ], 
      [
        null, 
        null, 
        null, 
        null, 
        null, 
        null, 
        null, 
        null, 
        null
      ]
    ]
  };
  rJS(window)
  
    .ready(function (g) {
      window.g = g;
      return g.getElement(function (el) {
        gadget_element = el;
      });
    })
  
    .declareMethod('render', function (data) {
      this.data = JSON.parse(data);
    })
    
    .declareMethod('getData', function () {
      return "fake datas";
    })
  
    .declareMethod('startService', function () {
      var gadget = this;
      return this.getElement().push(function(element) {
        gadget_element = element;
        that.start();
        var preference = gadget.data.preference !== undefined ?
          gadget.data.preference : {},
        coordinates = preference['coordinates'];
        $.each(gadget.data.nodes, function (key, value) {
          if (coordinates === undefined || coordinates[key] === undefined) {
            value['coordinate'] = {
              'top': 0.0,
              'left': 0.0
            };
          } else {
            value['coordinate'] = coordinates[key];
          }
          value['id'] = key;
          that.newElement(value);
          if (value.data) { // backward compatibility
            that.updateElementData(key, {
              data: value.data
            });
          }
        });
        $.each(gadget.data.edges, function (key, value) {
          that.addEdge(key, value);
        });
        that.redraw();
      }).push(function() {
        // Infinite wait, until cancelled
        return new RSVP.defer().promise;
      }).push(undefined, function(error) {
        $(gadget_element).find("#main").html("");
        throw error;
      });
    })
}(jQuery, jsPlumb, console));
