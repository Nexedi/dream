/*global window, document, RSVP, rJS, Handlebars, initGadgetMixin*/
(function(window, document, RSVP, rJS, Handlebars, initGadgetMixin) {
    "use strict";
    /*jslint nomen: true*/
    var gadget_klass = rJS(window), tool_template_source = gadget_klass.__template_element.getElementById("tool-template").innerHTML, tool_template = Handlebars.compile(tool_template_source);
    function waitForDragstart(tool) {
        var callback;
        function canceller() {
            if (callback !== undefined) {
                tool.removeEventListener("dragstart", callback, false);
            }
        }
        /*jslint unparam: true*/
        function itsANonResolvableTrap(resolve, reject) {
            callback = function(evt) {
                try {
                    evt.dataTransfer.setData("text/html", tool.outerHTML);
                } catch (e) {
                    reject(e);
                }
            };
            tool.addEventListener("dragstart", callback, false);
        }
        return new RSVP.Promise(itsANonResolvableTrap, canceller);
    }
    initGadgetMixin(gadget_klass);
    gadget_klass.declareAcquiredMethod("getConfigurationDict", "getConfigurationDict").declareMethod("render", function() {
        var g = this;
        return g.getConfigurationDict().push(function(config_dict) {
            var tools_container = document.createElement("div");
            tools_container.className = "tools-container";
            Object.keys(config_dict).forEach(function(key) {
                var name = config_dict[key].name || key.split("-")[1];
                if (key !== "Dream-Configuration") {
                    tools_container.innerHTML += tool_template({
                        key: key,
                        name: name
                    });
                }
            });
            g.props.element.querySelector(".tools").appendChild(tools_container);
        });
    }).declareMethod("startService", function() {
        var promiseArray = [];
        [].forEach.call(this.props.element.querySelectorAll(".tool"), function(tool) {
            promiseArray.push(waitForDragstart(tool));
        });
        return RSVP.all(promiseArray);
    });
})(window, document, RSVP, rJS, Handlebars, initGadgetMixin);