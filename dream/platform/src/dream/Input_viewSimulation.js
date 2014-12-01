/*global rJS, RSVP, jQuery, promiseEventListener, initGadgetMixin */
/*jslint nomen: true */
(function (window, rJS, RSVP, $, promiseEventListener, initGadgetMixin) {
  "use strict";

  function saveForm(gadget) {
    var general;
    return gadget.getDeclaredGadget('fieldset')
      .push(function (fieldset_gadget) {
        return fieldset_gadget.getContent();
      })
      .push(function (content) {
        general = content;
        // Always get a fresh version, to prevent deleting spreadsheet & co
        return gadget.aq_getAttachment({
          "_id": gadget.props.jio_key,
          "_attachment": "body.json"
        });
      })
      .push(function (body) {
        var data = JSON.parse(body);
        data.general = general;
        return gadget.aq_putAttachment({
          "_id": gadget.props.jio_key,
          "_attachment": "body.json",
          "_data": JSON.stringify(data, null, 2),
          "_mimetype": "application/json"
        });
      });
  }

  function runSimulation(gadget) {
    return new RSVP.Queue()
      .push(function () {
        return gadget.aq_getAttachment({
          "_id": gadget.props.jio_key,
          "_attachment": "body.json"
        });
      })
      .push(function (body_json) {
        // XXX Hardcoded relative URL
        return gadget.aq_ajax({
          url: "../../runSimulation",
          type: "POST",
          data: body_json,
          headers: {
            "Content-Type": 'application/json'
          }
        });
      })
      .push(function (evt) {
        var json_data = JSON.parse(evt.target.responseText);
        if (json_data.success !== true) {
          throw new Error(json_data.error);
        }
        return gadget.aq_putAttachment({
          "_id": gadget.props.jio_key,
          "_attachment": "simulation.json",
          "_data": JSON.stringify(json_data.data, null, 2),
          "_mimetype": "application/json"
        });
      })
      .push(function () {
        return gadget.whoWantsToDisplayThisDocument(
          gadget.props.jio_key,
          "view_result"
        );
      })
      .push(function (url) {
        return gadget.pleaseRedirectMyHash(url);
      });
  }

  function waitForRunSimulation(gadget) {
    var submit_evt;
    return new RSVP.Queue()
      .push(function () {
        return promiseEventListener(
          gadget.props.element.getElementsByClassName("run_form")[0],
          'submit',
          false
        );
      })
      .push(function (evt) {
        submit_evt = evt;
        // Prevent double click
        evt.target.getElementsByClassName("ui-btn")[0].disabled = true;
        $.mobile.loading('show');
        return saveForm(gadget);
      })
      .push(function () {
        return runSimulation(gadget);
      })
      .push(undefined, function (error) {
        // Always drop the loader
        $.mobile.loading('hide');
        throw error;
      })
      .push(function () {
        submit_evt.target.getElementsByClassName("ui-btn")[0].disabled = false;
        $.mobile.loading('hide');
      });
  }

  /////////////////////////////////////////////////////////////////
  // Handlebars
  /////////////////////////////////////////////////////////////////
  // Precompile the templates while loading the first gadget instance
  var gadget_klass = rJS(window);
  initGadgetMixin(gadget_klass);
  gadget_klass
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("aq_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("aq_putAttachment", "jio_putAttachment")
    .declareAcquiredMethod("aq_ajax", "jio_ajax")
    .declareAcquiredMethod("pleaseRedirectMyHash", "pleaseRedirectMyHash")
    .declareAcquiredMethod("whoWantsToDisplayThisDocument",
                           "whoWantsToDisplayThisDocument")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function (options) {
      var gadget = this,
        data;

      this.props.jio_key = options.id;

      return gadget.aq_getAttachment({
        "_id": gadget.props.jio_key,
        "_attachment": "body.json"
      })
        .push(function (json) {
          var application_configuration = {};
          data = JSON.parse(json);
          application_configuration =
            data.application_configuration.general || {};

          return gadget.getDeclaredGadget('fieldset').push(
            function (fieldset_gadget) {
              return fieldset_gadget.render({
                value: data.general,
                property_definition: application_configuration
              });
            }
          );
        });
    })

    .declareMethod("startService", function () {
      return waitForRunSimulation(this);
    });
}(window, rJS, RSVP, jQuery, promiseEventListener, initGadgetMixin));
