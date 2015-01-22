/*global rJS, RSVP, jQuery, Handlebars,
  promiseEventListener, initGadgetMixin*/
/*jslint nomen: true */
(function (window, rJS, RSVP, Handlebars, initGadgetMixin) {
  "use strict";

  /////////////////////////////////////////////////////////////////
  // Handlebars
  /////////////////////////////////////////////////////////////////
  // Precompile the templates while loading the first gadget instance
  var i, gadget_klass = rJS(window),
    source = gadget_klass.__template_element
                         .getElementById("label-template")
                         .innerHTML,
    label_template = Handlebars.compile(source);

  initGadgetMixin(gadget_klass);
  gadget_klass

    .declareMethod("render", function (options, node_id) {
      // XXX node_id is added like a property so that one can change the node
      // id
      var gadget = this,
        queue;

      gadget.props.key = options.key; // used for recursive fieldsets
      gadget.props.field_gadget_list = [];

      function addField(property_id, property_definition, value) {
        var sub_gadget;
        console.log("addField", property_id, property_definition, value);
        queue
          .push(function () {
            // XXX this is incorrect for recursive fieldsets.
            // we should use nested fieldset with legend
            gadget.props.element.insertAdjacentHTML(
              'beforeend',
              label_template({
                "for": property_id,
                "name": ( property_definition.name ||
                          property_definition.description ||
                          property_id )
              })
            );

            //console.log("PD", property_definition);
            if (property_definition.oneOf) {
              // if we got a oneOf, then we use the first one that matches our
              // data.
                console.log(value);
              for (i = 0; i < property_definition.oneOf.length; i += 1) {
                console.log(property_definition.oneOf[i]);

              };
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

      queue = new RSVP.Queue()
        .push(function () {
          if (node_id) {
            addField('id', {'type': 'string'}, node_id);
          }
          console.log(options.property_definition);
          Object.keys(options.property_definition.properties
            ).forEach(function (property_name) {
            var property_definition =
              options.property_definition.properties[property_name],
              value = (options.value || {})[property_name] === undefined
              ? property_definition._default : options.value[property_name];
            //console.log(property_name, property_definition);
            // XXX some properties are not editable
            // XXX should not be defined here
            if (property_name !== 'coordinate' &&
                property_name !== '_class' &&
                property_name !== 'id') {
              addField(property_name, property_definition, value);
            }
          });
        });
      return queue;
    })

    .declareMethod("notifyDataChanged", function () {
      console.log("content changed");
    })

    // getContent of all subfields
    .declareMethod("getContent", function () {
      var i, promise_list = [], gadget = this;
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
        });
    });


}(window, rJS, RSVP, Handlebars, initGadgetMixin));
