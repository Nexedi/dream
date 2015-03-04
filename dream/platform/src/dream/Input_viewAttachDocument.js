/*global rJS, RSVP, promiseEventListener, promiseReadAsDataURL,
         initGadgetMixin, $, setTimeout */
(function (window, rJS, RSVP, promiseEventListener, promiseReadAsDataURL,
           initGadgetMixin) {
  "use strict";

  var gadget_klass = rJS(window);
  initGadgetMixin(gadget_klass);
  gadget_klass
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("aq_putAttachment", "jio_putAttachment")
    .declareAcquiredMethod("aq_getAttachment", "jio_getAttachment")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("startService", function () {
      var gadget = this,
        encoded_data,
        button;
      return new RSVP.Queue()
      .push(function () {
        return promiseEventListener(
          gadget.props.element.getElementsByClassName("attach_document")[0],
          'submit',
          false
        );
      })
      .push(function (evt) {
        button = evt.target.getElementsByClassName("ui-btn")[0];
        button.disabled = true;
        var file = evt.target.import_file.files[0];
        return promiseReadAsDataURL(file);
      })
      .push(function (filecontent) {
        encoded_data = filecontent;
        // get fresh version
        return gadget.aq_getAttachment({
          "_id": gadget.props.jio_key,
         "_attachment": "body.json"
        });
      })
      .push(function (jio_data) {
        var data = JSON.parse(jio_data);
        data.input[gadget.props.action_definition.input_id] = encoded_data;
        return gadget.aq_putAttachment({
          "_id": gadget.props.jio_key,
         "_attachment": "body.json",
         "_data": JSON.stringify(data)
        });
      }).push(function (){
        // XXX quick way to get a popup message
        $.mobile.loading( 'show', { text: "File uploaded", textVisible: true, textonly: true });
        setTimeout(function () { $.mobile.loading( "hide" ); button.disabled = false; }, 1000);
      });
    })
    .declareMethod("render", function (options) {
      this.props.jio_key = options.id;
      this.props.action_definition = options.action_definition;
    });

}(window, rJS, RSVP, promiseEventListener, promiseReadAsDataURL,
  initGadgetMixin));
