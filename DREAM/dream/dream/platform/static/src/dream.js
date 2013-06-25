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

    priv.initDialog = function() {
      // code to allow changing values on connections. For now we assume
      // that it is throughput. But we will need more generic code
      var throughput = $( "#throughput" ),
        allFields = $( [] ).add( throughput ),
        tips = $( ".validateTips" );

      function updateTips( t ) {
        tips
          .text( t )
          .addClass( "ui-state-highlight" );
        setTimeout(function() {
          tips.removeClass( "ui-state-highlight", 1500 );
        }, 500 );
      }

      function checkLength( o, n, min, max ) {
        if ( o.val().length > max || o.val().length < min ) {
          o.addClass( "ui-state-error" );
          updateTips( "Length of " + n + " must be between " +
            min + " and " + max + "." );
          return false;
        } else {
          return true;
        }
      }

      function checkRegexp( o, regexp, n ) {
        if ( !( regexp.test( o.val() ) ) ) {
          o.addClass( "ui-state-error" );
          updateTips( n );
          return false;
        } else {
          return true;
        }
      }    

      $( "#dialog-form" ).dialog({
        autoOpen: false,
        height: 300,
        width: 350,
        modal: true,
        buttons: {
          "Validate": function() {
            var bValid = true, i, i_length, box;
            allFields.removeClass( "ui-state-error" );
  
            bValid = bValid && checkRegexp( throughput, /^([0-9])+$/, "Througput must be integer." );
  
            if ( bValid ) {
              // Update the model with new value
              i_length = model.box_list.length;
              for (i = 0; i < i_length; i++) {
                box = model.box_list[i];
                if (box.id === priv.box_id) {
                  box.throughput = parseInt(throughput.val(), 10);
                }
              }
              priv.updateModel();
              $( this ).dialog( "close" );
            }
          },
          Cancel: function() {
            $( this ).dialog( "close" );
          }
        },
        close: function() {
          allFields.val( "" ).removeClass( "ui-state-error" );
        }
      });
    };

    // Prevent enter key to do nasty things
    $('#dialog-form :input').on("keypress", function(e) {
      console.log("keyup, e", e);
      return e.keyCode !== 13;
    });

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

    Object.defineProperty(that, "newElement", {
      configurable: false,
      enumerable: false,
      writable: false,
      value: function (element) {
        var element_id = "Dream." + element.id.split('_')[0];
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
      }
    });

    Object.defineProperty(that, "setSimulationParameters", {
      configurable: false,
      enumerable: false,
      writable: false,
      value: function (simulation_parameters) {
        priv.setSimulationParameters(simulation_parameters);
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