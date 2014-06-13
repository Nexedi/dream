/*global rJS, RSVP, initDocumentPageMixin, jQuery, Handlebars,
  promiseEventListener, initGadgetMixin */
/*jslint nomen: true */
(function (window, rJS, RSVP, initDocumentPageMixin, $, Handlebars,
           promiseEventListener, initGadgetMixin) {
  "use strict";

  /////////////////////////////////////////////////////////////////
  // Handlebars
  /////////////////////////////////////////////////////////////////
  // Precompile the templates while loading the first gadget instance
  var gadget_klass = rJS(window),
    source = gadget_klass.__template_element
                         .getElementById("label-template")
                         .innerHTML,
    label_template = Handlebars.compile(source);

  initGadgetMixin(gadget_klass);
  initDocumentPageMixin(gadget_klass);
  gadget_klass
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("aq_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("aq_putAttachment", "jio_putAttachment")
    .declareAcquiredMethod("aq_ajax", "jio_ajax")
    .declareAcquiredMethod("pleaseRedirectMyHash", "pleaseRedirectMyHash")
    .declareAcquiredMethod("whoWantToDisplayThisDocumentPage",
                           "whoWantToDisplayThisDocumentPage")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function (options) {
      var i,
        gadget = this,
        property,
        parent_element = gadget.props.element
          .querySelector(".simulation_parameters"),
        value,
        queue,
        data,
        property_list =
          options.configuration_dict['Dream-Configuration'].property_list;

      this.props.jio_key = options.id;

      queue = gadget.aq_getAttachment({
        "_id": gadget.props.jio_key,
        "_attachment": "body.json"
      })
        .push(function (json) {
          data = JSON.parse(json).general;
        });

      function addField(property, value) {
        var sub_gadget;
        queue
          .push(function () {
            parent_element.insertAdjacentHTML(
              'beforeend',
              label_template({label: (property.name || property.id)})
            );
            return gadget.declareGadget("../string_field/index.html");
          })
          .push(function (gg) {
            sub_gadget = gg;
            value = data[property.id] || value;
            return sub_gadget.render({field_json: {
              title: (property.description || ''),
              key: property.id,
              value: value
            }});
          })
          .push(function () {
            return sub_gadget.getElement();
          })
          .push(function (sub_element) {
            parent_element.appendChild(sub_element);
          });
      }

      for (i = 0; i < property_list.length; i += 1) {
        property = property_list[i];
        if (property._class === "Dream.Property") {
          value = property._default || "";
          addField(property, value);
        }
      }

      return queue;
    })

    .declareMethod("startService", function () {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return promiseEventListener(
            gadget.props.element.getElementsByClassName("run_form")[0],
            'submit',
            false
          );
        })
        .push(function () {
          // Prevent double click
          gadget.props.element
            .getElementsByClassName("ui-btn")[0].disabled = true;

          return gadget.aq_getAttachment({
            "_id": gadget.props.jio_key,
            "_attachment": "body.json"
          });
        })
        .push(function (body_json) {
          $.mobile.loading('show');
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
        .push(undefined, function (error) {
          // Always drop the loader
          $.mobile.loading('hide');
          throw error;
        })
        .push(function (evt) {
          $.mobile.loading('hide');
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
        .push(function (result) {
          return gadget.whoWantToDisplayThisDocumentPage(
            "debug_json",
            gadget.props.jio_key
          );
        })
        .push(function (url) {
          return gadget.pleaseRedirectMyHash(url);
        });
    });
}(window, rJS, RSVP, initDocumentPageMixin, jQuery, Handlebars,
  promiseEventListener, initGadgetMixin));
