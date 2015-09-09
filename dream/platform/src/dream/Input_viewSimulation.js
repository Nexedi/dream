/*global rJS, RSVP, jQuery, promiseEventListener, initGadgetMixin, alert */
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
    var result_json;
    return new RSVP.Queue()
      .push(function () {
        return gadget.aq_getAttachment({
          "_id": gadget.props.jio_key,
          "_attachment": "body.json"
        });
      })
      .push(function (body_json) {
        // do not send previous results to simulation engine
        var json_without_result = JSON.parse(body_json);
        json_without_result.result.result_list = [];
        // XXX Hardcoded relative URL
        return gadget.aq_ajax({
          url: "../../runSimulation",
          type: "POST",
          data: JSON.stringify(json_without_result),
          headers: {
            "Content-Type": 'application/json'
          }
        });
      })
      .push(function (evt) {
        result_json = JSON.parse(evt.target.responseText);
        if (result_json.success !== true) {
          throw new Error(result_json.error);
        }
        // get latest version
        return gadget.aq_getAttachment({
          "_id": gadget.props.jio_key,
          "_attachment": "body.json"
        });
      }).push(function(data){
        data = JSON.parse(data);
        if (!data.result.result_list) {
          data.result.result_list = [];
        }
        // XXX option to always add ?
        if (data.general.reset_result_list) {
          data.result.result_list = [];
        }
        data.result.result_list = [];
        data.result.result_list = data.result.result_list.concat(
          result_json.data.result.result_list
        );
        return gadget.aq_putAttachment({
          "_id": gadget.props.jio_key,
          "_attachment": "body.json",
          "_data": JSON.stringify(data, null, 2),
          "_mimetype": "application/json"
        }).fail(function(reason){
          alert("Could not save simulation results.Please check the simulation parameters or try to delete some models.\n\nError was:" + reason);
          return gadget.whoWantsToDisplayThisDocument(
            gadget.props.jio_key,
            "view"
          );
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
