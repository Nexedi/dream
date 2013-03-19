Object.keys = function( obj ) {
  var array = new Array();
  for ( var prop in obj ) {
    if ( obj.hasOwnProperty( prop ) ) {
      array.push( prop );
    }
  }
  return array;
};


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

      var line;
//       line = jsPlumb.connect({source:"window1", target: "window2"});
//       line = jsPlumb.connect({source:"window2", target: "window3"});
//       line = jsPlumb.connect({source:"window4", target: "window5"});
//       line = jsPlumb.connect({source:"window5", target: "window6"});
//       // Example to change line color
//       // line.setPaintStyle({strokeStyle:"#42a62c", lineWidth:2 });
//       line = jsPlumb.connect({source:"window3", target: "window7"});
//       line = jsPlumb.connect({source:"window6", target: "window7"});
//       line = jsPlumb.connect({source:"window7", target: "window8"});
//       line = jsPlumb.connect({source:"window7", target: "window10"});
			//
            
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
         style_string;
     graph_data.box_list = [
       {id: 'window1', title: '1', target_list: ['window2'], coordinate: {top: 10, left: 5}},
       {id: 'window2', title: '2', target_list: ['window3'], coordinate: {top: 10, left: 15}},
       {id: 'window3', title: '3', target_list: ['window7'], coordinate: {top: 10, left: 25}},
       {id: 'window4', title: '4', target_list: ['window5'], coordinate: {top: 30, left: 5}},
       {id: 'window5', title: '5', target_list: ['window6'], coordinate: {top: 30, left: 15}},
       {id: 'window6', title: '6', target_list: ['window7'], coordinate: {top: 30, left: 25}},
       {id: 'window7', title: 'Moulding', target_list: ['window8', 'window10'], coordinate: {top: 20, left: 35}},
       {id: 'window8', title: '8', target_list: ['window9'], coordinate: {top: 10, left: 45}},
       {id: 'window9', title: '9', coordinate: {top: 10, left: 55}},
       {id: 'window10', title: '10', target_list: ['window11'], coordinate: {top: 30, left: 45}},
       {id: 'window11', title: '11', coordinate: {top: 30, left: 55}},
     ];

     // Add boxes in the render div
     render_dom = $("[id=render]");
     i_length = graph_data.box_list.length;
     for (i=0; i < i_length; i++) {
       box = graph_data.box_list[i];
       style_string = ""
       if (box.coordinate !== undefined) {
         style_string = 'style="';
         _.each(box.coordinate, function(value, key, list) {
           style_string = style_string + key + ':' + value + 'em;';
         })
       }
       style_string = style_string + '"';
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
         }
       }
     }


     // Initial DEMO code : make all the window divs draggable
     jsPlumb.draggable(jsPlumb.getSelector(".window"), { grid: [20, 20] });
  }
  setTimeout(function () {
    console.log("in timeout");
    displayGraph()
  }, 500);
})();

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
  setTimeout(function () {
    console.log("in timeout");
    sendData("http://localhost:5000/someTest", {"a": "b"},
             function (response) {console.log("ok", response);},
             function(foo, bar, baz) {console.log("failure");})
  }, 1000);
})();