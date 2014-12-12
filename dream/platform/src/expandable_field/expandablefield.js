/*global rJS, RSVP, jQuery, Handlebars, loopEventListener,
  promiseEventListener, initGadgetMixin, console */
/*jslint nomen: true */
(function (window, rJS, RSVP, Handlebars, initGadgetMixin) {
  // loopEventListener) {
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

  /*function addField(gadget, property_id, property_definition, value) {
    console.log("ADDFIELD EXPANDABLEFIELDSET 1");
    console.log(gadget);
    var sub_gadget,
      queue = new RSVP.Queue();
    queue
      .push(function () {
        // XXX this is incorrect for recursive fieldsets.
        // we should use nested fieldset with legend
        console.log("EXPANDABLE insertingAdjacentHTML for:"
          + property_id);

        console.log(1111111111111);
        gadget.props.element.insertAdjacentHTML(
          'beforeend',
          label_template({
            "for": property_id,
            "name": (property_definition.name || property_id)
          })
        );
        console.log("ADDFIELD EXPANDABLEFIELDSET 2");
        if (property_definition.type === "object") {
          // Create a recursive fieldset for this key.
          console.log(1);
          return gadget.declareGadget("../fieldset/index.html");
        }
        if (property_definition.type === "number") {
          console.log(2);
          return gadget.declareGadget("../number_field/index.html");
        }
        if (property_definition.enum) {
          console.log(3);
          return gadget.declareGadget("../list_field/index.html");
        }
          console.log(4);
        return gadget.declareGadget("../string_field/index.html");
      })
      .push(function (gg) {
        console.log("ADDFIELD EXPANDABLEFIELDSET to render subgadgets");
        sub_gadget = gg;
        return sub_gadget.render({
          key: property_id,
          value: value,
          property_definition: property_definition
        });
      })
      .push(function () {
        console.log("ADDFIELD EXPANDABLEFIELDSET to get elements");	  
        return sub_gadget.getElement();
      })
      .push(function (sub_element) {
        console.log("ADDFIELD EXPANDABLEFIELDSET updating field_gadget_list");
        gadget.props.element.appendChild(sub_element);
        gadget.props.field_gadget_list.push(sub_gadget);
      });
  }*/

  function syncField(gadget) {
    console.log("SYNCFIELD EXPANDABLEFIELDSET 1");
    var i, properties_dict, //type, value, ind,
      // current_options = gadget.props.options.value,
      sub_title, sub_type, in_type, default_value, previous_value,
      labels, ins, j,
      recent_occupied = [],
      prop_name = gadget.props.definition.property_def.title;
    console.log(prop_name);
	// set the title of the field
    gadget.props.element.children[1].innerHTML = prop_name;
    gadget.props.element.children[1].setAttribute("for", prop_name);
    // sub fields set props.key correctly
    for (j = 0; j <= gadget.props.field_gadget_list.length-1; j +=1) {
      gadget.props.field_gadget_list[j].props.key = prop_name;
    }
    // un-hide the title of the field
    gadget.props.element.children[1].style.display = '';
    // if the gadget has properties defined (is an object with properties)
    if (gadget.props.definition.property_def.properties) {
      properties_dict = gadget.props.definition.property_def.properties;
      gadget.props.element.children[2].style.display = '';
      // XXX assuming that the number of labels
      //     is the same as the number of inputs
      ins = gadget.props.element.children[2]
                                   .getElementsByTagName("input");
      labels = gadget.props.element.children[2]
                                   .getElementsByTagName("label");
      for (i = 0; i <= Object.keys(properties_dict).length-1; i += 1) {
        sub_title = Object.keys(properties_dict)[i];
        console.log("sub_title");
        console.log(sub_title);
        sub_type = properties_dict[sub_title].type;
		default_value =  properties_dict[sub_title].default;
        // previous value
        if (gadget.props.options.value[prop_name]) {
          previous_value = gadget.props.options.value[prop_name][sub_title];
		}
        for (j = 0; j <= ins.length-1; j += 1) {
          // if the element is not already occupied
          if (!(recent_occupied.indexOf(ins[j]) > -1)) {
            if (ins[j].getAttribute("type")) {
              // XXX hardcoded value for string input 
              //  as text is used in HTML
              if (sub_type === "string") {in_type = "text"; }
              if (ins[j].getAttribute("type") === sub_type ||
                  ins[j].getAttribute("type") === in_type ) {
                ins[j].setAttribute("name", sub_title);
                ins[j].setAttribute("title", sub_title);
                // if (previous_value !== "undefined") 
                ins[j].setAttribute(
                  "value",
                  previous_value === undefined
                  ? default_value
                  : previous_value
                );
                labels[j].innerHTML = sub_title;
                labels[j].setAttribute('for', sub_title);
                recent_occupied.push(ins[j]);
                break;
              }
            }
          }
        }
      }
      console.log("occupied");
      console.log(recent_occupied);
      for (j = 0; j <= ins.length-1; j += 1) {
        if (!(recent_occupied.indexOf(ins[j]) > -1)) {
          ins[j].parentNode.parentNode.style.display = 'block';
          ins[j].parentNode.parentNode.style.display = 'none';
          labels[j].style.display = 'block';
          labels[j].style.display = 'none';
        }
      }
    }
  }

  /*function updateFieldSet(evt) {
    console.log("updateFieldSetupdateFieldSetupdateFieldSet");
    console.log(evt);
    console.log(this);
    console.log(this.props);
    var gadget = this,
      select = gadget.props.element.getElementsByTagName('select')[0],
      update_value = select.options[select.selectedIndex].value,
      options = gadget.props.options,
      i, select_index, child, index;
    for (select_index = 0; 
         select_index <= gadget.props.element.childNodes.length-1;
         select_index += 1) {
      child = gadget.props.element.childNodes[select_index];
      if (child.className === "ui-select") { select_index += 1; break; }
    }
    for (i = 0; i <= select_index; i += 1) {
      gadget.props.element.removeChild(gadget.props.element.lastChild);
    }
    for (index = 0;
         index <= options.property_definition.allOf.length - 1;
         index += 1) {
      if (options.property_definition.allOf[index].oneOf) {
        break;
      }
    }
    console.log(options.property_definition.allOf[index]);
    for (i = 0;
         i <= options.property_definition.allOf[index].oneOf.length - 1;
         i += 1) {
      if (options.property_definition.allOf[index].oneOf[i].title
          === update_value) {
        console.log(
          options.property_definition.allOf[index].oneOf[i].title,
          options.property_definition.allOf[index].oneOf[i],
          options.property_definition.allOf[index].oneOf[i].default
        );
        // addField(
          // gadget,
          // options.property_definition.allOf[index].oneOf[i].title,
          // options.property_definition.allOf[index].oneOf[i],
          // options.property_definition.allOf[index].oneOf[i].default
        // );
        break;
      }
    }
  }*/

  /*function waitForListFieldSelection(gadget) {
    var element = gadget.props.element.getElementsByTagName('select')[0];
    console.log("OLA Ta Mora stin pistaAaAaA");
    console.log(gadget);
    console.log(element);
    return loopEventListener(
      element,
      'change',
      false,
      updateFieldSet.bind(gadget)
    );
  }*/

  initGadgetMixin(gadget_klass);
  gadget_klass
    .declareMethod("render", function (options, node_id) {
      // XXX node_id is added like a property so that one can change the node
      // id
      var gadget = this,
        queue, index, len, ind, oneOf_list,
        req_props_sdict = {},
        ab_title, ab_definition, w,
        value, prop_name, prop_definition, string_value;

      console.log("EXPANDABLEFIELDSET RENDER 1");
      console.log(options);
      gadget.props.key = options.key; // used for recursive fieldsets
      gadget.props.field_gadget_list = [];
      // storing the options to the gadget properties
      // this way they are accessible methods external to render
      gadget.props.options = options;

      function addField(property_id, property_definition, value) {
        console.log("ADDFIELD EXPANDABLEFIELDSET 1");
        var sub_gadget;
        queue
          .push(function () {
            // XXX this is incorrect for recursive fieldsets.
            // we should use nested fieldset with legend
            console.log("EXPANDABLE insertingAdjacentHTML for:"
              + property_id);
            gadget.props.element.insertAdjacentHTML(
              'beforeend',
              label_template({
                "for": property_id,
                "name": (property_definition.name || property_id)
              })
            );
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

      ////////////////////////////////////////////////////////////////
      // function that finds the different types of fields that are 
      //  requested and calculates how many times each one of them 
      //  should be initiated 
      //  fields of type object are assumed to be all the same
      ////////////////////////////////////////////////////////////////
      function findRequestedTypes(oneOf_list) {
        var prop_dict, prop_list,
          prop_type_list, x, search_item,
          req_props_dlist = [],
          req_props_slist = [], 
          // req_props_sdict = {},
          counter, y,
          handleReduce = function (previous, current) {
            return previous > current ? previous : current;
          };
        /*////////////////////////////////////////////////////////////
        // find the different type of fields requested 
        // as well as the different fields for each different option*/
        for (ind = 0; ind <= oneOf_list.length - 1; ind += 1) {
          if (oneOf_list[ind].properties) {
            // dictionary of the properties of the spec item 
            prop_dict = oneOf_list[ind].properties;
            // list of properties keys of the spec item
            prop_list = Object.keys(prop_dict);
            // list of different properties of the spec item
            prop_type_list = [];
            ////////////////////////////////////////////////////////
            // XXX what if the type is object and there are other 
            //  different objects?
            //  We assume that in that case all objects
            //  the same definition
            ////////////////////////////////////////////////////////
            for (x = 0; x <= prop_list.length-1; x += 1) {
              search_item = prop_dict[prop_list[x]].type;
              prop_type_list.push(search_item);
              if (req_props_slist.indexOf(search_item) === -1) {
                // list of unique requested properties
                req_props_slist.push(prop_dict[prop_list[x]].type);
              }
            }
            // array of requested type-arrays for each different item
            req_props_dlist.push(prop_type_list);
          }
        }
        /////////////////////////////////////////////////////////////
        // find the maximum number of appearances 
        // for each requested type within req_props_dlist
        /////////////////////////////////////////////////////////////
        for (x = 0; x <= req_props_slist.length-1; x += 1){
          req_props_sdict[req_props_slist[x]] = [];
          for (ind = 0; ind <= req_props_dlist.length-1; ind += 1) {
            counter = 0;
            for (y = 0; y <= req_props_dlist[ind].length-1; y += 1) {
              if (req_props_slist[x] === req_props_dlist[ind][y]) {
                counter += 1;
              }
            }
            req_props_sdict[req_props_slist[x]].push(counter);
          }
        }
        for (ind = 0;
             ind <= Object.keys(req_props_sdict).length-1;
             ind += 1) {
          ////////////////////////////////////////////////////////////
          // key = Object.keys(req_props_sdict)[ind])
          // value = array of occurrences =
          //  req_props_sdict[Object.keys(req_props_sdict)[ind]]
          // find the maximum number within the array 
          //  and replace the array itself
          ////////////////////////////////////////////////////////////
          req_props_sdict[Object.keys(req_props_sdict)[ind]] =
            req_props_sdict[Object.keys(req_props_sdict)[ind]].reduce(
              handleReduce
            );
        }
        console.log("req_props_sdict");
        console.log(req_props_sdict);
      /////////////////////////////////////////////////////////////////
      }

      console.log("EXPANDABLEFIELDSET RENDER 2");
      queue = new RSVP.Queue()
        .push(function () {
          if (node_id) {
            // addField(gadget, 'id', {'type': 'string'}, node_id);
            addField('id', {'type': 'string'}, node_id);
          }
          if (!gadget.props.options.property_definition.allOf) {
            console.log("allOf must be used for expandable fields");
          }
          len = gadget.props.options.property_definition.allOf.length;
          for (index = 0; index <= len - 1; index += 1) {
            console.log("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=");
            console.log(gadget.props.options.
                               property_definition.allOf[index]);
            if (gadget.props.options
                      .property_definition.allOf[index].oneOf) {
              /* adding various hidden list fields */
              oneOf_list = gadget.props.options
                            .property_definition.allOf[index].oneOf;
              /* find what type and how many of which at maximum 
                 fields are requested */
              findRequestedTypes(oneOf_list);
              /* initiate the requested fields
               get a property definition for object-type fields
                req_props_sdict */
              ab_definition = {
                description: "",
                title: "field" + "_" + index,
                properties: {},
                type: "object"
              };
              for (ind = 0;
                   ind <= Object.keys(req_props_sdict).length-1;
                   ind += 1) {
                // create an abstract property definition (updated later)
                for (w = 0;
                     w <= req_props_sdict[Object.keys(req_props_sdict)[ind]]-1;
                     w += 1) {
                  ab_title = Object.keys(req_props_sdict)[ind] + "_" + w;
                  ab_definition.properties[ab_title] = {
                    type: Object.keys(req_props_sdict)[ind],
                    default: "",
                    description: "",
                    required: true
                  };
                }
              }
              console.log("ab_definition for " + index);
              console.log(ab_definition);
              // add a field with abstract definition
              addField(
                ab_definition.title,
                ab_definition,
                "undefined"
              );
              // find out if the oneOf_list item should be initiated 
              // (if it is the selected one (string_value))
              for (ind = 0; ind <= oneOf_list.length - 1; ind += 1) {
                if (oneOf_list[ind].title === string_value) {
                  value
                  = (gadget.props.options.value || {})[oneOf_list[ind].title]
                    === undefined
                    ? oneOf_list[ind].default
                    : gadget.props.options.value[oneOf_list[ind].title];
                  gadget.props.definition = {
                    name : oneOf_list[ind].title,
                    property_def : oneOf_list[ind],
                    value : value
                  };
                }
              }
            } else {
              // XXX add a listfield
              if (Object.keys(gadget.props.options.property_definition
                                    .allOf[index].properties).length !== 1) {
                console.log("the expandable property must be defined" + 
                            "as a string with single string property"); 
              }
              prop_name = Object.keys(gadget.props.options
                                            .property_definition
                                            .allOf[index].properties)[0];
              prop_definition = gadget.props.options
                                      .property_definition.allOf[index]
                                      .properties[prop_name];
              string_value = (gadget.props.options.value || {})[prop_name] 
                === undefined
                ? prop_definition.default
                : gadget.props.options.value[prop_name];
              addListField({
                key: prop_name,
                value: string_value,
                property_definition: prop_definition
              });
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
          console.log("Retrieving results from sub_fields");
          console.log(result_list);
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
          var keys, index, sub_keys, allowed_sub_keys = [], j;
          if (Object.keys(results).length !== 1) {
            console.log("the expandable property results must contain" + 
              "a single key of an object that can contain detailed results"); 
          }
          results[Object.keys(results)[0]][select.getAttribute('name')] =
            select.options[select.selectedIndex].value;
          keys = Object.keys(results[Object.keys(results)[0]]);
          console.log("modifying received results");
          /* results[Object.keys(results)[0]] :::::: is the result returned
		   keys[index] :::::: different keys of the result returned
           results[Object.keys(results)[0]][keys[index]] ::::::: 
                     the variable with key keys[index] */
          for (index = 0; index <= keys.length - 1; index +=1) {
            // if the type of the variable of the result is object
            if (typeof results[Object.keys(results)[0]][keys[index]]
                       === "object") {
              // hold the keys of that object
              sub_keys = Object.keys(
                results[Object.keys(results)[0]][keys[index]]
              );
              if (keys[index]
                          === gadget.props.definition.property_def.title) {
                if (gadget.props.definition.property_def.properties) {
                  // find the allowed keys according to the prop_definition
                  allowed_sub_keys 
                    = Object.keys(
                      gadget.props.definition.property_def.properties
                  );
                  for (j = 0; j <= sub_keys.length-1; j += 1) {
                    // if any of the keys is not in the allowed_sub_keys
                    if (!(allowed_sub_keys.indexOf(sub_keys[j]) > -1)) {
                      // remove it
                      delete results[
                               Object.keys(results)[0]
                             ][keys[index]][sub_keys[i]];
                    }
                  }
                }
              }
            }
            if (keys[index] !== select.options[select.selectedIndex].value &&
                keys[index] !== select.getAttribute('name')) {
              delete results[Object.keys(results)[0]][keys[index]];
              break;
            
            }
          }
          console.log("final results");
          console.log(results);
          return results;
        });
    })
    .declareMethod('startService', function () {
      console.log("STARTSERVICE EXPANDFIELD");
      var gadget = this,
        ind, sel_ind, sought_child;
      return RSVP.Queue()
        .push(function () {
          for (sel_ind = 0; 
               sel_ind <= gadget.props.element.children.length-1;
               sel_ind += 1) {
            sought_child = gadget.props.element.children[sel_ind];
            if (sought_child.className === "ui-select") {
              sel_ind += 1;
              break;
            }
          }
          for (ind = sel_ind; 
               ind <= gadget.props.element.children.length-1;
               ind += 1) {
            console.log("hiding :");
            gadget.props.element.children[ind].style.display = "block";
            gadget.props.element.children[ind].style.display = "none";
          }
        })
        .push(function () {
          console.log("STARTSERVICE EXPANDFIELD 1");
          syncField(gadget);
        })
        .push(function () {
          // waitForListFieldSelection(gadget);
          console.log("wait for selection ended");
        });
    });
}(window, rJS, RSVP, Handlebars, initGadgetMixin));//, loopEventListener));
