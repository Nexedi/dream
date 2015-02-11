/*global rJS, promiseEventListener, initGadgetMixin, RSVP, CodeMirror */
(function (window, rJS, promiseEventListener, initGadgetMixin, RSVP, CodeMirror) {
  "use strict";

  var gadget_klass = rJS(window);
  initGadgetMixin(gadget_klass);
  gadget_klass
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("aq_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("aq_putAttachment", "jio_putAttachment")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("startService", function () {
      var gadget = this;
      return new RSVP.Queue()
      .push(function () {
        return promiseEventListener(
          gadget.props.element.querySelector(".save_button"),
          'click',
          false
        );
      })
      .push(function () {
        return gadget.aq_putAttachment({
          "_id": gadget.props.jio_key,
         "_attachment": "body.json",
         "_data": gadget.props.codemirror.getValue()
        });
      });
    })
    .declareMethod("render", function (options) {
      var gadget = this;
      this.props.jio_key = options.id;
      this.props.result = options.result;

      return gadget.aq_getAttachment({
        "_id": gadget.props.jio_key,
        "_attachment": "body.json"
      })
      .push(function (result_json) {
        var jsonTextArea = gadget.props.element.querySelector(".json");
        jsonTextArea.textContent = result_json;
        gadget.props.codemirror = CodeMirror.fromTextArea(jsonTextArea, {
          lineNumbers: true,
          mode: {name: 'javascript', json: true},
          foldGutter: true,
          lint: true,
          gutters: ["CodeMirror-linenumbers", "CodeMirror-foldgutter", "CodeMirror-lint-markers"],
          extraKeys: {
            "Ctrl-S": function(instance) {
              // XXX this is outside of promise chain.
              return gadget.aq_putAttachment({
                "_id": gadget.props.jio_key,
                "_attachment": "body.json",
                "_data": instance.getValue()
              });
            }
          }
        });
      });
    });
}(window, rJS, promiseEventListener, initGadgetMixin, RSVP, CodeMirror));