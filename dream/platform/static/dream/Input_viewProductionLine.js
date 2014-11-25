/*global window, rJS, RSVP, loopEventListener*/
(function(window, rJS, RSVP, loopEventListener) {
    "use strict";
    var gadget_klass = rJS(window);
    // TODO: save on parent gadget
    function saveGraph(evt) {
        var gadget = this;
        return new RSVP.Queue().push(function() {
            // Prevent double click
            if (evt) {
                evt.target.getElementsByClassName("ui-btn")[0].disabled = true;
            }
            return gadget.getDeclaredGadget("productionline_graph");
        }).push(function(graph_gadget) {
            return graph_gadget.getContent();
        }).push(function(body) {
            return gadget.aq_putAttachment({
                _id: gadget.props.jio_key,
                _attachment: "body.json",
                _data: JSON.stringify(JSON.parse(body), null, 2),
                _mimetype: "application/json"
            });
        }).push(function() {
            if (evt) {
                evt.target.getElementsByClassName("ui-btn")[0].disabled = false;
            }
        });
    }
    function waitForSave(gadget) {
        return loopEventListener(gadget.props.element.getElementsByClassName("save_form")[0], "submit", false, saveGraph.bind(gadget));
    }
    gadget_klass.ready(function(g) {
        g.props = {};
    }).ready(function(g) {
        return g.getElement().push(function(element) {
            g.props.element = element;
        });
    }).declareAcquiredMethod("aq_getAttachment", "jio_getAttachment").declareAcquiredMethod("aq_putAttachment", "jio_putAttachment").allowPublicAcquisition("notifyDataChanged", function() {
        // We are notified by an included gadget that the data has changed.
        // Here we save automatically. We could mark a dirty flag to warn the
        // user if she leaves the page without saving.
        // Since we are notified quite often and saving is resource expensive, we
        // use this trick to prevent saving too many times
        if (this.timeout) {
            window.clearTimeout(this.timeout);
        }
        this.timeout = window.setTimeout(saveGraph.bind(this), 100);
    }).declareMethod("render", function(options) {
        var jio_key = options.id, gadget = this, data;
        gadget.props.jio_key = jio_key;
        return new RSVP.Queue().push(function() {
            /*jslint nomen: true*/
            return RSVP.all([ gadget.aq_getAttachment({
                _id: jio_key,
                _attachment: "body.json"
            }), gadget.getDeclaredGadget("productionline_graph") ]);
        }).push(function(result_list) {
            data = result_list[0];
            return result_list[1].render(data);
        }).push(function() {
            return gadget.getDeclaredGadget("productionline_toolbox");
        }).push(function(toolbox_gadget) {
            toolbox_gadget.render(data);
        });
    }).declareMethod("startService", function() {
        var g = this, graph;
        return g.getDeclaredGadget("productionline_graph").push(function(graph_gadget) {
            graph = graph_gadget;
            return g.getDeclaredGadget("productionline_toolbox");
        }).push(function(toolbox) {
            return RSVP.all([ graph.startService(), toolbox.startService(), waitForSave(g) ]);
        });
    });
})(window, rJS, RSVP, loopEventListener);