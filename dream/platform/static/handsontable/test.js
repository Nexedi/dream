/*global rJS, JSON, QUnit, jQuery*/
(function(rJS, JSON, QUnit, $) {
    "use strict";
    var start = QUnit.start, stop = QUnit.stop, test = QUnit.test, equal = QUnit.equal, sample = JSON.stringify([ [ "row1", "data11", "data12", "data13" ], [ "row2", "data21", "data22", "data23" ], [ "row3", "data31", "data32", "data33" ] ]);
    QUnit.config.testTimeout = 5e3;
    rJS(window).ready(function(g) {
        test("data output is equal to input", function() {
            var hstable_gadget;
            stop();
            g.declareGadget("./index.html", {
                element: document.querySelector("#qunit-fixture")
            }).then(function(new_gadget) {
                hstable_gadget = new_gadget;
                return hstable_gadget.render(sample);
            }).then(function() {
                return hstable_gadget.getData();
            }).then(function(data) {
                equal(data, sample);
            }).always(start);
        });
        test("the table is displayed", function() {
            var hstable_gadget;
            stop();
            g.declareGadget("./index.html", {
                element: document.querySelector("#qunit-fixture")
            }).then(function(new_gadget) {
                hstable_gadget = new_gadget;
                return hstable_gadget.render(sample);
            }).then(function() {
                var rows = $("table tbody tr");
                equal(rows.length, 3);
                equal(rows[0].childNodes.length, 4);
                equal(rows[0].childNodes[2].innerHTML, "data12");
            }).always(start);
        });
        test("the gadget can be configured", function() {
            var hstable_gadget;
            stop();
            g.declareGadget("./index.html", {
                element: document.querySelector("#qunit-fixture")
            }).then(function(new_gadget) {
                hstable_gadget = new_gadget;
                return hstable_gadget.render(sample, {
                    minSpareRows: 1
                });
            }).then(function() {
                var rows = $("table tbody tr");
                // There is one spare row
                equal(rows.length, 4);
            }).then(function() {
                return hstable_gadget.getData();
            }).then(function(data) {
                equal(data, JSON.stringify([ [ "row1", "data11", "data12", "data13" ], [ "row2", "data21", "data22", "data23" ], [ "row3", "data31", "data32", "data33" ], [ null, null, null, null ] ]));
            }).always(start);
        });
    });
})(rJS, JSON, QUnit, jQuery);