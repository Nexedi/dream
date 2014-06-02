/*global window, jQuery, rJS */
"use strict";
(function (window, $, rJS) {

  $.mobile.ajaxEnabled = false;
  $.mobile.linkBindingEnabled = false;
  $.mobile.hashListeningEnabled = false;
  $.mobile.pushStateEnabled = false;

  rJS(window).ready(function () {
    var g = rJS(this),
      body = g.context,
      main_context = g.context.find('.ui-content').first(),
      ioGadgetConfig = {"type": "local",
                        "username": "officejs",
                        "application_name": "officejs"
                       },
      jioGadget;

    function setTitle(title) {
      g.context.find("#headergadget").find("h1").text(title);
      return $('title').text("OfficeJS | " + title);
    }

    function enhanceGadgetRendering(gadget) {
      gadget.context.enhanceWithin();
      return gadget.getTitle()
        .then(setTitle);
    }

    function registerSaveButton(gadget) {
      window.jqs = gadget;
      $("#save-doc").click(function () {
        var fileName = $("#iogadget input").val();
        jioGadget.configureIO(ioGadgetConfig, fileName)
          .then(gadget.getContent)
          .then(function (o) {jioGadget.setIO(o); });
      });
      return gadget;
    }

    function registerLoadButton(gadget) {
      $("#load-doc").click(function () {
        var fileName = $("#iogadget input").val();
        jioGadget.configureIO(ioGadgetConfig, fileName)
          .then(jioGadget.getIO)
          .then(gadget.setContent);
      });
      return gadget;
    }

    function registerClearButton(gadget) {
      $("#new-doc").click(function () {
        gadget.clearContent();
      });
    }

    function registerIOButtons(gadget) {
      registerSaveButton(gadget);
      registerLoadButton(gadget);
      registerClearButton(gadget);
    }

    function initializeRoute() {
      body
        .route("add", "", 1)
        .done(function () {
          $.url.redirect('/login/');
        });

      body
        .route("add", "/about/", 1)
        .done(function () {
          g.declareGadget('./about.html', main_context)
            .then(enhanceGadgetRendering);
        });

      body
        .route("add", "/contact/", 1)
        .done(function () {
          g.declareGadget('./contact.html', main_context)
            .then(enhanceGadgetRendering);
        });

      body
        .route("add", "/login/", 1)
        .done(function () {
          g.declareGadget('./login.html', main_context)
            .then(enhanceGadgetRendering);
        });

      body
        .route("add", "/graph/", 1)
        .done(function () {
          g.declareIframedGadget('./graph.html', main_context)
            .then(registerIOButtons);
        });

      body
        .route("add", "/simulation/", 1)
        .done(function () {
          g.declareIframedGadget('./simulation.html', main_context)
            .then(registerIOButtons);
        });
    }

    g.declareGadget('./io.html', g.context.find("#iogadget"))
      .done(function (ioGadget) {
        window.jio = ioGadget;
        jioGadget = ioGadget;
        // Trigger route change
        initializeRoute();
        $.url.onhashchange(function () {
          body.route("go", $.url.getPath())
            .fail(function () {
              g.declareGadget('./error.html', main_context)
                .then(enhanceGadgetRendering)
                .then(initializeRoute);
            });
        });
      });
  });

}(window, jQuery, rJS));
