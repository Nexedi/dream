(function($) {
  "use strict";

  jsPlumb.bind("ready", function() {

    /* Initialize jsPlumb defaults
     */
    // TODO: default for connections ?
    jsPlumb.setRenderMode(jsPlumb.SVG);
    jsPlumb.importDefaults({
      Endpoint: [ "Dot", {radius: 2} ],
      ConnectionOverlays : [
        [ "Arrow", { location:1, width:10 } ]
      ],
      Anchor: "Continuous"
    });     


$.widget("dream.grapheditor", {
  options: {
    node_class: "graph_node", // CSS class for nodes
    node_data_key: "grapheditor_node_data", // Key to store data on nodes using $.data
                                            // XXX is it good idea to use
                                            // $.data ???
    draggable_nodes: true, // Can nodes be dragged
  },

  _create: function() {
     this.nodes = {};
     this.edges = {};

     if (this.options.graph) {
        this.graph(this.options.graph);
     }
  },

  destroy: function() {
    this.clear();
    this._destroy();
  },

  clear: function() {
    this.edges = {};
    $.each(this.nodes, $.proxy(function(node_id, node) {
      jsPlumb.remove(node);
      delete(this["nodes"][node_id]);
    }, this));
  },

  create_node_element: function(node_id, node_data) {
    // Create an element for a node, and add it to the main element.
    return $('<div>')
       .uniqueId()
      .addClass(this.options.node_class)
      .text(node_data['name'] || node_id)
      .appendTo(this.element)
  },

  add_node: function(node_id, node_data) {
    /* add a node */
    var element = this.create_node_element(node_id, node_data);
    if (this.options.draggable_nodes) {
      // make the node draggable
      jsPlumb.draggable(element, {
        containment: this.element,
        stop: $.proxy(function(node_id, event) {
            this.node_position(node_id, this.node_position(node_id));
            this._trigger("node_moved", event, node_id);
          }, this, node_id)
      });
    }
    this.nodes[node_id] = element;
    this.node_position(node_id, node_data);
    this.node_data(node_id, node_data);
    this._trigger('node_added', node_id);
  },

  create_edge_element: function(edge_id, source_node_id, destination_node_id, edge_data) {
    // Create an element for an edge
    var edge_label = edge_data['name'] || "";
    jsPlumb.connect({
      source: this.nodes[source_node_id].attr("id"),
      target: this.nodes[destination_node_id].attr("id"),
      paintStyle: { lineWidth: 1, strokeStyle: "#000" }, // XXX make this an option
      overlays : [["Label", {label: edge_label}]]
    });
  },

  add_edge: function(edge_id, source_node_id, destination_node_id, edge_data) {
    /* add an edge */
    this.create_edge_element(edge_id, source_node_id, destination_node_id, edge_data);
    this.edges[edge_id] = [source_node_id, destination_node_id, edge_data];
    this._trigger('edge_added', edge_id);
  },

  node_data: function(node_id, node_data) {
    /* get or set data for a node */
    var node = this.nodes[node_id];
    if (node_data === undefined) {
      return node.data(this.options.node_data_key);
    }
    this.nodes[node_id].data(this.options.node_data_key, node_data);
    this._trigger("node_data_changed", node_id)
    return this
  },

  edge_data: function(edge_id, edge_data) {
    /* get or set data for an edge */
    var edge = this.edges[edge_id];
    if (edge_data === undefined) {
      return edge[2]
    }
    this.edges[edge_id] = [edge[0], edge[1], edge_data]
    this._trigger("edge_data_changed", edge_id)
    return this
  },

  node_position: function(node_id, position) {
    /* Get or set the position of a node with position given on a 0..1 scale */
    var node = this.nodes[node_id],
        node_position = node.position(),
        element_position = this.element.position();
    if (position === undefined) {
      return {
        "top": (node_position.top - element_position.top)
          / (this.element.height() - node.height()),
        "left": (node_position.left - element_position.left)
          / (this.element.width() - node.width())
      };
    }
    node.css({
        "top": element_position.top + 
          Math.floor(position.top * (this.element.height() - node.height())) + "px",
        "left": element_position.left +
          Math.floor(position.left * (this.element.width() - node.width())) + "px"
    });
    // update node data with position
    this.node_data(node_id, $.extend(this.node_data(node_id), 
      {top: position.top, left: position.left}));
    jsPlumb.repaintEverything();
    return this;
  },

  graph: function(value) {
    // get or set the graph data
    if ( value === undefined ) {
      // get
      var graph = {"nodes": {}, "edges": {}};
      $.each(this.nodes, $.proxy(function(node_id, node) {
        graph["nodes"][node_id] = node.data(this.options.node_data_key);
      }, this));
      $.each(this.edges, $.proxy(function(edge_id, edge) {
        graph["edges"][edge_id] = this.edges[edge_id];
      }, this));
      return graph;
    }

    this.clear();
    $.each(value.nodes, $.proxy(function(node_id, node) {
      this.add_node(node_id, node);
    }, this));
    $.each(value.edges, $.proxy(function(edge_id, edge) {
      this.add_edge(edge_id, edge[0], edge[1], edge[2] || {});
    }, this));
    return this;
  }
});





    $.getJSON("JSONInputs/Topology01.json", function(data) {
      $("#main").grapheditor({graph: data,
        node_moved: function(event, node_id) {
          $("#debug_zone").val(JSON.stringify(
            $("#main").grapheditor("graph"), undefined, " "));
        }
      });

      // move a node
      function move_node() {
        $("#main").grapheditor("node_position", $("#node_id").val(), {
          top: $("#node_top").val() / 100,
          left: $("#node_left").val() / 100});
      }
      $("#move_node").click(move_node);
      $("#node_top").change(move_node);
      $("#node_left").change(move_node);
      
      // when node is selected or moved, update the sliders
      function updateSliders(node_id) {
        var node_pos = grapheditor.node_position(node_id);
        $("#node_id").val(node_id);
        $("#node_top").val(Math.floor(node_pos.top * 100)).slider("refresh");
        $("#node_left").val(Math.floor(node_pos.left * 100)).slider("refresh");
      }

      // Access the nodes
      var grapheditor = $("#main").data("dreamGrapheditor");
      $.each(grapheditor.nodes, function(node_id, node) {
        node.click(function(e){updateSliders(node_id)});
        // test: click to add a property
        node.click(function(e){
           $.mobile.changePage( "#dialog", { role: "dialog" } );
          $("#main").grapheditor("node_data", node_id,
            $.extend( $("#main").grapheditor("node_data", node_id),
                      {"dbclick": 1} ))
        });
      })
      $("#main").on("grapheditornode_moved", function(event, node_id) { updateSliders(node_id) })

      // reload from json
      $("#load_json").click(function() { $("#main").grapheditor("graph",
        JSON.parse($("#debug_zone").val()))});
      
    });

  });
})(jQuery);
