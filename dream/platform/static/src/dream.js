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

    priv.removeElement = function(element_id) {
      priv.plumb.removeElement(element_id);
    };

    priv.initDialog = function(title, element_id) {
      $( "#dialog-form" ).dialog({autoOpen: false});
    };

    priv.prepareDialogForElement = function(title, element_id) {
      // code to allow changing values on connections. For now we assume
      // that it is throughput. But we will need more generic code
      var throughput = $( "#throughput" ),
        allFields = $( [] ).add( throughput );
      $(function() {
        $( "input[type=submit]" )
          .button()
          .click(function( event ) {
            event.preventDefault();
          });
      });

      // Render fields for that particular element
      var fieldset = $("#dialog-fieldset");
      $("#dialog-fieldset").children().remove()
      var render_field = function(property_list, prefix) {
        if (prefix === undefined) {
          prefix = "";
        }
        _.each(property_list, function(property, key, list) {
          if (property._class === "Dream.Property") {
            fieldset.append("<label>" + prefix + property.id + "</label>" +
                            '<input type="text" name="' + property.id + '" id="' + property.id +
                            '" class="text ui-widget-content ui-corner-all"/>')
          } else if (property._class === "Dream.PropertyList") {
            var next_prefix = prefix + property.id + ".";
            render_field(property.property_list, next_prefix);
          }
        });
      };
      var element_id_prefix = element_id.split("_")[0];
      var property_list = configuration[element_id_prefix].property_list || [];
      console.log("property_list to be rendered", property_list);
      render_field(property_list);

      $( "#dialog-form" ).dialog({
        autoOpen: false,
        height: 300,
        width: 350,
        modal: true,
        title: title || "",
        buttons: {
          Cancel: function() {
            $( this ).dialog( "close" );
          },
          Delete: function() {
            console.log("Going to delete $(this)", $(this));
            priv.removeElement(element_id);
            $( this ).dialog( "close" );
          },
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
        },
        close: function() {
          allFields.val( "" ).removeClass( "ui-state-error" );
        }
      });
    };

    Object.defineProperty(that, "newElement", {
      configurable: false,
      enumerable: false,
      writable: false,
      value: function (element) {
        var element_id = element.id.split('_')[0]
        priv.plumb.newElement(element, configuration[element_id]);
        $("#" + element.id).bind('click', function() {
          console.log("bind click on window", $(this));
          //$("#dialog-form").attr("title", "bar");
          $( "#dialog-form" ).dialog( "destroy" ) ;
          priv.prepareDialogForElement(element.id, element.id);
          $( "#dialog-form" ).dialog( "open" );
        });
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
        priv.initDialog();
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