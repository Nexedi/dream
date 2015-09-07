/*global rJS, RSVP, jQuery, Handlebars, loopEventListener,
  promiseEventListener, initGadgetMixin, console */
/*jslint nomen: true */
(function (window, rJS, RSVP, Handlebars, initGadgetMixin,
           loopEventListener) {
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

  function syncField(gadget) {
    var i, properties_dict, sub_title_name,
      sub_title, sub_type, in_type, default_value, previous_value,
      labels = [], lbls, inps = [], inputs, j,
      index, corresponding_input, sub_gadget_list = [], old_title,
      recent_occupied = [],
      recent_occupied_labels = [],
      prop_name = gadget.props.definition.property_def.title;
    console.log("for prop_name syncField");
    console.log(prop_name);
	
	// set the title of the field
    gadget.props.element.children[1].innerHTML = prop_name;
    gadget.props.element.children[1].setAttribute("for", prop_name);
    // sub fields set props.key correctly
    // find any sub_sub_gadgets if any
    for (j = 0; j <= gadget.props.field_gadget_list.length-1; j +=1) {
      gadget.props.field_gadget_list[j].props.key = prop_name;
      if (gadget.props.field_gadget_list[j].props.field_gadget_list) {
        for (i = 0;
             i <= gadget.props.field_gadget_list[j]
                        .props.field_gadget_list.length-1;
             i += 1) {
          // if the sub-gadget has itself a field_gadget_list : 
          //  thus is a expandable field itself
          if (gadget.props.field_gadget_list[j]
              .props.field_gadget_list[i].props) {
            if (gadget.props.field_gadget_list[j]
                .props.field_gadget_list[i].props.field_gadget_list) {
              sub_gadget_list.push(gadget.props.field_gadget_list[j]
                                         .props.field_gadget_list[i]);
            }
          }
        }
      }
    }
    // un-hide the title of the field
    // gadget.props.element.children[1].style.display = '';
    // if the gadget has properties defined (is an object with properties)
    if (gadget.props.definition.property_def.properties) {
      properties_dict = gadget.props.definition.property_def.properties;
      gadget.props.element.children[2].style.display = '';
      inputs = gadget.props.element.children[2]
                                   .getElementsByTagName("input");
      // find the inputs that are direct children of the gadgets element
      for (i = 0; i <= inputs.length-1; i += 1) {
        if (inputs[i].parentNode.parentNode.parentNode ===
            gadget.props.element.children[2]) {
          inps.push(inputs[i]);
        }
      }
      lbls = gadget.props.element.children[2]
                                   .getElementsByTagName("label");
      // find the labels that are direct children of the gadgets element
      for (i = 0; i <= lbls.length-1; i += 1) {
        if (lbls[i].parentNode ===
            gadget.props.element.children[2]) {
          labels.push(lbls[i]);
        }
      }

      for (i = 0; i <= Object.keys(properties_dict).length-1; i += 1) {
        sub_title = Object.keys(properties_dict)[i];
        console.log("sub_title");
        console.log(sub_title);
        sub_type = properties_dict[sub_title].type ||
          (properties_dict[sub_title].allOf ?
            "allOf" : undefined);
        // if the gadget contains expandable inputs (allOf)
        // find the labels of that inputs
        if (properties_dict[sub_title].allOf) {
          for (j = 0; j <= labels.length-1; j += 1) {

            if (!(recent_occupied_labels.indexOf(labels[j]) > -1)) {
              // for that label, find if it is assigned to any input
              // proceed only if no input is assigned to it
              corresponding_input = false;
              for (index = 0; index <= inps.length-1; index += 1) {
                if (labels[j].getAttribute("for")
                    === inps[index].getAttribute("title")) {
                  corresponding_input = true;
                }
              }
              if (! corresponding_input) {
                old_title 
                  = JSON.parse(JSON.stringify(labels[j].getAttribute("for")));
                // if the old title of the label is the same with the key
                // of the subsubgadget then update the key of the subsubgadget
                for (index = 0;
                     index <= sub_gadget_list.length-1;
                     index += 1) {
                  if (sub_gadget_list[index].props.key === old_title) {
                    sub_gadget_list[index].props.key = sub_title;
                    break;
                  }
                }
                labels[j].innerHTML = sub_title;
                labels[j].setAttribute("for", sub_title);
                recent_occupied_labels.push(labels[j]);
                break;
              }
            }
          }
        }

		default_value =  properties_dict[sub_title].default;
        // find previous value if any
        if (gadget.props.options.value && gadget.props.options.value[prop_name]) {
          if (gadget.props.options.value[prop_name][sub_title] ||
              gadget.props.options.value[prop_name][sub_title] === "") {
            previous_value = gadget.props.options.value[prop_name][sub_title];
          }
		}
   sub_title_name = properties_dict[sub_title].name || sub_title;
    
        for (j = 0; j <= inps.length-1; j += 1) {
          // check if the input is one of a sub-gadget
          // do not proceed if yes
          if (inps[j].parentNode.parentNode.parentNode ===
              gadget.props.element.children[2]) {
            // if the element is not already occupied
            if (!(recent_occupied.indexOf(inps[j]) > -1)) {
              if (inps[j].getAttribute("type")) {
                // XXX hardcoded value for string input 
                //  as text is used in HTML
                if (sub_type === "string") {in_type = "text"; }
                if (inps[j].getAttribute("type") === sub_type ||
                    inps[j].getAttribute("type") === in_type ) {
                  inps[j].setAttribute("name", sub_title);
                  inps[j].setAttribute("title", sub_title);
                  // if the input type is text then undefined --> "" 
                  if (inps[j].getAttribute("type") === "text" &&
                      default_value === undefined) {
                    default_value = "";
                  }
                  inps[j].setAttribute(
                    "value",
                    previous_value === undefined
                    ? default_value
                    : previous_value
                  );
                  recent_occupied.push(inps[j]);
				  // find the label for that input
                  inps[j].parentNode.parentNode
                    .previousSibling.previousSibling.innerHTML = sub_title_name;
                  inps[j].parentNode.parentNode
                    .previousSibling.previousSibling
                    .setAttribute("for", sub_title);
                  recent_occupied_labels.push(inps[j].parentNode.parentNode
                    .previousSibling.previousSibling);
                  // present them
                  inps[j].parentNode.parentNode
                      .previousSibling.previousSibling.style.display = '';
                  inps[j].parentNode.parentNode.style.display = '';
                  break;
                }
              }
            }
          }
        }
      }
      // hiding the inps that are not occupied
      for (j = 0; j <= inps.length-1; j += 1) {
        if (!(recent_occupied.indexOf(inps[j]) > -1)) {
          inps[j].parentNode.parentNode.style.display = 'block';
          inps[j].parentNode.parentNode.style.display = 'none';
        }
      }
      // hiding the labels that are not occupied
      for (j = 0; j <= labels.length-1; j += 1) {
        if (!(recent_occupied_labels.indexOf(labels[j]) > -1)) {
          labels[j].style.display = 'block';
          labels[j].style.display = 'none';
        }
      }
    } else {
      // hide the sub_field as there is nothing to show
      gadget.props.element.children[2].style.display = 'block';
      gadget.props.element.children[2].style.display = 'none';
    }
  }

  function _handleSelectChange() { //evt) {
    console.log("UPDATING FIELDS DUE TO SELECTION CHANGE");
    var gadget = this, oneOf_list, i,
      prop_name = gadget.props.definition.property_def.title,
      select = gadget.props.element.getElementsByTagName('select')[0],
      update_name = select.options[select.selectedIndex].value;
    if (!(update_name === prop_name)) {
      prop_name = update_name;
	  // change gadget.props.definition 
      for (i = 0;
           i <= gadget.props.options.property_definition.allOf.length - 1;
           i += 1) {
        if (gadget.props.options.property_definition.allOf[i].oneOf) {
          oneOf_list 
            = gadget.props.options.property_definition.allOf[i].oneOf;
          break;
        }
      }
      for (i = 0;
           i <= oneOf_list.length - 1;
           i += 1) {
        if (oneOf_list[i].title
            === prop_name) {
          gadget.props.definition = {
            name : prop_name,
            property_def : oneOf_list[i],
            value : oneOf_list[i].default
          };
          break;
        }
      }
    }
    syncField(gadget);
  }
  
  function handleSelectChange() {
    try {
      return  _handleSelectChange.bind(this)();
    } catch (e) {
      console.log("ERROR in handleSelectChange", e);
      console.log(e.stack);
    }
  }
  
  function waitForListFieldSelection(gadget) {
    var element = gadget.props.element.getElementsByTagName('select')[0];
    console.log("INITIATING A LOOP EVENT LISTENER FOR OPTION CHANGE");
    return loopEventListener(
      element,
      'change',
      false,
      handleSelectChange.bind(gadget)
    );
  }

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
      console.log("provided options");
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
            console.log("expa insertingAdjacentHTML for:" + property_id);
            gadget.props.element.insertAdjacentHTML(
              'beforeend',
              label_template({
                "for": property_id,
                "name": (property_definition.name || property_id)
              })
            );
            if (property_definition.allOf) {
              // if there is type property then remove it
              if (property_definition.allOf[0].type) {
                delete property_definition.allOf[0].type;
              }
              return gadget.declareGadget("../expandable_field/index.html");
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
      // update the listfield of the expandable field
      function updateListField(options) {
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
          prop_type_list, x, search_item, search_item_def,
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
              search_item = prop_dict[prop_list[x]].allOf ?
                "allOf" : prop_dict[prop_list[x]].type;
              search_item_def = prop_dict[prop_list[x]] || "";
              prop_type_list.push([search_item, search_item_def]);
              if (req_props_slist.indexOf(search_item) === -1) {
                // list of unique requested properties
                req_props_slist.push(search_item);
              }
            }
            // array of requested type-arrays for each different item
            req_props_dlist.push(prop_type_list);
          }
        }
        console.log("array of requested type-arrays for each item");
        console.log(req_props_dlist);
        /////////////////////////////////////////////////////////////
        // find the maximum number of appearances 
        // for each requested type within req_props_dlist
        /////////////////////////////////////////////////////////////
        for (x = 0; x <= req_props_slist.length-1; x += 1){
          req_props_sdict[req_props_slist[x]] = {
            "number" : [],
            "definition" : {}};
          for (ind = 0; ind <= req_props_dlist.length-1; ind += 1) {
            counter = 0;
            for (y = 0; y <= req_props_dlist[ind].length-1; y += 1) {
              if (req_props_slist[x] === req_props_dlist[ind][y][0]) {
                counter += 1;
                search_item_def = req_props_dlist[ind][y][1];
              }
            }
            req_props_sdict[req_props_slist[x]].number.push(counter);
            req_props_sdict[req_props_slist[x]].definition
              = search_item_def;
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
          req_props_sdict[Object.keys(req_props_sdict)[ind]].number =
            req_props_sdict[Object.keys(req_props_sdict)[ind]].number.reduce(
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
            console.log(index + "th option of allOf");
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
                     w <= req_props_sdict[
                            Object.keys(req_props_sdict)[ind]
                          ].number-1;
                     w += 1) {
                  ab_title = Object.keys(req_props_sdict)[ind] + "_" + w;
                  if (req_props_sdict[
                        Object.keys(req_props_sdict)[ind]
                      ].definition.allOf) {
                    ab_definition.properties[ab_title]
                      = req_props_sdict[
                        Object.keys(req_props_sdict)[ind]
                      ].definition;
                  } else {
                    ab_definition.properties[ab_title] = {
                      type: Object.keys(req_props_sdict)[ind],
                      default: "",
                      description: "",
                      required: true
                    };
                  }
                }
              }
              for (ind = 0; ind <= oneOf_list.length - 1; ind += 1) {
                if (oneOf_list[ind].title === string_value) {
                  value
                  = (gadget.props.options.value || {})[oneOf_list[ind].title]
                    === undefined
                    ? oneOf_list[ind].default
                    : gadget.props.options.value[oneOf_list[ind].title];
                  break;
                }
              }
              console.log("abstract_definition for " + index);
              console.log(ab_definition);
              // add a field with abstract definition
              addField(
                ab_definition.title,
                ab_definition,
                value
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
                  break;
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
              updateListField({
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
          console.log("[*](/)[*]");
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
          /* results[Object.keys(results)[0]] ====== is the result returned
		     keys[index] ====== different keys of the result returned
             results[Object.keys(results)[0]][keys[index]] ====== 
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
                             ][keys[index]][sub_keys[j]];
                    }
                  }
                } else {
                  // if the definition has no props then the object is empty
                  results[Object.keys(results)[0]][keys[index]] = {};
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
            console.log("hiding all the children as the service starts:");
            gadget.props.element.children[ind].style.display = "block";
            gadget.props.element.children[ind].style.display = "none";
          }
        })
        .push(function () {
          console.log("STARTSERVICE EXPANDFIELD 1");
          syncField(gadget);
        })
        .push(function () {
          var i,
          promise_list = [];
          for (i = 0; i < gadget.props.field_gadget_list.length; i += 1) {
            if (gadget.props.field_gadget_list[i].startService) {
              promise_list.push(
                gadget.props.field_gadget_list[i].startService()
              );
            }
          }
          console.log("thr r " + promise_list.length + " subgadget promises");
          return RSVP.all(promise_list);
        }).push(function() {
           // XXX return is required so that we see errors, but it blocks everything
           /* return */ waitForListFieldSelection(gadget);
        });
    });
}(window, rJS, RSVP, Handlebars, initGadgetMixin, loopEventListener));
