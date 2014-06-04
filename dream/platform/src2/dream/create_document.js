/*global console, rJS, RSVP, FileReader */
(function (window, rJS, RSVP, FileReader) {
  "use strict";

  function promiseEventListener(target, type, useCapture) {
    //////////////////////////
    // Resolve the promise as soon as the event is triggered
    // eventListener is removed when promise is cancelled/resolved/rejected
    //////////////////////////
    var handle_event_callback;

    function canceller() {
      target.removeEventListener(type, handle_event_callback, useCapture);
    }

    function resolver(resolve) {
      handle_event_callback = function (evt) {
        canceller();
        evt.stopPropagation();
        evt.preventDefault();
        resolve(evt);
        return false;
      };

      target.addEventListener(type, handle_event_callback, useCapture);
    }
    return new RSVP.Promise(resolver, canceller);
  }

  function promiseReadAsText(file) {
    return new RSVP.Promise(function (resolve, reject) {
      var reader = new FileReader();
      reader.onload = function (evt) {
        resolve(evt.target.result);
      };
      reader.onerror = function (evt) {
        reject(evt);
      };
      reader.readAsText(file);
    });
  }

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("aq_post", "jio_post")
    .declareAcquiredMethod("aq_putAttachment", "jio_putAttachment")
    .declareAcquiredMethod("pleaseRedirectMyHash", "pleaseRedirectMyHash")
    .declareAcquiredMethod("whoWantToDisplayThisDocument",
                           "whoWantToDisplayThisDocument")

    /////////////////////////////////////////////////////////////////
    // ready
    /////////////////////////////////////////////////////////////////
    // Init local properties
    .ready(function (g) {
      g.props = {};
    })

    // Assign the element to a variable
    .ready(function (g) {
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
        });
    })

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

}(window, rJS, RSVP, FileReader));
