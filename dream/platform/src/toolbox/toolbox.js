/*global window, document, RSVP, rJS, initGadgetMixin, console*/
(function (window, document, RSVP, rJS, initGadgetMixin) {
  "use strict";

  /*jslint nomen: true*/
  var gadget_klass = rJS(window);
  function waitForDragstart(tool) {
    var callback;

    function canceller() {
      if (callback !== undefined) {
        tool.removeEventListener('dragstart', callback, false);
      }
    }
    /*jslint unparam: true*/
    function itsANonResolvableTrap(resolve, reject) {

      callback = function (evt) {
        try {
          evt.dataTransfer.setData('application/json',
            tool.dataset.class_name);
        } catch (e) {
          reject(e);
        }
      };

      tool.addEventListener('dragstart', callback, false);
    }
    return new RSVP.Promise(itsANonResolvableTrap, canceller);
  }

  initGadgetMixin(gadget_klass);
  gadget_klass

    // XXX errors not reported
    .declareMethod("render", function (json_data) {
      var data = JSON.parse(json_data),
        tools_container = document.createElement('div');
      /* display all nodes in the palette.
       */
      console.log("RENDERING TOOLBOX");
      tools_container.className = 'tools-container';
      Object.keys(data.class_definition).forEach(function (key) {
        var _class_object = data.class_definition[key], tool;
        // XXX "expand" the json schema "allOF" etc
        console.log(_class_object);
        if (_class_object.allOf) {
          console.log("yupi");
          if (_class_object.allOf[0].$ref === "#/class_definition/node") {
            console.log("yupi2");
            tool = document.createElement('div');
            // XXX maybe allow to configure the class name ?
            tool.className = "tool " + key;
            console.log("..");
            console.log(tool.className);
            tool.textContent = _class_object.name || key;
            console.log(tool.textContent);
            tool.draggable = true;
            tool.dataset.class_name = JSON.stringify(key);
            console.log(tool.dataset.class_name);
            Object.keys(_class_object.css || {}).forEach(function (k) {
              tool.style[k] = _class_object.css[k];
            });
            tools_container.appendChild(tool);
          }
        }
      });

      this.props.element.querySelector('.tools')
        .appendChild(tools_container);
    })

    .declareMethod('startService', function () {
      var promiseArray = [];
      [].forEach
        .call(this.props.element.querySelectorAll('.tool'), function (tool) {
          promiseArray.push(waitForDragstart(tool));
        });
      return RSVP.all(promiseArray);
    });
}(window, document, RSVP, rJS, initGadgetMixin));
