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
      //var throughput = $( "#throughput" ),
      //  allFields = $( [] ).add( throughput );
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
      var element_id_prefix = element_id.split("_")[0];
      var property_list = configuration[element_id_prefix].property_list || [];
      console.log("getData on element_id", element_id);
      var previous_data = priv.plumb.getData()["element"];
      previous_data = previous_data[element_id] || {};
      previous_data = previous_data.data || {};
      console.log("previous_data", previous_data);
      var previous_value;
      var renderField = function(property_list, previous_data, prefix) {
        if (prefix === undefined) {
          prefix = "";
        }
        _.each(property_list, function(property, key, list) {
          if (property._class === "Dream.Property") {
            console.log("property.id, previous_data", property.id, previous_data);
            previous_value = previous_data[property.id] || "";
            if (previous_value.length > 0) {
              previous_value = ' value="' + previous_value + '"';
            }
            //previous_value = ' value="bar"';
            console.log("previous_value");
            fieldset.append("<label>" + prefix + property.id + "</label>" +
                            '<input type="text" name="' + prefix + property.id + '"' +
                            previous_value +
                            ' id="' + prefix + property.id + '"' +
                            ' class="text ui-widget-content ui-corner-all"/>')
          } else if (property._class === "Dream.PropertyList") {
            var next_prefix = prefix + property.id + "-";
            var next_previous_data = previous_data[property.id] || {};
            console.log("next_previous_data", next_previous_data);
            renderField(property.property_list, next_previous_data, next_prefix);
          }
        });
      };
      console.log("property_list to be rendered", property_list);
      renderField(property_list, previous_data);

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
          Validate: function() {
            var data = {}, prefixed_property_id, property_element;
            var updateDataPropertyList = function(property_list, data, prefix) {
              console.log("updateDataPropertyList, property_list", property_list);
              if (prefix === undefined) {
                prefix = "";
              }
              _.each(property_list, function(property, key, list) {
                if (property._class === "Dream.Property") {
                  prefixed_property_id = prefix + property.id;
                  console.log("prefixed_property_id", prefixed_property_id);
                  property_element = $("#" + prefixed_property_id);
                  data[property.id] = property_element.val();
                } else if (property._class === "Dream.PropertyList") {
                  var next_prefix = prefix + property.id + "-";
                  data[property.id] = {};
                  updateDataPropertyList(property.property_list, data[property.id], next_prefix);
                }
              });
            };
            updateDataPropertyList(property_list, data);
            priv.plumb.updateElementData(element_id, {data: data});
            $( this ).dialog( "close" );
          },
        },
        close: function() {
          //allFields.val( "" ).removeClass( "ui-state-error" );
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

    Object.defineProperty(that, "updateElementData", {
      configurable: false,
      enumerable: false,
      writable: false,
      value: function (element_id, data) {
        priv.plumb.updateElementData(element_id, data);
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