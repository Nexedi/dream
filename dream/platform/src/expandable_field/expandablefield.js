/*global rJS, RSVP, jQuery, Handlebars,
  promiseEventListener, initGadgetMixin, console */
/*jslint nomen: true */
(function (window, rJS, RSVP, Handlebars, initGadgetMixin) {
  "use strict";

  /////////////////////////////////////////////////////////////////
  // Handlebars
  /////////////////////////////////////////////////////////////////
  // Precompile the templates while loading the first gadget instance
  var gadget_klass = rJS(window),
    label_source = gadget_klass.__template_element
                         .getElementById("expand-label-template")
                         .innerHTML,
    label_template = Handlebars.compile(label_source),
    option_source = gadget_klass.__template_element
                      .getElementById("expand-option-template")
                      .innerHTML,
    option_template = Handlebars.compile(option_source),
    selected_option_source = gadget_klass.__template_element
                         .getElementById("selected-expand-option-template")
                           .innerHTML,
    selected_option_template = Handlebars.compile(selected_option_source);

  initGadgetMixin(gadget_klass);
  gadget_klass

    .declareMethod("render", function (options, node_id) {
      // XXX node_id is added like a property so that one can change the node
      // id
      var gadget = this,
        queue, j, len, ind, oneOf, value;

      console.log("EXPANDABLEFIELDSET RENDER 1");
      console.log(options);
      gadget.props.key = options.key; // used for recursive fieldsets
      gadget.props.field_gadget_list = [];

      function addField(property_id, property_definition,
                                     value) {
        console.log("ADDFIELD EXPANDABLEFIELDSET 1");
        var sub_gadget, temp_property_def;
        queue
          .push(function () {
            // XXX this is incorrect for recursive fieldsets.
            // we should use nested fieldset with legend
            console.log("EXPANDABLE insertingAdjacentHTML for:" + property_id);
            gadget.props.element.insertAdjacentHTML(
              'beforeend',
              label_template({
                "for": property_id,
                "name": (property_definition.name || property_id)
              })
            );
            if (property_definition.allOf) {
              if (property_definition.allOf[0].type) {
                delete property_definition.allOf[0].type;
              }
              temp_property_def = property_definition.allOf[0];
              return gadget.declareGadget("../list_field/index.html");
            }
            if (property_definition.type === "object") {
              // Create a recursive fieldset for this key.
              return gadget.declareGadget("../fieldset/index.html");
            }
            if (property_definition.type === "number") {
              return gadget.declareGadget("../number_field/index.html");
            }
            if (property_definition.enum) {
              return gadget.declareGadget("../list_field/index.html");
            }
            return gadget.declareGadget("../string_field/index.html");
          })
          .push(function (gg) {
            sub_gadget = gg;
            if (temp_property_def) {
              return sub_gadget.render({
                key: property_id,
                value: value,
                property_definition: temp_property_def
              });
            }
            return sub_gadget.render({
              key: property_id,
              value: value,
              property_definition: property_definition
            });
          })
          .push(function () {
            return sub_gadget.getElement();
          })
          .push(function (sub_element) {
            gadget.props.element.appendChild(sub_element);
            gadget.props.field_gadget_list.push(sub_gadget);
          });
      }

      function addListField(options) {
        console.log("ADDLISTFIELD EXPANDABLEFIELDSET 1");
        var select = gadget.props.element.getElementsByTagName('select')[0],
          i,
          template,
          tmp = '';
        select.setAttribute('name', options.key);
        for (i = 0; i < options.property_definition.enum.length; i += 1) {
          if (options.property_definition.enum[i] === options.value) {
            template = selected_option_template;
          } else {
            template = option_template;
          }
          // XXX value and text are always same in json schema
          tmp += template({
            value: options.property_definition.enum[i],
            text: options.property_definition.enum[i]
          });
        }
        select.innerHTML += tmp;
      }

      function createListField(index) {
        console.log("CREATELISTFIELD EXPANDABLEFIELDSET 1");
        var property_name, property_definition;//, temp_length, temp_value;
        if ( Object.keys(options.property_definition.allOf[index].properties)
                   .length !== 1) {
          console.log("the expandable property must be defined" + 
                      "as a string with single string property"); 
        }
        property_name = Object.keys(options.property_definition
                                           .allOf[index].properties)[0];
        property_definition = options.property_definition.allOf[index]
                                     .properties[property_name];
        value = property_definition.default;
        value = (options.value || {})[property_name] === undefined
          ? value : options.value[property_name];
        addListField({
          key: property_name,
          value: value,
          property_definition: property_definition
        });
      }

      queue = new RSVP.Queue()
        .push(function () {
          if (node_id) {
            addField('id', {'type': 'string'}, node_id);
          }
          if (!options.property_definition.allOf) {
            console.log("allOf must be used for expandable fields");
          }
          console.log("RENDER EXPANDABLEFIELDSET 2");
          len = options.property_definition.allOf.length;
          // console.log("the length is equal to " + len);
          for (j = 0; j <= len - 1; j += 1) {
            if (options.property_definition.allOf[j].oneOf) {
              // XXX adding various hidden list fields
              // console.log("======== adding hidden list fields ========");
              oneOf = options.property_definition.allOf[j].oneOf;
              for (ind = 0; ind <= oneOf.length - 1; ind += 1) {
                value = oneOf[ind].default;
                value = (options.value || {})[oneOf[ind].title] === undefined
                  ? value : options.value[oneOf[ind].title];
                addField(oneOf[ind].title, oneOf[ind], value);
              }
            } else {
              // XXX add a listfield
              createListField(j);
            }
          }
        });
      return queue;
    })

    // getContent of all subfields
    .declareMethod("getContent", function () {
      console.log("GETCONTENT EXPANDABLEFIELDSET 1");
      var i, promise_list = [], gadget = this,
        select = gadget.props.element.getElementsByTagName('select')[0];
      for (i = 0; i < this.props.field_gadget_list.length; i += 1) {
        promise_list.push(this.props.field_gadget_list[i].getContent());
      }
      return RSVP.Queue()
        .push(function () { return RSVP.all(promise_list); })
        .push(function (result_list) {
          var name, result = {}, content = result;
          if (gadget.props.key) {
            content = result[gadget.props.key] = {};
          }
          for (i = 0; i < result_list.length; i += 1) {
            for (name in result_list[i]) {
              if (result_list[i].hasOwnProperty(name)) {
                content[name] = result_list[i][name];
              }
            }
          }
          return result;
        })
        .push(function (results) {
          // console.log(results);
          if (Object.keys(results).length !== 1) {
            console.log("the expandable property results must contain" + 
              "a single key of an object that can contain detailed results"); 
          }
          results[Object.keys(results)[0]][select.getAttribute('name')] =
            select.options[select.selectedIndex].value;
          console.log(results);
          return results;
        });
    })


    .declareMethod('startService', function () {
      console.log("STARTSERVICE EXPANDFIELD");
      var gadget = this;
      function waitForListFieldSelection(gadget) {
        console.log("OLA OMORFA OLA OMORFA");
        console.log(gadget);
      }


      return RSVP.Queue()
        .push(function () {
          waitForListFieldSelection(gadget); 
        });
    });

}(window, rJS, RSVP, Handlebars, initGadgetMixin));
