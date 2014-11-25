/*global rJS, JSON, QUnit, jQuery, RSVP, console*/
(function(rJS, JSON, QUnit, RSVP, $) {
    "use strict";
    var start = QUnit.start, stop = QUnit.stop, test = QUnit.test, equal = QUnit.equal, ok = QUnit.ok, sample_class_definition = {
        edge: {
            description: "Base definition for edge",
            properties: {
                _class: {
                    type: "string"
                },
                destination: {
                    type: "string"
                },
                name: {
                    type: "string"
                },
                required: [ "name", "_class", "source", "destination" ],
                source: {
                    type: "string"
                }
            },
            type: "object"
        },
        "Example.Edge": {
            _class: "edge",
            allOf: [ {
                $ref: "#edge"
            }, {
                properties: {
                    color: {
                        "enum": [ "red", "green", "blue" ]
                    }
                }
            } ],
            description: "An example edge with a color property"
        },
        "Example.Node": {
            _class: "node",
            allOf: [ {
                $ref: "#node"
            }, {
                properties: {
                    shape: {
                        type: "string"
                    }
                }
            } ],
            description: "An example node with a shape property"
        },
        node: {
            description: "Base definition for node",
            properties: {
                _class: {
                    type: "string"
                },
                coordinate: {
                    properties: {
                        left: "number",
                        top: "number"
                    },
                    type: "object"
                },
                name: {
                    type: "string"
                },
                required: [ "name", "_class" ]
            },
            type: "object"
        }
    }, sample_graph = {
        edge: {
            edge1: {
                _class: "Example.Edge",
                source: "N1",
                destination: "N2",
                color: "blue"
            }
        },
        node: {
            N1: {
                _class: "Example.Node",
                name: "Node 1",
                coordinate: {
                    top: 0,
                    left: 0
                },
                shape: "square"
            },
            N2: {
                _class: "Example.Node",
                name: "Node 2",
                shape: "circle"
            }
        }
    }, sample_graph_not_connected = {
        edge: {},
        node: {
            N1: {
                _class: "Example.Node",
                name: "Node 1",
                shape: "square"
            },
            N2: {
                _class: "Example.Node",
                name: "Node 2",
                shape: "circle"
            }
        }
    }, sample_data_graph = JSON.stringify({
        class_definition: sample_class_definition,
        graph: sample_graph
    }), sample_data_graph_not_connected = JSON.stringify({
        class_definition: sample_class_definition,
        graph: sample_graph_not_connected
    }), sample_data_empty_graph = JSON.stringify({
        class_definition: sample_class_definition,
        graph: {
            node: {},
            edge: {}
        }
    });
    QUnit.config.testTimeout = 5e3;
    rJS(window).ready(function(g) {
        test("Sample graph can be loaded and output is equal to input", function() {
            var jsplumb_gadget;
            stop();
            g.declareGadget("./index.html", {
                element: document.querySelector("#qunit-fixture")
            }).then(function(new_gadget) {
                jsplumb_gadget = new_gadget;
                return jsplumb_gadget.render(sample_data_graph);
            }).then(function() {
                return jsplumb_gadget.getContent();
            }).then(function(content) {
                equal(content, sample_data_graph);
            }).fail(console.error.bind(this)).always(start);
        });
        test("New node can be drag & dropped", function() {
            var jsplumb_gadget;
            stop();
            function runTest() {
                // XXX here I used getContent to have a promise, but there must be a
                // more elegant way.
                return jsplumb_gadget.getContent().then(function() {
                    // fake a drop event
                    var e = new Event("drop");
                    e.dataTransfer = {
                        getData: function(type) {
                            // make sure we are called properly
                            equal(type, "application/json");
                            return JSON.stringify("Example.Node");
                        }
                    };
                    jsplumb_gadget.props.main.dispatchEvent(e);
                }).then(function() {
                    return jsplumb_gadget.getContent();
                }).then(function(content) {
                    var node, graph = JSON.parse(content).graph;
                    equal(1, Object.keys(graph.node).length);
                    node = graph.node[Object.keys(graph.node)[0]];
                    equal("Example.Node", node._class);
                });
            }
            g.declareGadget("./index.html", {
                element: document.querySelector("#qunit-fixture")
            }).then(function(new_gadget) {
                jsplumb_gadget = new_gadget;
                jsplumb_gadget.render(sample_data_empty_graph);
            }).then(function() {
                return RSVP.any([ jsplumb_gadget.startService(), runTest() ]);
            }).fail(console.error.bind(this)).always(start);
        });
        test("Node can be dragged", function() {
            var jsplumb_gadget;
            stop();
            function runTest() {
                return jsplumb_gadget.getContent().then(function() {
                    // 100 and 60 are about 10% of the #main div ( set by css, so this
                    // might change )
                    $("div[title='Node 1']").simulate("drag", {
                        dx: 100,
                        dy: 60
                    });
                }).then(function() {
                    return jsplumb_gadget.getContent();
                }).then(function(content) {
                    var graph = JSON.parse(content).graph, node_coordinate = graph.node.N1.coordinate;
                    // Since original coordinates where 0,0 we are now about 0.1,0.1
                    // as we moved 10%
                    ok(node_coordinate.top - .1 < .1, "Top is ok");
                    ok(node_coordinate.left - .1 < .1, "Left is ok");
                });
            }
            g.declareGadget("./index.html", {
                element: document.querySelector("#qunit-fixture")
            }).then(function(new_gadget) {
                jsplumb_gadget = new_gadget;
                jsplumb_gadget.render(sample_data_graph);
            }).then(function() {
                return RSVP.any([ jsplumb_gadget.startService(), runTest() ]);
            }).fail(console.error.bind(this)).always(start);
        });
        test("Node properties can be edited", function() {
            var jsplumb_gadget;
            stop();
            function runTest() {
                return jsplumb_gadget.getContent().then(function() {
                    $("div[title='Node 1']").simulate("dblclick");
                    // XXX popup not displayed
                    $("input[name='name']").val("Modified Name");
                    $("input[value='Validate']").click();
                }).then(function() {
                    return jsplumb_gadget.getContent();
                }).then(function(content) {
                    var graph = JSON.parse(content).graph, node = graph.node.N1;
                    equal(node.name, "Modified Name");
                });
            }
            g.declareGadget("./index.html", {
                element: document.querySelector("#qunit-fixture")
            }).then(function(new_gadget) {
                jsplumb_gadget = new_gadget;
                jsplumb_gadget.render(sample_data_graph);
            }).then(function() {
                return RSVP.any([ jsplumb_gadget.startService(), runTest() ]);
            }).fail(console.error.bind(this)).always(start);
        });
        test("Node can be connected", function() {
            var jsplumb_gadget;
            stop();
            function runTest() {
                return jsplumb_gadget.getContent().then(function(content) {
                    var node1 = jsplumb_gadget.props.main.querySelector("div[title='Node 1']"), node2 = jsplumb_gadget.props.main.querySelector("div[title='Node 2']");
                    // At this point we have no edge
                    equal(Object.keys(JSON.parse(content).graph.edge).length, 0);
                    jsplumb_gadget.props.jsplumb_instance.connect({
                        source: node1.id,
                        target: node2.id
                    });
                }).then(function() {
                    return jsplumb_gadget.getContent();
                }).then(function(content) {
                    var edge, graph = JSON.parse(content).graph;
                    equal(Object.keys(graph.node).length, 2);
                    equal(Object.keys(graph.edge).length, 1);
                    edge = graph.edge[Object.keys(graph.edge)[0]];
                    // XXX how edge class would be set ? the first one from schema ?
                    //equal(edge._class, "Example.Edge");
                    equal(edge.source, "N1");
                    equal(edge.destination, "N2");
                });
            }
            g.declareGadget("./index.html", {
                element: document.querySelector("#qunit-fixture")
            }).then(function(new_gadget) {
                jsplumb_gadget = new_gadget;
                jsplumb_gadget.render(sample_data_graph_not_connected);
            }).then(function() {
                return RSVP.any([ jsplumb_gadget.startService(), runTest() ]);
            }).fail(console.error.bind(this)).always(start);
        });
        test("Node can be deleted", function() {
            var jsplumb_gadget;
            stop();
            function runTest() {
                return jsplumb_gadget.getContent().then(function() {
                    $("div[title='Node 1']").simulate("dblclick");
                    // XXX popup not displayed
                    $("input[value='Delete']").click();
                }).then(function() {
                    return jsplumb_gadget.getContent();
                }).then(function(content) {
                    var graph = JSON.parse(content).graph;
                    equal(1, Object.keys(graph.node).length);
                });
            }
            g.declareGadget("./index.html", {
                element: document.querySelector("#qunit-fixture")
            }).then(function(new_gadget) {
                jsplumb_gadget = new_gadget;
                jsplumb_gadget.render(sample_data_graph);
            }).then(function() {
                return RSVP.any([ jsplumb_gadget.startService(), runTest() ]);
            }).fail(console.error.bind(this)).always(start);
        });
    });
})(rJS, JSON, QUnit, RSVP, jQuery);