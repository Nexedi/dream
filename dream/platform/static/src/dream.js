(function (scope, $, jsPlumb, console, _) {
  "use strict";
  var dream = function (configuration) {
    var that = {}, priv = {}, general = {};

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
        if (value[0] !== 'Dream-Configuration') { // XXX
          render_element.append('<div id="' + value[0] + '" class="tool">' +
                      value[0].split('-')[1] + "<ul/></div>");
        };
      });
    };

    priv.removeElement = function(element_id) {
      priv.plumb.removeElement(element_id);
    };

    priv.initDialog = function() {
      $( "#dialog-form" ).dialog({autoOpen: false});
    };

    priv.initGeneralProperties = function() {
      var fieldset = $("#general-fieldset"),
          previous_data = priv.plumb.getData()['general'],
          previous_value = "",
          prefix = "General-";
      fieldset.children().remove()
      $.each(configuration['Dream-Configuration']['property_list'],
        function(idx, property){
          if (property._class === "Dream.Property") {
            previous_value = previous_data[property.id] || "";
            if (previous_value.length > 0) {
              previous_value = ' value="' + previous_value + '"';
            }
            fieldset.append("<label>" + property.id + "</label>" +
                            '<input type="text" name="' + prefix + property.id + '"' +
                            previous_value + ' id="' + prefix + property.id + '"' +
                            ' class="text ui-widget-content ui-corner-all"/>');
      }});
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
      var previous_data = priv.plumb.getData()["element"];
      previous_data = previous_data[element_id] || {};
      previous_data = previous_data.data || {};
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
            if (confirm("Are you sure you want to delete " + element_id + " ?")) {
              priv.removeElement(element_id);
            }
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
        var element_prefix = element.id.split('_')[0]
        priv.plumb.newElement(element, configuration[element_prefix]);
        $("#" + element.id).bind('click', function() {
          console.log("bind click on window", $(this));
          $( "#dialog-form" ).dialog( "destroy" ) ;
          priv.prepareDialogForElement(element.id, element.id);
          $( "#dialog-form" ).dialog( "open" );
        });
        // Store default values
        var data = {}, property_list = configuration[element_prefix]["property_list"] || [];
        var updateDefaultData = function(data, property_list) {
          _.each(property_list, function(element, key) {
            console.log("going to parse property_list, element", element);
            if(element._class === "Dream.Property") {
              data[element.id] = element.default;
            } else if (element._class === "Dream.PropertyList") {
              data[element.id] = {};
              var next_data = data[element.id];
              var next_property_list = element.property_list || [];
              updateDefaultData(next_data, next_property_list);
            }
          });
        }
        updateDefaultData(data, property_list);
        priv.plumb.updateElementData(element.id, {data: data});

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
        // save general configuration default values
        var general_properties = {};
        _.each(configuration["Dream-Configuration"].property_list, function(element, key) {
          console.log("dream.start, parsing general property", element.id);
          general_properties[element.id] = element.default;
        });
        priv.plumb.setGeneralProperties(general_properties);
        priv.initGeneralProperties();
      }
    });

    Object.defineProperty(that, "initGeneralProperties", {
      configurable: false,
      enumerable: false,
      writable: false,
      value: function () {
        priv.initGeneralProperties();
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

    function formatForManpy(data) {
      var manpy_dict = {}, coreObject = [], core_object_dict = {};
      $.each(data['element'], function(idx, element) { 
        var clone_element = {};
        /* clone the element and put content of 'data' at the top level. */
        $.each(element, function(k, v) { 
          if (k == 'data') {
            $.each(v, function(kk, vv) { 
              clone_element[kk] = vv;
            });
          } else {
            clone_element[k] = v;
          }
        });
        clone_element['predecessorList'] = [];
        coreObject.push( clone_element );
        /* keep a mapping for predecessorList */
        core_object_dict[clone_element['id']] = clone_element;
      });

      /* calculate predecessorList from sucessorList.
       * In the future we have to update ManPy to use sucessorList only
       */
      $.each(core_object_dict, function(k, v) {
        $.each(v['successorList'] || [], function(i, successor) {
          core_object_dict[successor].predecessorList.push( k );
        });
      });

      manpy_dict['coreObject'] = coreObject;
      manpy_dict['modelResource'] = [];
      manpy_dict['general'] = data['general'];
      return manpy_dict;
    }

    that.setGeneralProperties = function(properties) {
      priv.plumb.setGeneralProperties(properties);
    }

    that.getData = function() { return priv.plumb.getData() };

    that.runSimulation = function(callback) {
       // handle Dream.General properties (in another function maybe ?)
       var prefix = "General-", properties = {}, prefixed_property_id;

      $.each(configuration['Dream-Configuration']['property_list'],
        function(idx, property){
          if (property._class === "Dream.Property") {
            prefixed_property_id = prefix + property.id;
            properties[property.id] = $("#" + prefixed_property_id).val();
          }
        });
       priv.plumb.setGeneralProperties(properties);

       var model = formatForManpy(priv.plumb.getData());
       $.ajax(
          '/runSimulation', {
          data: JSON.stringify({json: model}),
          contentType: 'application/json',
          type: 'POST',
          success: function(data, textStatus, jqXHR){
            callback(data);
          }
      });
    };


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
