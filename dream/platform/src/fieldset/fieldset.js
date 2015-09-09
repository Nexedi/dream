/*global rJS, RSVP, jQuery, Handlebars,
  promiseEventListener, initGadgetMixin*/
/*jslint nomen: true */
(function (window, rJS, RSVP, Handlebars, initGadgetMixin) {
  "use strict";

  /////////////////////////////////////////////////////////////////
  // Handlebars
  /////////////////////////////////////////////////////////////////
  // Precompile the templates while loading the first gadget instance
  var gadget_klass = rJS(window),
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
        //console.log("addField", property_id, property_definition, value);
        queue
          .push(function () {
            gadget.props.fieldset_element.insertAdjacentHTML(
              'beforeend',
              label_template({
                "for": property_id,
                "name": ( property_definition.name ||
                          property_definition.description ||
                          property_id )
              })
            );
            // use expandable field if we have a oneOf in the schema
            if (property_definition.oneOf &&
                property_definition.properties &&
                Object.keys(property_definition.properties).length === 1) {
              property_definition = {
                allOf: [{properties: property_definition.properties},
                        { oneOf: property_definition.oneOf} ] };
              return gadget.declareGadget("../expandable_field/index.html");
            }
            if (property_definition.type === "object") {
              // Create a recursive fieldset for this key.
              return gadget.declareGadget("../fieldset/index.html");
            }
            if (property_definition.type === "number") {
              return gadget.declareGadget("../number_field/index.html");
            }
            if (property_definition.type === "integer") {
              return gadget.declareGadget("../integer_field/index.html");
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
            gadget.props.fieldset_element.appendChild(sub_element);
            gadget.props.field_gadget_list.push(sub_gadget);
          });
      }

      queue = new RSVP.Queue()
        .push(function () {
          var property_item_list = [], i, property_name, property_definition, value;
          //gadget.props.fieldset_element = document.createElement("fieldset");
          //gadget.props.element.appendChild(gadget.props.fieldset_element);
          gadget.props.fieldset_element = gadget.props.element;
          if (gadget.props.key) {
            // style only recursive fieldsets
            gadget.props.fieldset_element.style["border-width"] = "1px";
            gadget.props.fieldset_element.style["border-radius"] = "5px";
            gadget.props.fieldset_element.style.padding = "1px";
          }
          if (node_id) {
            addField('id', options.property_definition.properties.id || {'type': 'string'}, node_id);
          }

          Object.keys(options.property_definition.properties).forEach(function (property_name) {
            property_item_list.push([property_name, options.property_definition.properties[property_name]]);
          });
          /*
          * Sort properties so that higher priorities are displayed first.
          * If no priority is defined, sort by property id to have stable order.
          */
          property_item_list.sort(function(a, b) {
            var key_a = a[0], value_a = a[1],
                key_b = b[0], value_b = b[1];
            if (!isNaN(value_a.priority)) {
              if (!isNaN(value_b.priority)) {
                return value_b.priority - value_a.priority;
              }
              return -1;
            }
            if (!isNaN(value_b.priority)) {
              return 1;
            }
            return key_a < key_b ? -1 : (key_a > key_b ? 1 : 0);
          });

          for (i=0; i<property_item_list.length; i+=1) {
            property_name = property_item_list[i][0];
            property_definition = property_item_list[i][1];
            value = (options.value || {})[property_name] === undefined ?
                     property_definition.default : options.value[property_name];
            // XXX some properties are not editable
            // XXX should not be defined here
            if (property_name !== 'coordinate' &&
                property_name !== '_class' &&
                property_name !== 'id') {
              addField(property_name, property_definition, value);
            }
          }
        });
      return queue;
    })
    .declareMethod("startService", function () {
        var i, gadget=this,
        promise_list = [];
        for (i = 0; i < gadget.props.field_gadget_list.length; i += 1) {
          if (gadget.props.field_gadget_list[i].startService) {
            promise_list.push(
              gadget.props.field_gadget_list[i].startService()
            );
          }
        }
        return RSVP.all(promise_list);
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
