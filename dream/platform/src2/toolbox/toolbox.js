/*global window, document, RSVP, rJS, Handlebars*/
(function (window, document, RSVP, rJS, Handlebars) {
  "use strict";
  /*jslint nomen: true*/
  var gadget_klass = rJS(window),
    tool_template_source = gadget_klass.__template_element
      .getElementById('tool-template').innerHTML,
    tool_template = Handlebars.compile(tool_template_source);


  gadget_klass

    .declareAcquiredMethod("getConfigurationDict", "getConfigurationDict")

    .declareMethod("render", function () {
      var g = this;
      return new RSVP.Queue()
        .push(function () {
          return g.getConfigurationDict();
        })
        .push(function (config) {
          g.tools_container = document.createElement('div');
          g.tools_container.className = 'tools-container';
          Object.keys(config).forEach(function (key) {
            var name = config[key].name || key.split('-')[1];
            if (key !== 'Dream-Configuration') {
              g.tools_container.innerHTML += tool_template({
                key: key,
                name: name
              });
            }
          });
        });
    })

    .declareMethod('startService', function () {
      var g = this;
      return g.getElement().then(function (element) {
        element.querySelector('.tools')
          .appendChild(g.tools_container);
      });
    });

}(window, document, RSVP, rJS, Handlebars));
