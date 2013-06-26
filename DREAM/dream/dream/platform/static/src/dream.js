(function (scope, $, jsPlumb, console, _) {
  "use strict";
  var dream = function (configuration) {
    var that = {}, priv = {};

    priv.onError = function(error) {
       console.log("Error", error);
    };

    priv.getUrl = function() {
      return "/";
    };

    // Utility function to update the style of a box
    priv.updateBoxStyle = function (box_id, style) {
      var box;
      box = $("#" + box_id);
      _.each(style, function(value, key, list) {
        box.css(key, value);
      })
    };

    // Utility function to update the content of the box
    priv.updateBoxContent = function (box_id, title, throughput, worker) {
      var box, html_string;
      box = $("#" + box_id);
      html_string = "<strong>" + title + "</strong>";
      if (worker !== undefined && worker !== null) {
        html_string += "<br> (" + worker + ")";
      }
      html_string += "<br><strong>througput: " + throughput + "</strong>";
      box.html(html_string);
    };

    priv.displayTool = function() {
      var render_element = $("[id=tools]");
      _.each(_.pairs(configuration), function(value, key, list) {
        render_element.append('<div id="' + value[0] + '" class="tool">' +
                    value[0].split('-')[1] +
                    "<ul/></div>");
      });
    };

    Object.defineProperty(that, "newElement", {
      configurable: false,
      enumerable: false,
      writable: false,
      value: function (element) {
        var element_id = element.id.split('_')[0]
        priv.plumb.newElement(element, configuration[element_id]);
      }
    });

    Object.defineProperty(that, "start", {
      configurable: false,
      enumerable: false,
      writable: false,
      value: function () {
        priv.plumb = jsonPlumb.newJsonPlumb();
        priv.plumb.start();
        priv.displayTool();
      }
    });

    Object.defineProperty(that, "connect", {
      configurable: false,
      enumerable: false,
      writable: false,
      value: function (source_id, target_id) {
        priv.plumb.connect(source_id, target_id);
      }
    });

    return that;
  };
  var DreamNamespace = (function () {
    var that = {};

    /**
    * Creates a new dream instance.
    * @method newDream
    * @param  {object} model The model definition
    * @return {object} The new Dream instance.
    */
    Object.defineProperty(that, "newDream", {
      configurable: false,
      enumerable: false,
      writable: false,
      value: function (configuration) {
        var instance = dream(configuration);
        return instance;
      }
    });

    return that;
  })();

  Object.defineProperty(scope, "DREAM", {
    configurable: false,
    enumerable: false,
    writable: false,
    value: DreamNamespace
  });

}(window, jQuery, jsPlumb, console, _));