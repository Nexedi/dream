/*global rJS, JSON, QUnit, jQuery, RSVP, console*/

(function (rJS, JSON, QUnit, RSVP) {
  "use strict";
  var start = QUnit.start,
    stop = QUnit.stop,
    test = QUnit.test,
    equal = QUnit.equal,
    sample_class_definition = {
      "edge": {
        "description": "Base definition for edge",
        "properties": {
          "_class": {
            "type": "string"
          },
          "destination": {
            "type": "string"
          },
          "name": {
            "type": "string"
          },
          "required": [
            "name",
            "_class",
            "source",
            "destination"
          ],
          "source": {
            "type": "string"
          }
        },
        "type": "object"
      },
      "Example.Edge": {
        "_class": "edge",
        "allOf": [
          {
            "$ref": "#edge"
          },
          {
            "properties": {
              "color": {
                "enum": [
                  "red",
                  "green",
                  "blue"
                ]
              }
            }
          }
        ],
        "description": "An example edge with a color property"
      },
      "Example.Node": {
        "_class": "node",
        "allOf": [
          {
            "$ref": "#node"
          },
          {
            "properties": {
              "shape": {
                "type": "string"
              }
            }
          }
        ],
        "description": "An example node with a shape property"
      },
      "node": {
        "description": "Base definition for node",
        "properties": {
          "_class": {
            "type": "string"
          },
          "coordinate": {
            "properties": {
              "left": "number",
              "top": "number"
            },
            "type": "object"
          },
          "name": {
            "type": "string"
          },
          "required": [
            "name",
            "_class"
          ]
        },
        "type": "object"
      }
    },
    sample_graph = {
      "edge": {
        "edge1": {
          "_class": "Example.Edge",
          "source": "N1",
          "destination": "N2",
          "color": "blue"
        }
      },
      "node": {
        "N1": {
          "_class": "Example.Node",
          "name": "Node 1",
          "shape": "square"
        },
        "N2": {
          "_class": "Example.Node",
          "name": "Node 2",
          "shape": "circle"
        }
      }
    },
    sample_data_graph = JSON.stringify(
      {class_definition: sample_class_definition, graph: sample_graph }
    ),
    sample_data_empty_graph = JSON.stringify(
      {class_definition: sample_class_definition, graph: {node: {}, edge: {}} }
    );

  QUnit.config.testTimeout = 5000;

  rJS(window).ready(function (g) {

    test("Sample graph can be loaded and output is equal to input",
      function () {
        var jsplumb_gadget;
        stop();
        g.declareGadget("./index.html", {
          element: document.querySelector("#qunit-fixture")
        })
          .then(function (new_gadget) {
            jsplumb_gadget = new_gadget;
            return jsplumb_gadget.render(sample_data_graph);
          })
          .then(function () {
            return jsplumb_gadget.getContent();
          })
          .then(function (content) {
            equal(content, sample_data_graph);
          })
          .fail(console.error.bind(this))
          .always(start);
    });

    test("New node can be drag & dropped", function () {
      var jsplumb_gadget;
      stop();

      function runTest() {
        return jsplumb_gadget.getContent().then(function () {
            // fake a drop event
            var e = new Event('drop');
            e.dataTransfer = {
              getData: function(type){
                 // make sure we are called properly
                 equal(type, 'application/json');
                 return JSON.stringify("Example.Node");
              }
            };
            jsplumb_gadget.props.main.dispatchEvent(e);
          })
          .then(function () {
            return jsplumb_gadget.getContent();
          })
          .then(function (content) {
            var node, graph = JSON.parse(content).graph;
            equal(1, Object.keys(graph.node).length);
            node = graph.node[Object.keys(graph.node)[0]];
            equal('Example.Node', node._class);
          });
      }

      g.declareGadget("./index.html", {
        element: document.querySelector("#qunit-fixture")
      })
        .then(function (new_gadget) {
          jsplumb_gadget = new_gadget;
          jsplumb_gadget.render(sample_data_empty_graph);
        })
        .then(function () {
          return RSVP.any([
            jsplumb_gadget.startService(),
            runTest()
            ]);
        })
        .fail(console.error.bind(this))
        .always(start);
    });

  });

}(rJS, JSON, QUnit, RSVP));
