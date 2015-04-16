/*global window, document, RSVP, rJS, initGadgetMixin*/
(function(window, document, RSVP, rJS, initGadgetMixin) {
    "use strict";
    /*jslint nomen: true*/
    var gadget_klass = rJS(window);
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
                    // Internet explorer only accepts text and URI as types for dataTranser
                    // but firefox will replace location.href with the data if type is set to
                    // text or URI. We try to use application/json as type, and if it fails
                    // fallback to text.
                    try {
                        // IE will raise an error setting this.
                        evt.dataTransfer.setData("application/json", tool.dataset.class_name);
                    } catch (e) {
                        evt.dataTransfer.setData("text", tool.dataset.class_name);
                    }
                } catch (e) {
                    reject(e);
                }
            };
            tool.addEventListener("dragstart", callback, false);
        }
        return new RSVP.Promise(itsANonResolvableTrap, canceller);
    }
    initGadgetMixin(gadget_klass);
    gadget_klass.declareMethod("render", function(json_data) {
        var data = JSON.parse(json_data), tools_container = document.createElement("div");
        /* display all nodes in the palette.
       */
        tools_container.className = "tools-container";
        Object.keys(data.class_definition).forEach(function(key) {
            var _class = data.class_definition[key], tool;
            // XXX "expand" the json schema "allOf" etc
            if (_class._class === "node") {
                tool = document.createElement("div");
                // XXX maybe allow to configure the class name ?
                tool.className = "tool " + key;
                tool.textContent = _class.name || key;
                tool.draggable = true;
                tool.dataset.class_name = JSON.stringify(key);
                if (_class.description) {
                    tool.title = _class.description;
                }
                Object.keys(_class.css || {}).forEach(function(k) {
                    // some styles are ignored here, to keep the rendering of toolbox consistent.
                    if (k !== "line-height") {
                        tool.style[k] = _class.css[k];
                    }
                });
                tools_container.appendChild(tool);
            }
        });
        this.props.element.querySelector(".tools").appendChild(tools_container);
    }).declareMethod("startService", function() {
        var promiseArray = [];
        [].forEach.call(this.props.element.querySelectorAll(".tool"), function(tool) {
            promiseArray.push(waitForDragstart(tool));
        });
        return RSVP.all(promiseArray);
    });
})(window, document, RSVP, rJS, initGadgetMixin);