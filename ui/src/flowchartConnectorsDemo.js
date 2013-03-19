;(function() {
	
	window.jsPlumbDemo = {
		init : function() {
				
			jsPlumb.importDefaults({
				// default drag options
				DragOptions : { cursor: 'pointer', zIndex:2000 },
				// default to blue at one end and green at the other
				EndpointStyles : [{ fillStyle:'#225588' }, { fillStyle:'#558822' }],
				// blue endpoints 7 px; green endpoints 11.
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
          [ "Label", { label:"FOO", id:"label" }]
        ],
        Anchor: "Continuous",
        Connector: ["StateMachine", { curviness:20 }],
			});			

			init = function(connection) {
				connection.getOverlay("label").setLabel(connection.sourceId.substring(6) + "-" + connection.targetId.substring(6));
				connection.bind("editCompleted", function(o) {
					if (typeof console != "undefined")
						console.log("connection edited. path is now ", o.path);
				});
			};			

						
			// listen for new connections; initialise them the same way we initialise the connections at startup.
			jsPlumb.bind("jsPlumbConnection", function(connInfo, originalEvent) { 
				init(connInfo.connection);
			});			
						
			// make all the window divs draggable						
			jsPlumb.draggable(jsPlumb.getSelector(".window"), { grid: [20, 20] });

			//
			// listen for clicks on connections, and offer to delete connections on click.
			//
			jsPlumb.bind("click", function(conn, originalEvent) {
				if (confirm("Delete connection from " + conn.sourceId + " to " + conn.targetId + "?"))
					jsPlumb.detach(conn); 
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
    
		}
	};
})();

(function() {
   function displayGraph() {
     // So instead of having html filled with data, we will use
     // a structure (like if we got it from json) and we will render it
     var graph_data = {}, i, i_length, render_dom, box, j, j_length,
         style_string, line, people_list, setSimulationParameters,
         available_people = {};
     graph_data.box_list = [
       {id: 'window1', title: '1', target_list: ['window2'], coordinate: {top: 5, left: 5}},
       {id: 'window2', title: '2', target_list: ['window3'], coordinate: {top: 5, left: 15}},
       {id: 'window3', title: '3', target_list: ['window7'], coordinate: {top: 5, left: 25}},
       {id: 'window4', title: '4', target_list: ['window5'], coordinate: {top: 20, left: 5}},
       {id: 'window5', title: '5', target_list: ['window6'], coordinate: {top: 20, left: 15}},
       {id: 'window6', title: '6', target_list: ['window7'], coordinate: {top: 20, left: 25}},
       {id: 'window7', title: 'Moulding', target_list: ['window8', 'window10'], coordinate: {top: 12, left: 35}},
       {id: 'window8', title: '8', target_list: ['window9'], coordinate: {top: 5, left: 45}},
       {id: 'window9', title: '9', coordinate: {top: 5, left: 55}},
       {id: 'window10', title: '10', target_list: ['window11'], coordinate: {top: 20, left: 45}},
       {id: 'window11', title: '11', coordinate: {top: 20, left: 55}},
     ];

     // Add boxes in the render div
     render_dom = $("[id=render]");
     i_length = graph_data.box_list.length;
     for (i=0; i < i_length; i++) {
       box = graph_data.box_list[i];
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
       render_dom.append('<div class="window" id="' +
                         box.id + '" ' + style_string + '"><strong>' + box.title
                         + '</strong><br/><br/></div>');
     }

     // Now that we have all boxes, connect them
     for (i=0; i < i_length; i++) {
       box = graph_data.box_list[i];
       if (box.target_list !== undefined) {
         j_length = box.target_list.length;
         for (j=0; j < j_length; j++) {
           line = jsPlumb.connect({source:box.id, target: box.target_list[j]});
           // Example to change line color
           // line.setPaintStyle({strokeStyle:"#42a62c", lineWidth:2 });
         }
       }
     }

     //Fill list of people
     people_list = ["Seb", "Jerome", "Jean-Paul", "Anna", "George", "Ivor", "Dipo", "Stephan"];
     i_length = people_list.length;
     for (i = 0; i < i_length; i++) {
       $("#not_available ul").append("<li>" + people_list[i] + "</li>");
     }

     // Define ajax call to update list of available people
     setSimulationParameters = function(parameters) {
      $.ajax({
        url: "http://localhost:5000/setSimulationParameters",
        type: 'POST',
        data: JSON.stringify(parameters),
        contentType: "application/json",
        success: function(response) {
          console.log("got json response",response);
        },
        error: function(xhr, textStatus, error) {
          onError(error);
        }
      });
     };
     // Make list of people draggable, update list of people depending
     // to make them available or not
     $("#available li").draggable({appendTo: "body"});
     $("#not_available li").draggable({appendTo: "body"});
     $("#available").droppable({
       drop: function(event, ui) {
         available_people[ui.draggable.text()] = true;
         console.log(available_people);
         setSimulationParameters(available_people);
       }
     });
     $("#not_available").droppable({
       drop: function(event, ui) {
         available_people[ui.draggable.text()] = false;
         console.log(available_people);
         setSimulationParameters(available_people);
       }
     });

     // Initial DEMO code : make all the window divs draggable
     jsPlumb.draggable(jsPlumb.getSelector(".window"), { grid: [20, 20] });

     // Now communicate our model to the simulation server
     $.ajax({
       url: "http://localhost:5000/setModel",
       type: 'POST',
       data: JSON.stringify(graph_data),
       contentType: "application/json",
       success: function(response) {
         console.log("got json response",response);
       },
       error: function(xhr, textStatus, error) {
         onError(error);
       }
     });

     // Utility function to update the style of a box
     var updateBoxStyle = function (box_id, style) {
       var box;
       box = $("#" + box_id);
       _.each(style, function(value, key, list) {
         box.css(key, value);
       })
     };

     // Then ask the server from time to time for an update of graph based
     // on the result of some simulation
     var getModel = function () {
       var refreshGraph = function(model) {
         var i, i_length, box;
         i_length = model.box_list.length;
         console.log("model", model);
         for (i = 0; i < i_length; i++) {
           //, style: {"background-color":"#FF0000"}
           box = model.box_list[i];
           if (box.enabled) {
             updateBoxStyle(box.id, {"background-color": "#5EFB6E"});
           } else {
             updateBoxStyle(box.id, {"background-color": "#FF0000"});
           }
         }
       };
       $.ajax({
         url: "http://localhost:5000/getModel",
         type: 'GET',
         success: function(response) {
           refreshGraph(response);
         },
         error: function(xhr, textStatus, error) {
           onError(error);
         }
       });

       setTimeout(getModel, 1000);
     };
     setTimeout(getModel, 1000);
  }
  setTimeout(function () {
    console.log("in timeout");
    displayGraph()
  }, 500);
})();

// Dummy code only to show json communication with server
(function() {
   function sendData(url, data, onSuccess, onError) {
 
    $.ajax({
        url: url,
        type: 'POST',
        data: JSON.stringify(data),
        contentType: "application/json",
        //crossDomain: true,
        success: function(responseJSON) {
          console.log("got json response",responseJSON);
        },
        error: function(xhr, textStatus, errorThrown) {
          onError(errorThrown);
        }
    });
  }
//   setTimeout(function () {
//     console.log("in timeout");
//     sendData("http://localhost:5000/someTest", {"a": "b"},
//              function (response) {console.log("ok", response);},
//              function(foo, bar, baz) {console.log("failure");})
//   }, 1000);
})();