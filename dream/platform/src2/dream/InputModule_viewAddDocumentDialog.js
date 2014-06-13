/*global rJS, RSVP, promiseEventListener, promiseReadAsText,
         initGadgetMixin */
(function (window, rJS, RSVP, promiseEventListener, promiseReadAsText,
           initGadgetMixin) {
  "use strict";

  var gadget_klass = rJS(window);
  initGadgetMixin(gadget_klass);
  gadget_klass
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("aq_post", "jio_post")
    .declareAcquiredMethod("aq_putAttachment", "jio_putAttachment")
    .declareAcquiredMethod("pleaseRedirectMyHash", "pleaseRedirectMyHash")
    .declareAcquiredMethod("whoWantToDisplayThisDocument",
                           "whoWantToDisplayThisDocument")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("startService", function () {
      var gadget = this,
        json_data,
        name;

      return new RSVP.Queue()
        .push(function () {
          return promiseEventListener(
            gadget.props.element.getElementsByClassName("import_form")[0],
            'submit',
            false
          );
        })
        .push(function (evt) {
          // Prevent double click
          gadget.props.element
            .getElementsByClassName("ui-btn")[0].disabled = true;

          var file = evt.target.dream_import.files[0];
          name = file.name;
          return promiseReadAsText(file);
        })
        .push(function (json) {
          var now = new Date();
          json_data = json;
          // Create jIO document
          return gadget.aq_post({
            title: name,
            type: "Dream",
            format: "application/json",
            modified: now.toUTCString(),
            date: now.getFullYear() + "-" + (now.getMonth() + 1) + "-" +
              now.getDate()
          });
        })
        .push(function (jio_document) {
          // Add JSON as attachment
          return gadget.aq_putAttachment({
            "_id": jio_document.id,
            "_attachment": "body.json",
            "_data": json_data,
            "_mimetype": "application/json"
          });
        })
        .push(function (result) {
          return gadget.whoWantToDisplayThisDocument(result.id);
        })
        .push(function (url) {
          return gadget.pleaseRedirectMyHash(url);
        });
    });

}(window, rJS, RSVP, promiseEventListener, promiseReadAsText,
  initGadgetMixin));
