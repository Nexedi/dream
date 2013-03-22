(function (scope, $, jsPlumb, console, _) {
  "use strict";
  var dream = function (model) {
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
        HoverPaintStyle : {strokeStyle:"#42a62c", lineWidth:2 },
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
            
      // make all the window divs draggable           
      jsPlumb.draggable(jsPlumb.getSelector(".window"), { grid: [20, 20] });

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
    };

    priv.initDialog = function() {
      // code to allow changing values on connections. For now we assume
      // that it is throughput. But we will need more generic code
      var throughput = $( "#throughput" ),
        allFields = $( [] ).add( throughput ),
        tips = $( ".validateTips" );

      function updateTips( t ) {
        tips
          .text( t )
          .addClass( "ui-state-highlight" );
        setTimeout(function() {
          tips.removeClass( "ui-state-highlight", 1500 );
        }, 500 );
      }

      function checkLength( o, n, min, max ) {
        if ( o.val().length > max || o.val().length < min ) {
          o.addClass( "ui-state-error" );
          updateTips( "Length of " + n + " must be between " +
            min + " and " + max + "." );
          return false;
        } else {
          return true;
        }
      }

      function checkRegexp( o, regexp, n ) {
        if ( !( regexp.test( o.val() ) ) ) {
          o.addClass( "ui-state-error" );
          updateTips( n );
          return false;
        } else {
          return true;
        }
      }    

      $( "#dialog-form" ).dialog({
        autoOpen: false,
        height: 300,
        width: 350,
        modal: true,
        buttons: {
          "Validate": function() {
            var bValid = true, i, i_length, box;
            allFields.removeClass( "ui-state-error" );
  
            console.log("going to check troughput val", throughput.val());
            bValid = bValid && checkRegexp( throughput, /^([0-9])+$/, "Througput must be integer." );
  
            if ( bValid ) {
              console.log("new value is ok...", throughput.val());
              console.log("dialog_connection", priv.dialog_connection);
              // Update the model with new value
              i_length = model.box_list.length;
              for (i = 0; i < i_length; i++) {
                box = model.box_list[i];
                if (box.id === priv.dialog_connection.sourceId) {
                  box.throughput = parseInt(throughput.val(), 10);
                }
              }
              priv.setModel();
              $( this ).dialog( "close" );
            }
          },
          Cancel: function() {
            $( this ).dialog( "close" );
          }
        },
        close: function() {
          allFields.val( "" ).removeClass( "ui-state-error" );
        }
      });
    };

    priv.displayGraph = function () {
      var render_element, i, i_length, box, style_string, j, j_length, line;
      // Add boxes in the render div
      render_element = $("[id=render]");
      i_length = model.box_list.length;
      for (i=0; i < i_length; i++) {
        box = model.box_list[i];
        style_string = ""
        if (box.coordinate !== undefined) {
          _.each(box.coordinate, function(value, key, list) {
            style_string = style_string + key + ':' + value + 'em;';
          })
        }
        if (box.style !== undefined) {
          _.each(box.style, function(value, key, list) {
            style_string = style_string + key + ':' + value + ';';
          })
        }
        if (style_string.length > 0) {
          style_string = 'style="' + style_string + '"';
        }
        render_element.append('<div class="window" id="' +
                          box.id + '" ' + style_string + '">'
                          + '</div>');
      }

      // Now that we have all boxes, connect them
      for (i=0; i < i_length; i++) {
        box = model.box_list[i];
        if (box.target_list !== undefined) {
          j_length = box.target_list.length;
          for (j=0; j < j_length; j++) {
            console.log("in dream, jsPlumb.connect", box.id, box.target_list[j]);
            line = jsPlumb.connect({source:box.id, target: box.target_list[j],
                                   labelStyle : { cssClass:"component label" }});
            //, label: box.throughput.toString()});
            // Example to change line color
            // line.setPaintStyle({strokeStyle:"#42a62c", lineWidth:2 });
          }
        }
      }

      // Initial DEMO code : make all the window divs draggable
      jsPlumb.draggable(jsPlumb.getSelector(".window"), { grid: [20, 20] });

    };

    priv.setSimulationParameters = function (simulation_parameters) {
      $.ajax({
        url: "http://localhost:5000/setSimulationParameters",
        type: 'POST',
        data: JSON.stringify(simulation_parameters),
        contentType: "application/json",
        success: function(response) {
          console.log("got json response",response);
        },
        error: function(xhr, textStatus, error) {
          priv.onError(error);
        }
      });
    };

    // Utility function to update the style of a box
    priv.updateBoxStyle = function (box_id, style) {
      var box;
      box = $("#" + box_id);
      _.each(style, function(value, key, list) {
        box.css(key, value);
      })
    };

    // Utility function to update the content of the box
    priv.updateBoxContent = function (box_id, title, worker) {
      var box, html_string;
      box = $("#" + box_id);
      html_string = "<strong>" + title + "</strong>";
      if (worker !== undefined && worker !== null) {
        html_string += "<br> (" + worker + ")";
      }
      box.html(html_string);
    };

    priv.getModel = function (success) {
      $.ajax({
        url: "http://localhost:5000/getModel",
        type: 'GET',
        success: success,
        error: function(xhr, textStatus, error) {
          priv.onError(error);
        }
      });
    };

    priv.setModel = function () {
      // Now communicate our model to the simulation server
      $.ajax({
        url: "http://localhost:5000/setModel",
        type: 'POST',
        data: JSON.stringify(model),
        contentType: "application/json",
        success: function(response) {
          console.log("got json response",response);
        },
        error: function(xhr, textStatus, error) {
          priv.onError(error);
        }
      });
    };

    priv.updateConnectionLabel = function (source_id, target_id, title) {
      var connection_array, i, i_length, connection;
      connection_array = jsPlumb.getConnections({source: source_id, target: target_id});
      i_length = connection_array.length;
      for (i = 0; i < i_length; i++) {
        connection = connection_array[i];
        if (connection.getLabel() !== title) {
          connection.setLabel(title);
        }
      }
    };

    priv.updateModel = function (success) {
      var refreshGraph = function(model) {
        //console.log("model", model);
        var i, i_length, box;
        //console.log("before i_length");
        //console.log("model", model);
        //console.log(typeof(model));
        //console.log("model.box_list", model["box_list"]);
        i_length = model.box_list.length;
        //console.log("after i_length");
        //console.log("model", model);
        for (i = 0; i < i_length; i++) {
          //, style: {"background-color":"#FF0000"}
          box = model.box_list[i];
          if (box.enabled) {
            priv.updateBoxStyle(box.id, {"background-color": "#5EFB6E"});
          } else {
            priv.updateBoxStyle(box.id, {"background-color": "#FF0000"});
          }
          // Update content of the box
          priv.updateBoxContent(box.id, box.title, box.worker);
          // Update the label
          if (box.target_list !== undefined) {
            priv.updateConnectionLabel(box.id, box.target_list[0], box.throughput.toString());
          };
        }
        // Refresh total throughput value
        $("#total_throughput h2").text(model.throughput.toString());
      };
      priv.getModel(refreshGraph);
    };

    priv.updateModelRegularly = function () {
      var updateRegularly = function() {
        priv.updateModel();
        setTimeout(updateRegularly, 1000);
      };
      setTimeout(updateRegularly, 1000);
    };

    Object.defineProperty(that, "start", {
      configurable: false,
      enumerable: false,
      writable: false,
      value: function () {
        priv.setModel();
        priv.initJsPlumb();
        priv.initDialog();
        priv.displayGraph();
        priv.updateModelRegularly();
      }
    });

    Object.defineProperty(that, "setSimulationParameters", {
      configurable: false,
      enumerable: false,
      writable: false,
      value: function (simulation_parameters) {
        priv.setSimulationParameters(simulation_parameters);
      }
    });

    return that;
  };
  var DreamNamespace = (function () {
    var that = {};

    /**
    * Creates a new dream instance.
    * @method newDream
    * @param  {object} model The model definition
    * @return {object} The new Dream instance.
    */
    Object.defineProperty(that, "newDream", {
      configurable: false,
      enumerable: false,
      writable: false,
      value: function (model) {
        var instance = dream(model);
        return instance;
      }
    });

    return that;
  })();

  Object.defineProperty(scope, "DREAM", {
    configurable: false,
    enumerable: false,
    writable: false,
    value: DreamNamespace
  });

}(window, jQuery, jsPlumb, console, _));