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

    .declareMethod("render", function (property_list, data, key) {
      var gadget = this,
        queue,
        value,
        property;

      gadget.key = key; // used for recursive fieldsets
      gadget.props.field_gadget_list = [];
      function addField(property, value) {
        var sub_gadget;
        queue
          .push(function () {
            // XXX this is incorrect for recursive fieldsets.
            // we should use nested fieldset with legend
            gadget.props.element.insertAdjacentHTML(
              'beforeend',
              label_template({
                "for": property.id,
                "name": (property.name || property.id)
              })
            );
            if (property._class === "Dream.PropertyList") {
              // Create a recursive fieldset for this key.
              return gadget.declareGadget("../fieldset/index.html");
            }
            if (property.type === "number") {
              return gadget.declareGadget("../number_field/index.html");
            }
            if (property.choice) {
              return gadget.declareGadget("../list_field/index.html");
            }
            return gadget.declareGadget("../string_field/index.html");
          })
          .push(function (gg) {
            sub_gadget = gg;
            var choice = property.choice || [],
              default_opt = choice[0] ? [choice[0][1]] : [""];
            value = (data[property.id] === undefined ?
                      value : data[property.id]);
            if (gg.__title === 'Fieldset') {
              // XXX there must be a better way instead of using __title ?
              return gg.render(property.property_list, value, property.id);
            }
            return sub_gadget.render({field_json: {
              title: (property.description || ''),
              key: property.id,
              value: value,
              items: choice,
              default: default_opt
            }});
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
          Object.keys(property_list).forEach(function (i) {
            property = property_list[i];
            value = property._default === undefined ? "" : property._default;
            addField(property, value);
          });
        });

      return queue;
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
          if (gadget.key) {
            content = result[gadget.key] = {};
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
