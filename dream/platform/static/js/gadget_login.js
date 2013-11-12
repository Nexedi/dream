/*global window, jQuery, rJS */
"use strict";
(function (window, $, rJS, undefined) {

  var gk = rJS(window);

  rJS(window).ready(function () {
    var g = rJS(this),
      form_context = g.context.find('form'),
      field_context = form_context.find("input[type=text]");

    function submit_event() {
      var jio_json = {
        "type": "local",
        "username": field_context.val()
      };
      // XXX What to do?
      g.context.text(JSON.stringify(jio_json));
      return false;
    }

    form_context.submit(submit_event);

  });

}(window, jQuery, rJS));
