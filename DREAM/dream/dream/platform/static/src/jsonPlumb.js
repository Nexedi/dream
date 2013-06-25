(function (scope, $, jsPlumb, console, _) {
  "use strict";
  var jsonPlumb = function (model) {
    var that = {}, priv = {};

    priv.onError = function(error) {
       console.log("Error", error);
    };

    priv.initJsPlumb = function () {
      jsPlumb.setRenderMode(jsPlumb.SVG);
      jsPlumb.importDefaults({
        // default drag options
        DragOptions : { cursor: 'pointer', zIndex:2000 },
        EndpointStyles : [{ fillStyle:'#225588' }, { fillStyle:'#558822' }],
        PaintStyle : {strokeStyle:"#736AFF", lineWidth:2 },
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
        Anchor: "Continuous",
        Connector: ["StateMachine", { curviness:20 }],
      });     

      var init = function(connection) {
        connection.bind("editCompleted", function(o) {
        });
      };      
            
      // listen for new connections; initialise them the same way we initialise the connections at startup.
      jsPlumb.bind("jsPlumbConnection", function(connInfo, originalEvent) { 
        init(connInfo.connection);
      });     
            
      // listen for clicks on connections, and offer to change values on click.
      jsPlumb.bind("click", function(conn, originalEvent) {
        console.log("user click connection", conn);
        priv.dialog_connection = conn;
        $( "#dialog-form" ).dialog( "open" );
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
        console.log("updateConnectionData is being called");
        var source_element;
        source_element = priv.element_container[connection.sourceId];
        source_element.successorList = source_element.successorList || [];
        source_element.successorList.push(connection.targetId);
        priv.onDataChange();
      };

      // bind to connection/connectionDetached events, and update the list of connections on screen.
      jsPlumb.bind("connection", function(info, originalEvent) {
        updateConnectionData(info.connection);
      });
      jsPlumb.bind("connectionDetached", function(info, originalEvent) {
        updateConnectionData(info.connection, true);
      });
      priv.draggable();
    };

    priv.updateElementCoordinate = function(element_id, x, y) {
      var selection = priv.selection_container[element_id] || {};
      var coordinate = selection.coordinate || {};
      //var main_div_offset = $("#main").offset();
      //coordinate.x = x - main_div_offset.left;
      //coordinate.y = y - main_div_offset.top;
      coordinate.x = x;
      coordinate.y = y;
      console.log("jsonPlumb, updateElementCoordinate, selection", priv.selection_container);
      selection["coordinate"] = coordinate;
      priv.selection_container[element_id] = selection;
      priv.onDataChange();
      return coordinate;
    };

    priv.draggable = function() {
      // make all the window divs draggable
      var stop = function(el) {
        var element_id = el.target.id;
        priv.updateElementCoordinate(element_id, el.clientX, el.clientY);
      }
      jsPlumb.draggable(jsPlumb.getSelector(".window"), { grid: [20, 20] ,
                                                          stop: stop,
      });
    };
    priv.addElementToContainer = function(element, option) {
      // Now update the container of elements
      var element_data = {_class: element.class,
          id: element.id,
          name: element.id,
          option: option
      };
      priv.element_container[element.id] = element_data;
      priv.onDataChange();
    };

    priv.onDataChange = function() {
      $.publish("Dream.Gui.onDataChange", priv.getData());
    };

    priv.getData = function() {
      return {"element": priv.element_container, "selection": priv.selection_container};
    };

    priv.removeElement = function(element_id) {
      jsPlumb.removeAllEndpoints($("#" + element_id));
      $("#" + element_id).remove();
      delete(priv.element_container[element_id]);
      priv.onDataChange();
    };

    priv.initDialog = function(title, element_id) {
      // code to allow changing values on connections. For now we assume
      // that it is throughput. But we will need more generic code
      var throughput = $( "#throughput" ),
        allFields = $( [] ).add( throughput ),
        tips = $( ".validateTips" );
      $(function() {
        $( "input[type=submit]" )
          .button()
          .click(function( event ) {
            event.preventDefault();
          });
      });

      $( "#dialog-form" ).dialog({
        autoOpen: false,
        height: 300,
        width: 350,
        modal: true,
        title: title || "",
        buttons: {
          Cancel: function() {
            $( this ).dialog( "close" );
          },
          Delete: function() {
            console.log("Going to delete $(this)", $(this));
            priv.removeElement(element_id);
            $( this ).dialog( "close" );            
          },
          "Validate": function() {
            var bValid = true, i, i_length, box;
            allFields.removeClass( "ui-state-error" );
  
            bValid = bValid && checkRegexp( throughput, /^([0-9])+$/, "Througput must be integer." );
  
            if ( bValid ) {
              // Update the model with new value
              i_length = model.box_list.length;
              for (i = 0; i < i_length; i++) {
                box = model.box_list[i];
                if (box.id === priv.box_id) {
                  box.throughput = parseInt(throughput.val(), 10);
                }
              }
              priv.updateModel();
              $( this ).dialog( "close" );
            }
          },
        },
        close: function() {
          allFields.val( "" ).removeClass( "ui-state-error" );
        }
      });
    };

    Object.defineProperty(that, "start", {
      configurable: false,
      enumerable: false,
      writable: false,
      value: function () {
        priv.element_container = {};
        priv.selection_container = {};
        priv.initJsPlumb();
        priv.initDialog();
      }
    });

    Object.defineProperty(that, "removeElement", {
      configurable: false,
      enumerable: false,
      writable: false,
      value: function (element_id) {
        console.log("going to remove element", element_id);
        priv.removeElement(element_id);
      }
    });

    Object.defineProperty(that, "getData", {
      configurable: false,
      enumerable: false,
      writable: false,
      value: function () {
        return priv.getData();
      }
    });

    Object.defineProperty(that, "newElement", {
      configurable: false,
      enumerable: false,
      writable: false,
      value: function (element, option) {
        var render_element, style_string="", coordinate = {};
        render_element = $("[id=render]");
        if (element.coordinate !== undefined) {
          priv.updateElementCoordinate(element.id, element.coordinate.x, element.coordinate.y)
          var main_div_offset = $("#main").offset();
          coordinate.x = element.coordinate.x - main_div_offset.left;
          coordinate.y = element.coordinate.y - main_div_offset.top;

          _.each(coordinate, function(value, key, list) {
            if (key === "x") {
              key = "left";
            } else {
              key = "top";
            }
            style_string = style_string + key + ':' + value + 'px;';
          })
        }
        if (style_string.length > 0) {
          style_string = 'style="' + style_string + '"';
        }
        render_element.append('<div class="window" id="' +
                          element.id + '" ' + style_string + '">'
                          + element.id + '</div>');
        // Initial DEMO code : make all the window divs draggable
        priv.draggable();
        
        console.log("window selector", jsPlumb.getSelector(".window"));
        jsPlumb.getSelector("#" + element.id).bind('click', function() {
          console.log("bind click on window", $(this));
          //$("#dialog-form").attr("title", "bar");
          $( "#dialog-form" ).dialog( "destroy" ) ;
          priv.initDialog(element.id, element.id);
          $( "#dialog-form" ).dialog( "open" );
        });

        // Add endPoint to allow drawing connections
        var color = "#00f";
        var gradient_color = "#09098e";
        // Different endpoint color for Repairman
        if (element.class === "Dream.Repairman") {
          color = "rgb(189,11,11)";
          gradient_color = "rgb(255,0,0)";
        };
        var endpoint = {
          endpoint: "Rectangle",
          paintStyle:{ width:25, height:21, fillStyle:color },
          isSource:true,
          scope:"blue rectangle",
          connectorStyle : {
            gradient:{stops:[[0, color], [0.5, gradient_color], [1, color]]},
            lineWidth:5,
            strokeStyle:color,
            dashstyle:"2 2"
          },
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
        priv.addElementToContainer(element, option);
      }
    });

    return that;
  };

  var JsonPlumbNamespace = (function () {
    var that = {};

    /**
    * Creates a new dream instance.
    * @method newDream
    * @param  {object} model The model definition
    * @return {object} The new Dream instance.
    */
    Object.defineProperty(that, "newJsonPlumb", {
      configurable: false,
      enumerable: false,
      writable: false,
      value: function (model) {
        var instance = jsonPlumb(model);
        return instance;
      }
    });

    return that;
  })();

  Object.defineProperty(scope, "jsonPlumb", {
    configurable: false,
    enumerable: false,
    writable: false,
    value: JsonPlumbNamespace
  });

}(window, jQuery, jsPlumb, console, _));