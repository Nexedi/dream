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

/*global RSVP, rJS, $, jsPlumb, Handlebars,
  loopEventListener, promiseEventListener, DOMParser, confirm, console*/
/*jslint unparam: true todo: true */
(function (RSVP, rJS, $, jsPlumb, Handlebars,
           loopEventListener, promiseEventListener, DOMParser) {
  "use strict";
  
/* TODO:
 * use services
 * drop jquery ui dependency
 * less dependancies ( promise event listner ? )
 * document exposed css / jsplumb config
 * no more handlebars
 * accept ERP5 format
 * auto springy layout
 * drop zoom level
 * rename draggable()
 * allow changing node and edge class
 * factorize node & edge popup edition
 */

  /*jslint nomen: true */
  var gadget_klass = rJS(window),
    node_template_source = gadget_klass.__template_element
      .getElementById('node-template').innerHTML,
    node_template = Handlebars.compile(node_template_source),
    popup_edit_template = gadget_klass.__template_element
       .getElementById('popup-edit-template'),
    domParser = new DOMParser();

  function loopJsplumbBind(gadget, type, callback) {
    //////////////////////////
    // Infinite event listener (promise is never resolved)
    // eventListener is removed when promise is cancelled/rejected
    //////////////////////////
    var handle_event_callback,
      callback_promise,
      jsplumb_instance = gadget.props.jsplumb_instance;

    function cancelResolver() {
      if ((callback_promise !== undefined) &&
          (typeof callback_promise.cancel === "function")) {
        callback_promise.cancel();
      }
    }

    function canceller() {
      if (handle_event_callback !== undefined) {
        jsplumb_instance.unbind(type);
      }
      cancelResolver();
    }

    function resolver(resolve, reject) {

      handle_event_callback = function () {
        var args = arguments;
        cancelResolver();
        callback_promise = new RSVP.Queue()
          .push(function () {
            return callback.apply(jsplumb_instance, args);
          })
          .push(undefined, function (error) {
            if (!(error instanceof RSVP.CancellationError)) {
              canceller();
              reject(error);
            }
          });
      };

      jsplumb_instance.bind(type, handle_event_callback);
    }
    return new RSVP.Promise(resolver, canceller);
  }

  function getNodeId(gadget, element_id) {
    console.log("getNODEID 1");
    // returns the ID of the node in the graph from its DOM element id
    var node_id;
    $.each(gadget.props.node_id_to_dom_element_id, function (k, v) {
      if (v === element_id) {
        node_id = k;
        return false;
      }
    });
    return node_id;
  }

  function generateNodeId(gadget, element) {
    console.log("generateNODEID 1");
    // Generate a node id
    var n = 1,
      class_def = gadget.props.data.class_definition[element._class],
      id = class_def.allOf[1].properties.id.default || element._class;
    while (gadget.props.data.graph.node[id + n] !== undefined) {
      n += 1;
    }
    return id + n;
  }

  function generateDomElementId(gadget_element) {
    // Generate a probably unique DOM element ID.
    var n = 1;
    while ($(gadget_element).find('#DreamNode_' + n).length > 0) {
      n += 1;
    }
    return 'DreamNode_' + n;
  }

  function getDefaultEdgeClass(gadget){
    // TODO: use first edge class available in class_definition
    return 'Dream.Edge';
  }

  function updateConnectionData(gadget, connection, remove) {
    if (connection.ignoreEvent) {
      // this hack is for edge edition. Maybe there I missed one thing and
      // there is a better way.
      return;
    }
    if (remove) {
      delete gadget.props.data.graph.edge[connection.id];
      //delete gadget.props.data.graph.main_graph.node[connection.id];
    } else {
      var edge_data = gadget.props.data.graph.edge[connection.id] || {
        _class: getDefaultEdgeClass(gadget)
      };
      edge_data.source = getNodeId(gadget, connection.sourceId);
      edge_data.destination = getNodeId(gadget, connection.targetId);
      gadget.props.data.graph.edge[connection.id] = edge_data;
    }
    gadget.notifyDataChanged();
  }

  function convertToAbsolutePosition(gadget, x, y) {
    var zoom_level = gadget.props.zoom_level * 1.1111,
      canvas_size_x = $(gadget.props.main).width(),
      canvas_size_y = $(gadget.props.main).height(),
      size_x = $(gadget.props.element).find('.dummy_window').width() *
        zoom_level,
      size_y = $(gadget.props.element).find('.dummy_window').height() *
        zoom_level,
      top = Math.floor(y * (canvas_size_y - size_y)) + "px",
      left = Math.floor(x * (canvas_size_x - size_x)) + "px";
    return [left, top];
  }

  function convertToRelativePosition(gadget, x, y) {
    var zoom_level = gadget.props.zoom_level * 1.1111,
      canvas_size_x = $(gadget.props.main).width(),
      canvas_size_y = $(gadget.props.main).height(),
      size_x = $(gadget.props.element).find('.dummy_window').width() *
        zoom_level,
      size_y = $(gadget.props.element).find('.dummy_window').height() *
        zoom_level,
      top = Math.max(Math.min(y.replace('px', '') /
                              (canvas_size_y - size_y), 1), 0),
      left = Math.max(Math.min(x.replace('px', '') /
                               (canvas_size_x - size_x), 1), 0);
    return [left, top];
  }

  function updateElementCoordinate(gadget, node_id, coordinate) {
    console.log("updateELEMENTCOORDINATE 1");
    var element_id = gadget.props.node_id_to_dom_element_id[node_id],
      element,
      relative_position;

    if (coordinate === undefined) {
      element = $(gadget.props.element).find("#" + element_id);
      relative_position = convertToRelativePosition(
        gadget,
        element.css('left'),
        element.css('top')
      );
      coordinate = {
        left: relative_position[0],
        top: relative_position[1]
      };
    }

    gadget.props.data.graph.node[node_id].coordinate = coordinate;
    gadget.notifyDataChanged();
    return coordinate;
  }

  function draggable(gadget) {
    var jsplumb_instance = gadget.props.jsplumb_instance,
      stop = function (element) {
        updateElementCoordinate(gadget, getNodeId(gadget, element.target.id));
      };

    // XXX This function should only touch the node element that we just added.
    jsplumb_instance
      .draggable(jsplumb_instance.getSelector(".window"), {
        containment: 'parent',
        grid: [10, 10],
        stop: stop // FIXME: we should only accept if dropped in #main
      });

    jsplumb_instance
      .makeSource(jsplumb_instance.getSelector(".window"), {
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

    jsplumb_instance
      .makeTarget(jsplumb_instance.getSelector(".window"), {
        dropOptions: {
          hoverClass: "dragHover"
        },
        anchor: "Continuous"
      });
  }

  function updateNodeStyle(gadget, element_id, class_definition) {
    // Update node size according to the zoom level
    // XXX does nothing for now
    var zoom_level = gadget.props.zoom_level * 1.1111,
      element = $(gadget.props.element).find("#" + element_id),
      new_value;
    $.each(gadget.props.style_attr_list, function (i, j) {
      new_value = $(gadget.props.element).find('.dummy_window').css(j)
        .replace('px', '') * zoom_level + 'px';
      element.css(j, new_value);
    });
    Object.keys(class_definition.css || {}).forEach(function (k) {
      element.css(k, class_definition.css[k]);
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


  function removeElement(gadget, node_id) {
    console.log("removeELEMENT 1");
    var element_id = gadget.props.node_id_to_dom_element_id[node_id];
    gadget.props.jsplumb_instance.removeAllEndpoints(
      $(gadget.props.element).find("#" + element_id)
    );
    $(gadget.props.element).find("#" + element_id).remove();
    delete gadget.props.data.graph.node[node_id];
    delete gadget.props.node_id_to_dom_element_id[node_id];

    //$.each(gadget.props.data.graph.main_graph.node, function (k, v) {
    $.each(gadget.props.data.graph.edge, function (k, v) {
      if (node_id === v.source || node_id === v.destination) {
        delete gadget.props.data.graph.edge[k];
      }
    });

    gadget.notifyDataChanged();
    console.log("removeELEMENT 4");
  }

  function updateElementData(gadget, node_id, data) {
    console.log("updateELEMENTDATA 1");
    var element_id = gadget.props.node_id_to_dom_element_id[node_id],
      new_id = data.id;
    if (data.data.name) {
      $(gadget.props.element).find("#" + element_id).text(data.data.name)
        .attr("title", data.data.name)
        .append('<div class="ep"></div></div>');
      gadget.props.data.graph.node[node_id].name = data.data.name;
    }
    delete data.id;
    //$.extend(gadget.props.data.graph.main_graph.node[node_id], data.data);
    $.extend(gadget.props.data.graph.node[node_id], data.data);
    if (new_id && new_id !== node_id) {
      gadget.props.data.graph.node[new_id]
        = gadget.props.data.graph.node[node_id];
      delete gadget.props.data.graph.node[node_id];

      gadget.props.node_id_to_dom_element_id[new_id]
        = gadget.props.node_id_to_dom_element_id[node_id];
      delete gadget.props.node_id_to_dom_element_id[node_id];

      //delete gadget.props.data.graph.main_graph.node[new_id].id;
      //$.each(gadget.props.data.graph.main_graph.node, function (k, v) {
      delete gadget.props.data.graph.node[new_id].id;
      $.each(gadget.props.data.graph.edge, function (k, v) {
        if (v.source === node_id) {
          v.source = new_id;
        }
        if (v.destination === node_id) {
          v.destination = new_id;
        }
      });
    }
    console.log("updateELEMENTDATA 7");
    gadget.notifyDataChanged();
  }

  function addEdge(gadget, edge_id, edge_data) {
    var overlays = [],
      connection;

    if (edge_data.name) {
      overlays = [["Label", {
        cssClass: "l1 component label",
        label: edge_data.name
      }]];
    }

    if (gadget.props.data.graph.node[edge_data.source] === undefined) {
      throw new Error("Edge Source " + edge_data.source + " does not exist");
    }
    if (gadget.props.data.graph.node[edge_data.source] === undefined) {
      throw new Error("Edge Destination " + edge_data.source
        + " does not exist");
    }

    // If an edge has this data:
    // { _class: 'Edge', 
    //   source: 'N1',
    //   destination: 'N2',
    //   jsplumb_source_endpoint: 'BottomCenter',
    //   jsplumb_destination_endpoint: 'LeftMiddle',
    //   jsplumb_connector: 'Flowchart' }
    // Then it is rendered using a flowchart connector. The difficulty is that
    // jsplumb does not let you configure the connector type on the edge, but
    // on the source endpoint. One solution seem to create all types of
    // endpoints on nodes.
    if ( edge_data.jsplumb_connector === 'Flowchart' ) {
        connection = gadget.props.jsplumb_instance.connect({
            uuids: [edge_data.source + ".flowChart" +
                         edge_data.jsplumb_source_endpoint,
                    edge_data.destination + ".flowChart" +
                         edge_data.jsplumb_destination_endpoint],
            overlays: overlays
        });
    } else {    
      connection = gadget.props.jsplumb_instance.connect({
        source: gadget.props.node_id_to_dom_element_id[edge_data.source],
        target: gadget.props.node_id_to_dom_element_id[edge_data.destination],
        Connector: [ "Bezier", {curviness: 75} ],
        overlays: overlays
      });
    }

    // set data for 'connection' event that will be called "later"
    gadget.props.data.graph.edge[edge_id] = edge_data;

    // jsplumb assigned an id, but we are controlling ids ourselves.
    connection.id = edge_id;
  }

  /* function expandSchema(class_definition, full_schema) {
    // minimal expanding of json schema, supports merging allOf and $ref
    // references
    // TODO: check for a library that would provide full support
    var property, referenced, i, j, len,
      expanded_class_definition = {properties:
        class_definition.properties || {}},
      ref_word_list, ref_word, ref_definition_list,
      ref_definition_word, ref_definition_root, ref_definition,
      sub_ref_def, sub_ref_def_list,
      sub_ref_def_word, sub_ref_def_root, prop;
    console.log("expandSCHEMA 1");
    console.log(class_definition);
    console.log(full_schema);
    console.log(expanded_class_definition);
	
    if (class_definition.allOf) {
      for (i = 0; i < class_definition.allOf.length; i += 1) {
        referenced = class_definition.allOf[i];
        if (referenced.$ref) {
          ref_word_list = referenced.$ref.split("/");
          ref_word = ref_word_list[ref_word_list.length-1];
          referenced = expandSchema(
            full_schema.class_definition[ref_word],
            full_schema);
        }
        // console.log(full_schema.class_definition.definitions);
        if (referenced.properties) {
          console.log("[[[[[[[[[[]]]]]]]]]]");
          console.log(referenced.properties);
          for (property in referenced.properties) {
            if (referenced.properties.hasOwnProperty(property)) {
              if (referenced.properties[property].type || 
                  referenced.properties[property].$ref) {
                console.log("..");
                console.log(property);
                console.log(referenced.properties[property]);
                if (referenced.properties[property].$ref) {
                  ref_definition_list
                    = referenced.properties[property].$ref.split("/");
                  ref_definition_word
                    = ref_definition_list[ref_definition_list.length-1];
                  ref_definition
                    = full_schema.class_definition
                                 .definitions[ref_definition_word];
                  if (ref_definition.allOf) {
                    if (ref_definition.allOf[1].oneOf) {
                      len = ref_definition.allOf[1].oneOf.length - 1;
                      for (j = 0; j <= len; j += 1) {
                        if (ref_definition.allOf[1]
                                          .oneOf[j].$ref) {
                          sub_ref_def_list = ref_definition.allOf[1]
                                               .oneOf[j].$ref.split("/");
                          sub_ref_def_word
                            = sub_ref_def_list[sub_ref_def_list.length-1];
                          sub_ref_def_root
                            = sub_ref_def_list[sub_ref_def_list.length-2];
                          sub_ref_def = full_schema.class_definition
                            .definitions[sub_ref_def_root][sub_ref_def_word];
                          ref_definition.allOf[1].oneOf[j] = sub_ref_def;
                        }
                      }
                    }
                  }
                  expanded_class_definition.properties[property]
                    = ref_definition;
                  //console.log("for property " + property + ", definition:");
                  //console.log(ref_definition);
                } else {
                  if (referenced.properties[property].properties) {
                    console.log("not a reference");
                    console.log(referenced.properties[property].properties);
                    for (prop in referenced.properties[property]
                                           .properties) {
                      if (referenced.properties[property]
                                    .properties.hasOwnProperty(prop)) {
                        console.log(7);
                        console.log(prop);
                        console.log(referenced.properties[property]
                                    .properties[prop]);
                        if (referenced.properties[property]
                                      .properties[prop].$ref) {
                          console.log("!!!!");
                          ref_definition_list
                            = referenced.properties[property]
                                .properties[prop].$ref.split("/");
                          console.log(ref_definition_list);
                          ref_definition_word
                            = ref_definition_list[
                                ref_definition_list.length-1
                              ];
                          console.log(ref_definition_word);
                          ref_definition_root
                            = ref_definition_list[
                                ref_definition_list.length-2
                              ];
                          console.log(ref_definition_root);
                          ref_definition = full_schema
                            .class_definition[
                              ref_definition_root
                            ][ref_definition_word];
                          console.log(ref_definition);
                          if (ref_definition.allOf) {
                            if (ref_definition.allOf[1].oneOf) {
                              len = ref_definition.allOf[1].oneOf.length - 1;
                              for (j = 0; j <= len; j += 1) {
                                if (ref_definition.allOf[1]
                                             .oneOf[j].$ref) {
                                  sub_ref_def_list = ref_definition.allOf[1]
                                             .oneOf[j].$ref.split("/");
                                  sub_ref_def_word
                                    = sub_ref_def_list[
                                        sub_ref_def_list.length-1
                                      ];
                                  sub_ref_def_root
                                    = sub_ref_def_list[
                                        sub_ref_def_list.length-2
                                      ];
                                  sub_ref_def = full_schema.class_definition
                                    .definitions[
                                      sub_ref_def_root
                                    ][sub_ref_def_word];
                                  ref_definition.allOf[1].oneOf[j] 
                                    = sub_ref_def;
                                }
                              }
                            }
                          }
                          referenced.properties[property].properties[prop]
                            = ref_definition;
                        }
                      }
                    }
                  }
                  expanded_class_definition.properties[property]
                    = referenced.properties[property];
                }
              }
            }
          }
        }
      }
    }
    // console.log("expandSCHEMA 2");
    // console.log(expanded_class_definition);
    return expanded_class_definition;
  } */

  function expandOneOf(definition, fullSchema) {
    var j, len = definition.allOf[1].oneOf.length - 1,
      def_ref_list, def_ref_word,
	  def_ref_root, referenced_def;
    for (j = 0; j <= len; j += 1) {
      if (definition.allOf[1].oneOf[j].$ref) {
        def_ref_list = definition.allOf[1].oneOf[j].$ref.split("/");
        def_ref_word = def_ref_list[def_ref_list.length - 1];
        def_ref_root = def_ref_list[def_ref_list.length - 2];
        referenced_def
          = fullSchema.class_definition
                      .definitions[def_ref_root][def_ref_word];
        definition.allOf[1].oneOf[j] = referenced_def;
      }
    }
    return definition;
  }

  function expandReference(definition, fullSchema) {
    var  ref_definition_list
           = definition.$ref.split("/"),
         ref_definition_word
           = ref_definition_list[ref_definition_list.length - 1],
	     ref_definition_root
           = ref_definition_list[ref_definition_list.length - 2],
	     ref_definition = fullSchema
           .class_definition[ref_definition_root][ref_definition_word];
    console.log("expandingReference");
    if (ref_definition.allOf) {
      if (ref_definition.allOf[1].oneOf) {
        console.log("there is oneOf");
        ref_definition = expandOneOf(ref_definition, fullSchema);
      }
    }
    definition = ref_definition;
    console.log("* * *");
    console.log(definition);
    return definition;
  }

  function expandProperties(definition, expanded_class_def, fullSchema) {
    console.log("expanding properties");
    console.log(definition);
    var property, temp1, temp2, i, subProp, temp3;
    for (property in definition.properties) {
      if (definition.properties.hasOwnProperty(property)) {
        console.log("...");
        console.log(property);
        if (definition.properties[property].allOf
         || definition.properties[property].properties
         || definition.properties[property].type
         || definition.properties[property].$ref) {
          if (definition.properties[property].$ref) {
            temp1
              = expandReference(
                  definition.properties[property], fullSchema
                );
            console.log("there is a referenced property # #");
            console.log(property);
            expanded_class_def.properties[property]
              = temp1;
            if (temp1.allOf) {
              if (temp1.allOf[1].oneOf) {
                for (i = 0; i <= temp1.allOf[1].oneOf.length-1; i += 1) {
                  if (temp1.allOf[1].oneOf[i].properties) {
                    for (subProp in temp1.allOf[1].oneOf[i].properties) {
                      if (temp1.allOf[1].oneOf[i]
                               .properties.hasOwnProperty(subProp)) {
                        if (temp1.allOf[1].oneOf[i].properties[subProp].$ref) {
                          console.log("there is referenced sub-property");
                          console.log(subProp);
                          temp3
                            = expandReference(
                              temp1.allOf[1].oneOf[i].properties[subProp],
                              fullSchema
                            );
                          expanded_class_def.properties[property]
                            .allOf[1].oneOf[i].properties[subProp]
                            = temp3;
                        }
                      }
                    }
                  }
                }
              }
            }
          } else {
            if (definition.properties[property].properties) {
              console.log("there is a property property --> recursive");
              console.log(property);
              expanded_class_def.properties[property] = {properties: {}};
              temp2 = expandProperties(
                definition.properties[property],
                expanded_class_def.properties[property],
                fullSchema
              );
              definition.properties[property] = temp2;
            }
            console.log("before expanding definition");
            console.log(property);
            expanded_class_def.properties[property]
              = definition.properties[property];
          }
        }
      }
    }
    console.log("- * - * -");
    console.log(expanded_class_def);
    return expanded_class_def;
  }

  function expandSchema(class_definition, full_schema) {
    // minimal expanding of json schema, supports merging allOf and $ref
    // references
    // TODO: check for a library that would provide full support
    console.log("EXPANDING SCHEMA FOR :");
    console.log(class_definition);
    var referenced, i, 
      expanded_class_definition = {
        properties: class_definition.properties || {}
      }, 
      ref_word_list, ref_word;
    if (class_definition.allOf) {
      for (i = 0; i < class_definition.allOf.length; i += 1) {
        referenced = class_definition.allOf[i];
        if (referenced.$ref) {
          ref_word_list = referenced.$ref.split("/");
          ref_word = ref_word_list[ref_word_list.length - 1];
          console.log("# there is reference");
          referenced = expandSchema(
            full_schema.class_definition[ref_word],
            full_schema
          );
        }
        if (referenced.properties) {
          console.log("# there are properties");
          expanded_class_definition = expandProperties(
            referenced,
            expanded_class_definition,
            full_schema
          );
        }
      }
    }
    console.log("EXPANDED SCHEMA FOR : 2");
    console.log(expanded_class_definition);
    return expanded_class_definition;
  }

  function openEdgeEditionDialog(gadget, connection) {
    var edge_id = connection.id,
      edge_data = gadget.props.data.graph.edge[edge_id],
      edit_popup = $(gadget.props.element).find('#popup-edit-template'),
      schema,
      fieldset_element,
      delete_promise;

    schema = expandSchema(
      gadget.props.data.class_definition[edge_data._class],
      gadget.props.data
    );

    // We do not edit source & destination on edge this way.
    delete schema.properties.source;
    delete schema.properties.destination;

    gadget.props.element.appendChild(
      document.importNode(popup_edit_template.content, true).children[0]
    );
    edit_popup = $(gadget.props.element).find('#edit-popup');
    edit_popup.find('.node_class').text(connection._class);
    fieldset_element = edit_popup.find('fieldset')[0];
    edit_popup.popup();
    edit_popup.show();

    function save_promise(fieldset_gadget, edge_id) {
      return RSVP.Queue()
        .push(function () {
          return promiseEventListener(
            edit_popup.find("form")[0],
            'submit',
            false
          );
        })
        .push(function (evt) {
          var data = {
              "id": $(evt.target[1]).val(),
              "data": {}
          };
          return fieldset_gadget.getContent().then(function (r) {
            $.extend(data.data, gadget.props.data.graph.edge[connection.id]);
            $.extend(data.data, r);
            // to redraw, we remove the edge and add again.
            // but we want to disable events on connection, since event
            // handling promise are executed asynchronously in undefined order,
            // we cannot just remove and /then/ add, because the new edge is
            // added before the old is removed.
            connection.ignoreEvent = true;
            gadget.props.jsplumb_instance.detach(connection);

            addEdge(gadget, r.id, data.data);
          });
        });
    }

    delete_promise = new RSVP.Queue()
      .push(function () {
        return promiseEventListener(
          edit_popup.find("form [type='button']")[0],
          'click',
          false
        );
      })
      .push(function () {
        // connectionDetached event will remove the edge from data
        gadget.props.jsplumb_instance.detach(connection);
      });

    return gadget.declareGadget("../fieldset/index.html", {
      element: fieldset_element,
      scope: 'fieldset'
    })
      .push(function (fieldset_gadget) {
        return RSVP.all([fieldset_gadget,
                         fieldset_gadget.render({value: edge_data, 
                                          property_definition: schema},
                                          edge_id)]);
      })
      .push(function (fieldset_gadget) {
        edit_popup.enhanceWithin();
        edit_popup.popup('open');
        return fieldset_gadget[0];
      })
      .push(function (fieldset_gadget) {
        // Expose the dialog handling promise so that we can wait for it in
        // test.
        gadget.props.dialog_promise = RSVP.any([
          save_promise(fieldset_gadget, edge_id),
          delete_promise
        ]);
        return gadget.props.dialog_promise;
      })
      .push(function () {
        edit_popup.popup('close');
        edit_popup.remove();
        delete gadget.props.dialog_promise;
      });
  }

  function openNodeEditionDialog(gadget, element) {
    console.log("openNODEDIALOG 1");
    var node_id = getNodeId(gadget, element.id),
      node_data = gadget.props.data.graph.node[node_id],
      node_edit_popup = $(gadget.props.element).find('#popup-edit-template'),
      schema,
      fieldset_element,
      delete_promise;
    
    // If we have no definition for this, we do not allow edition.
    //TODO: node_data._class may not exist
    if ( gadget.props.data.class_definition[node_data._class] === undefined ) {
      return;
    }
    console.log("OPEN DIALOG FOR NODE");
    console.log(gadget.props);
    console.log(gadget.props.data.class_definition);
    console.log(node_data);
    schema = expandSchema(
      gadget.props.data.class_definition[node_data._class],
      gadget.props.data
    );
    console.log("----schema----");
    console.log(schema);
    console.log("----schema----");
    if (node_edit_popup.length !== 0) {
      node_edit_popup.remove();
    }

    gadget.props.element.appendChild(
      document.importNode(popup_edit_template.content, true).children[0]
    );
    node_edit_popup = $(gadget.props.element).find('#edit-popup');
    console.log("openNODEDIALOG 1.3");
    console.log(node_edit_popup);
    console.log(node_edit_popup.find(".node_class"));
    console.log(gadget.props.data.graph.node);
    console.log(node_data);
    console.log(node_edit_popup.find(".node_class").text(node_data._class));
    // Set the name of the popup to the node class
    node_edit_popup.find('.node_class').text(node_data._class);
    fieldset_element = node_edit_popup.find('fieldset')[0];
    node_edit_popup.popup();

    node_data.id = node_id; // XXX

    function save_promise(fieldset_gadget, node_id) {
      return RSVP.Queue()
        .push(function () {
          return promiseEventListener(
            node_edit_popup.find("form")[0],
            'submit',
            false
          );
        })
        .push(function (evt) {
          var data = {
              // XXX id should not be handled differently ...
              "id": $(evt.target[1]).val(),
              "data": {}
            };
          return fieldset_gadget.getContent().then(function (r) {
            console.log("******");
            console.log("******");
            console.log("******");
            console.log(r);
            console.log("******");
            console.log("******");
            console.log("******");
            $.extend(data.data, r);
            updateElementData(gadget, node_id, data);
          });
        });
    }

    console.log("openNODEDIALOG 3");
    delete_promise = new RSVP.Queue()
      .push(function () {
        return promiseEventListener(
          node_edit_popup.find("form [type='button']")[0],
          'click',
          false
        );
      })
      .push(function () {
        return removeElement(gadget, node_id);
      });

    console.log("openNODEDIALOG 4");
    return gadget.declareGadget("../fieldset/index.html", {
      element: fieldset_element,
      scope: 'fieldset'
    })
      .push(function (fieldset_gadget) {
        console.log("^^^^^^^^^^^^^^^^^^^");
        console.log("^^^^^^^^^^^^^^^^^^^");
        console.log("^^^^^^^^^^^^^^^^^^^");
        console.log(fieldset_gadget);
        console.log("^^^^^^^^^^^^^^^^^^^");
        console.log("^^^^^^^^^^^^^^^^^^^");
        console.log("^^^^^^^^^^^^^^^^^^^");
        return RSVP.all([fieldset_gadget,
                         fieldset_gadget.render({value: node_data, 
                                          property_definition: schema},
                                          node_id)]);
      })
      .push(function (fieldset_gadget) {
        console.log(fieldset_gadget[0]);
        return RSVP.Queue()
          .push(function () {
            console.log(fieldset_gadget[0]);
            fieldset_gadget[0].startService();
          })
          .push(function () {
            console.log(":::::::::::::::::::::::::::");
            console.log(fieldset_gadget);
            console.log(":::::::::::::::::::::::::::");
            node_edit_popup.enhanceWithin();
            node_edit_popup.popup('open');
            return fieldset_gadget[0];
          });
      })
      .push(function (fieldset_gadget) {
        // Expose the dialog handling promise so that we can wait for it in
        // test.
        console.log("=======:::::::::::::::::::=======");
        console.log(fieldset_gadget);
        console.log("=======:::::::::::::::::::=======");
        gadget.props.dialog_promise = RSVP.any([
          save_promise(fieldset_gadget, node_id),
          delete_promise
        ]);
        return gadget.props.dialog_promise;
      })
      .push(function () {
        node_edit_popup.popup('close');
        node_edit_popup.remove();
        delete gadget.props.dialog_promise;
      });
  }
  //function waitForNodeClick(gadget, node, config_dict) {
  function waitForNodeClick(gadget, node) {
    console.log("waitFORNODEclick 1");
    gadget.props.nodes_click_monitor
      .monitor(loopEventListener(
        node,
        'dblclick',
        false,
        openNodeEditionDialog.bind(null, gadget, node)
        //openNodeDialog.bind(null, gadget, node, config_dict)
      ));
  }

  function waitForConnection(gadget) {
    return loopJsplumbBind(gadget, 'connection',
                    function (info, originalEvent) {
        updateConnectionData(gadget, info.connection, false);
      });
  }

  function waitForConnectionDetached(gadget) {
    return loopJsplumbBind(gadget, 'connectionDetached',
                    function (info, originalEvent) {
        updateConnectionData(gadget, info.connection, true);
      });
  }

  function waitForConnectionClick(gadget) {
    return loopJsplumbBind(gadget, 'click', function (connection) {
      return openEdgeEditionDialog(gadget, connection);
    });
  }

  function addNode(gadget, node_id, node_data) {
    console.log("addNODE 0");
    var render_element = $(gadget.props.main),
      class_definition = gadget.props.data.class_definition[node_data._class],
      coordinate = node_data.coordinate,
      dom_element_id,
      box,
      absolute_position,
      domElement;

    dom_element_id = generateDomElementId(gadget.props.element);
    gadget.props.node_id_to_dom_element_id[node_id] = dom_element_id;

    node_data.name = node_data.name || class_definition.name;
    //gadget.props.data.graph.main_graph.node[node_id] = node_data;
    gadget.props.data.graph.node[node_id] = node_data;

    if (coordinate === undefined) {
      coordinate = {top: 0, left: 0};
    }

    node_data.coordinate = updateElementCoordinate(
      gadget,
      node_id,
      coordinate
    );

    // XXX make node template an option, or use CSS from class_definition
    /*jslint nomen: true*/
    domElement = domParser.parseFromString(
      node_template({
        "class": node_data._class.replace('.', '-'),
        "element_id": dom_element_id,
        "title": node_data.name || node_data.id,
        "name": node_data.name || node_data.id
      }),
      "text/html"
    ).querySelector('.window');
    render_element.append(domElement);
    waitForNodeClick(gadget, domElement);
    //waitForNodeClick(gadget, domElement, class_definition);

    box = $(gadget.props.element).find("#" + dom_element_id);
    absolute_position = convertToAbsolutePosition(
      gadget,
      coordinate.left,
      coordinate.top
    );
    box.css("top", absolute_position[1]);
    box.css("left", absolute_position[0]);
    updateNodeStyle(gadget, dom_element_id, class_definition);
    draggable(gadget); // XXX make only this element draggable.

    // Add some flowchart endpoints
    // TODO: add them all !
    gadget.props.jsplumb_instance.addEndpoint(dom_element_id, {
        isSource:true,
        maxConnections:-1,
        connector:[ "Flowchart", { stub:[40, 60],
                                   gap:10,
                                   cornerRadius:5,
                                   alwaysRespectStubs:true } ]
        }, { anchor: "BottomCenter",
            uuid: node_id + ".flowchartBottomCenter" });

    gadget.props.jsplumb_instance.addEndpoint(dom_element_id,
        { isTarget:true, maxConnections: -1 },
        { anchor: "LeftMiddle", uuid: node_id + ".flowChartLeftMiddle" });


    gadget.notifyDataChanged();
    console.log("addNODE 7");
  }

  function waitForDrop(gadget) {
    console.log("wait for DROP 1");
    var callback;
    function canceller() {
      console.log("wait for DROP canceler1");
      if (callback !== undefined) {
        console.log("wait for DROP canceller2");
        gadget.props.main.removeEventListener('drop', callback, false);
      }
    }
    /*jslint unparam: true*/
    function resolver(resolve, reject) {
      console.log("wait for DROP resolver1");
      callback = function (evt) {
        try {
          var class_name = JSON.parse(
              evt.dataTransfer.getData('application/json')
            ),
            offset = $(gadget.props.main).offset(),
            relative_position = convertToRelativePosition(
              gadget,
              evt.clientX - offset.left + "px",
              evt.clientY - offset.top + "px"
            );
          addNode(gadget,
            generateNodeId(gadget, {_class: class_name}),
            {
              coordinate: {
                left: relative_position[0],
                top: relative_position[1]
              },
              _class: class_name
            });
        } catch (e) {
          console.log("wait for DROP resolver100");
          reject(e);
        }
      };
      gadget.props.main.addEventListener('drop', callback, false);
    }
    console.log("wait for DROP 2");

    return new RSVP.all( [
      // loopEventListener adds an event listener that will prevent default for
      // dragover
      loopEventListener(gadget.props.main, 'dragover', false,
        function () {return undefined; }),
      RSVP.Promise(resolver, canceller) ]);
  }

  //initGadgetMixin(gadget_klass);
  gadget_klass
    .ready(function (g) {
      g.props = {};
      g.props.node_id_to_dom_element_id = {};
      g.props.zoom_level = 1.0;
      g.props.style_attr_list = [
        'width',
        'height',
        'padding-top',
        'line-height'
      ];
      g.getElement().then( function (element) {
        g.props.element = element;
      });
    })
    .declareAcquiredMethod('notifyDataChanged', 'notifyDataChanged')
    .declareMethod('render', function (data) {
      // var gadget = this;
      console.log("RENDEERING WORKFLOW EDITOR1");
      this.props.data = JSON.parse(data);
      this.props.jsplumb_instance = jsPlumb.getInstance();
      console.log("RENDEERING WORKFLOW EDITOR3");
      // XXX data loading is done in startService
      /*
      $.each(this.props.data.graph.node, function (key, value) {
        addNode(gadget, key, value);
      });
      $.each(this.props.data.graph.edge, function (key, value) {
        addEdge(gadget, key, value);
      });
      */
    })

    .declareMethod('getContent', function () {
      console.log("£££££££");
      console.log("£££££££");
      console.log("£££££££");
      console.log(this.props.data);
      console.log("£££££££");
      console.log("£££££££");
      console.log("£££££££");
      return JSON.stringify(this.props.data);
    })

    .declareMethod('startService', function () {
      console.log("startservice WORKFLOW EDITOR1");
      var gadget = this,
        jsplumb_instance = gadget.props.jsplumb_instance;
      this.props.main = this.props.element.querySelector('#main');

      jsplumb_instance.setRenderMode(jsplumb_instance.SVG);
      jsplumb_instance.importDefaults({
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
        Container: this.props.main
      });
      console.log("startservice WORKFLOW EDITOR2");
      draggable(gadget);

      this.props.nodes_click_monitor = RSVP.Monitor();

      // load the data
      $.each(this.props.data.graph.node, function (key, value) {
        addNode(gadget, key, value);
      });
      console.log("startservice WORKFLOW EDITOR3");
      $.each(this.props.data.graph.edge, function (key, value) {
        addEdge(gadget, key, value);
      });
      console.log("startservice WORKFLOW EDITOR4");
      return RSVP.all([
        waitForDrop(gadget),
        waitForConnection(gadget),
        waitForConnectionDetached(gadget),
        waitForConnectionClick(gadget),
        gadget.props.nodes_click_monitor
      ]);
    });

}(RSVP, rJS, $, jsPlumb, Handlebars, loopEventListener,
promiseEventListener, DOMParser));
