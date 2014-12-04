/*global console, jQuery, rJS, RSVP, alert, Handlebars, initGadgetMixin */
/*jslint nomen: true */
(function (window, $, rJS, RSVP, Handlebars, initGadgetMixin) {
  "use strict";

  /////////////////////////////////////////////////////////////////
  // Desactivate jQuery Mobile URL management
  /////////////////////////////////////////////////////////////////
  $.mobile.ajaxEnabled = false;
  $.mobile.linkBindingEnabled = false;
  $.mobile.hashListeningEnabled = false;
  $.mobile.pushStateEnabled = false;

  /////////////////////////////////////////////////////////////////
  // Minimalistic ERP5's like portal type configuration
  /////////////////////////////////////////////////////////////////
  // XXX we should use lists instead to keep ordering
  var portal_types = {
    "Pre Input Module": {
      view: {
        gadget: "InputModule_viewAddInstanceDefinitionDialog",
        type: "object_fast_input",
        title: "Choose Instance Definition"
      }
    }//,
    /*"Input Module": {
      "view": {
        "gadget": "InputModule_viewInputList",
        "type": "object_list",
        "title": "Document List"
      },
      "view_fast_input": {
        "gadget": "InputModule_viewAddDocumentDialog",
        "type": "object_fast_input",
        "title": "Create Document"
      }
    }*/
    // TODO: remove this once everything is merged.
    /*"Input": {
      "view": {
        "gadget": "Input_viewProductionLine",
        "type": "object_view",
        "title": "Production Line"
      },
      "view_wip_part_spreadsheet": {
        "gadget": "Input_viewWipPartSpreadsheet",
        "type": "object_view",
        "title": "WIP Part Spreadsheet",
        "condition": function (gadget) {
          console.log("-------------------+----------------------");
          console.log(gadget);
          console.log(gadget.props);
          console.log(gadget.props.configuration_dict);
          console.log("-------------------+----------------------");
          return (gadget.props.configuration_dict['Dream-Configuration']
                        .gui.wip_part_spreadsheet);
        }
      },
      "view_shift_spreadsheet": {
        "gadget": "Input_viewShiftSpreadsheet",
        "type": "object_view",
        "title": "Shift Spreadsheet",
        "condition": function (gadget) {
          return (gadget.props.configuration_dict['Dream-Configuration']
                        .gui.shift_spreadsheet);
        }
      },
      "view_available_capacity_spreadsheet": {
        "gadget": "Input_viewAvailableCapacitySpreadsheet",
        "type": "object_view",
        "title": "Available Capacity Spreadsheet",
        "condition": function (gadget) {
          return (gadget.props.configuration_dict['Dream-Configuration']
                        .gui.capacity_by_project_spreadsheet);
        }
      },
      "view_required_capacity_spreadsheet": {
        "gadget": "Input_viewRequiredCapacitySpreadsheet",
        "type": "object_view",
        "title": "Required Capacity Spreadsheet",
        "condition": function (gadget) {
          return (gadget.props.configuration_dict['Dream-Configuration']
                        .gui.capacity_by_station_spreadsheet);
        }
      },
      "view_dp_capacity_spreadsheet": {
        "gadget": "Input_viewDemandPlanningCapacitySpreadsheet",
        "type": "object_view",
        "title": "Demand Planning Required Capacity Spreadsheet",
        "condition": function (gadget) {
          return (gadget.props.configuration_dict['Dream-Configuration']
                        .gui.dp_capacity_spreadsheet);
        }
      },
      "view_dp_route_spreadsheet": {
        "gadget": "Input_viewDemandPlanningRouteSpreadsheet",
        "type": "object_view",
        "title": "Demand Planning Route Spreadsheet",
        "condition": function (gadget) {
          return (gadget.props.configuration_dict['Dream-Configuration']
                        .gui.dp_route_spreadsheet);
        }
      },
      "view_simu": {
        "gadget": "Input_viewSimulation",
        "type": "object_view",
        "title": "Run simulation"
      },
      "view_management": {
        "gadget": "Input_viewDocumentManagement",
        "type": "object_view",
        "title": "Manage document"
      },
      "view_result": {
        "gadget": "Input_viewResultList",
        "type": "object_view",
        "title": "Results"
      }
    },
    "Output": {
      "view": {
        "gadget": "Output_viewStationUtilisationGraph",
        "type": "object_view",
        "title": "Stations Utilization",
        "condition": function (gadget) {
          return (gadget.props.configuration_dict['Dream-Configuration']
                        .gui.station_utilisation_graph);
        }
      },
      "download_excel_spreadsheet": {
        "gadget": "Output_viewDownloadExcelSpreadsheet",
        "type": "object_view",
        "title": "Download Excel Spreadsheet",
        "condition": function (gadget) {
          return (gadget.props.configuration_dict['Dream-Configuration']
                        .gui.download_excel_spreadsheet);
        }
      },
      "view_capacity_utilization": {
        "gadget": "Output_viewCapacityUtilisationGraph",
        "type": "object_view",
        "title": "Capacity Utilization",
        "condition": function (gadget) {
          return (gadget.props.configuration_dict['Dream-Configuration']
                        .gui.capacity_utilisation_graph);
        }
      },
      "view_queue_stat": {
        "gadget": "Output_viewQueueStatGraph",
        "type": "object_view",
        "title": "Queues Statistics",
        "condition": function (gadget) {
          return (gadget.props.configuration_dict['Dream-Configuration']
                        .gui.queue_stat);
        }
      },
      "view_exit_stat": {
        "gadget": "Output_viewExitStatistics",
        "type": "object_view",
        "title": "Exit Statistics",
        "condition": function (gadget) {
          return (gadget.props.configuration_dict['Dream-Configuration']
                        .gui.exit_stat);
        }
      },
      "view_gantt": {
        "gadget": "Output_viewJobGantt",
        "type": "object_view",
        "title": "Job Gantt",
        "condition": function (gadget) {
          return (gadget.props.configuration_dict['Dream-Configuration']
                        .gui.job_gantt);
        }
      },
      "view_schedule": {
        "gadget": "Output_viewJobScheduleSpreadsheet",
        "type": "object_view",
        "title": "Job Schedule",
        "condition": function (gadget) {
          return (gadget.props.configuration_dict['Dream-Configuration']
                        .gui.job_schedule_spreadsheet);
        }
      },
      "view_debug": {
        "gadget": "Output_viewDebugJson",
        "type": "object_view",
        "title": "Debug JSON",
        "condition": function (gadget) {
          return (gadget.props.configuration_dict['Dream-Configuration']
                        .gui.debug_json);
        }
      }
    }*/
  },
    panel_template,
    navigation_template,
    active_navigation_template,
    error_template,
    gadget_klass = rJS(window);


  function calculateTabHTML(gadget, options, key, title, active) {
    /*console.log('________________________');
    console.log(key);
    console.log(gadget);
    console.log(options);
    console.log(title);
    console.log(active);
    console.log('________________________');*/
    return new RSVP.Queue()
      .push(function () {
        var kw = {
          action: key,
          id: options.id
        };
        if (options.result !== undefined) {
          kw.result = options.result;
        }
        return gadget.aq_pleasePublishMyState(kw);
      })
      .push(function (url) {
        /*console.log('<><><><><><><>><><><><><><><calculating tab url:');
        console.log(key);
        if (url === undefined) {
          console.log('tab url:');
          console.log(url);
        } else {
          console.log('undefined url');
        }*/
        var kw = {
          title: title,
          link: url
        };
        if (active === true) {
          return active_navigation_template(kw);
        }

        return navigation_template(kw);

      });
  }

  function getNextLink(gadget, portal_type, options) {
    var forward_kw = {action: options.action || "view"},
      queue = new RSVP.Queue();
    if (portal_type === "Input") {
      forward_kw.id = options.id;
    } else if (portal_type === "Output") {
      forward_kw.id = options.id;
      queue
        .push(function () {
          return gadget.getDeclaredGadget("jio");
        })
        .push(function (jio_gadget) {
          return jio_gadget.getAttachment({
            _id: options.id,
            "_attachment": "simulation.json"
          });
        })
        .push(function (sim_json) {
          var document_list = JSON.parse(sim_json),
            current = parseInt(options.result, 10);
          if (current === (document_list.length - 1)) {
            forward_kw.result = 0;
          } else {
            forward_kw.result = current + 1;
          }
        });
    } else if (portal_type !== "Pre Input Module") {
      throw new Error("Unknown portal type: " + portal_type);
    }
    return queue.push(function () {
      return gadget.aq_pleasePublishMyState(forward_kw);
    });
  }

  function getTitle(gadget, portal_type, options) {
    var title;
    if (portal_type === "Pre Input Module") {
      title = "Documents";
    } else if (portal_type === "Input") {
      title = gadget.getDeclaredGadget("jio")
        .push(function (jio_gadget) {
          return jio_gadget.get({_id: options.id});
        })
        .push(function (jio_doc) {
          return jio_doc.data.title + " (" + jio_doc.data.modified + ")";
        });
    } else if (portal_type === "Output") {
      title = gadget.getDeclaredGadget("jio")
        .push(function (jio_gadget) {
          return jio_gadget.getAttachment({
            _id: options.id,
            "_attachment": "simulation.json"
          });
        })
        .push(function (sim_json) {
          var document_list = JSON.parse(sim_json);
          return document_list[options.result].score + " " +
            document_list[options.result].key;
        });
    } else {
      throw new Error("Unknown portal type: " + portal_type);
    }
    return title;
  }

  function calculateNavigationHTML(gadget, portal_type, options) {
    /*console.log('.............................');
    console.log(gadget);
    console.log(portal_type);
    console.log(options);
    console.log(options.action);
    console.log(portal_types[portal_type]);
    console.log(portal_types[portal_type][options.action]);
    console.log(portal_types[portal_type][options.action].type);
    console.log('<<<<<<<<<<<<<<<<<<<<<<<<<<<<');*/
    var nav_html,
      action;
    if (portal_types[portal_type][options.action].type ===
        "object_view") {
      return new RSVP.Queue()
        .push(function () {
          var url_list = [],
            key2;
          for (key2 in portal_types[portal_type]) {
            if (portal_types[portal_type].hasOwnProperty(key2)) {
              action = portal_types[portal_type][key2];
              if (action.type === "object_view") {
                if ((action.condition === undefined) ||
                    (action.condition(gadget))) {
                  url_list.push(
                    calculateTabHTML(gadget, options, key2, action.title,
                                     (key2 === options.action))
                  );
                }
              }
            }
          }
          /*console.log('url_list');
          console.log(url_list);
          console.log('>>>>>>>>>>>>>>>>>>>>>>>>');*/
          return RSVP.all(url_list);
        })
        .push(function (entry_list) {
          /*console.log('entry_list');
          console.log(entry_list);*/
          var i;
          nav_html =
            '<nav data-role="navbar" data-collapsible="true"><ul>';
          for (i = 0; i < entry_list.length; i += 1) {
            nav_html += entry_list[i];
          }
          nav_html += '</ul></nav>';
          return nav_html;
        });
    }
  }

  initGadgetMixin(gadget_klass);
  /*console.log('AaAaAaAaAaAaAaAaAaAaAaAaAaAaAaAaAaAaAaAaAaAaAaAa');
  console.log(gadget_klass);
  console.log('AaAaAaAaAaAaAaAaAaAaAaAaAaAaAaAaAaAaAaAaAaAaAaAa');*/
  gadget_klass
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("pleaseRedirectMyHash", "pleaseRedirectMyHash")

    /////////////////////////////////////////////////////////////////
    // Handle acquisition
    /////////////////////////////////////////////////////////////////
    // Bridge to jio gadget
    .allowPublicAcquisition("jio_allDocs", function (param_list) {
      return this.getDeclaredGadget("jio")
        .push(function (jio_gadget) {
          return jio_gadget.allDocs.apply(jio_gadget, param_list);
        });
    })
    .allowPublicAcquisition("jio_ajax", function (param_list) {
      return this.getDeclaredGadget("jio")
        .push(function (jio_gadget) {
          return jio_gadget.ajax.apply(jio_gadget, param_list);
        });
    })
    .allowPublicAcquisition("jio_post", function (param_list) {
      return this.getDeclaredGadget("jio")
        .push(function (jio_gadget) {
          return jio_gadget.post.apply(jio_gadget, param_list);
        });
    })
    .allowPublicAcquisition("jio_remove", function (param_list) {
      return this.getDeclaredGadget("jio")
        .push(function (jio_gadget) {
          return jio_gadget.remove.apply(jio_gadget, param_list);
        });
    })
    .allowPublicAcquisition("jio_get", function (param_list) {
      return this.getDeclaredGadget("jio")
        .push(function (jio_gadget) {
          return jio_gadget.get.apply(jio_gadget, param_list);
        });
    })
    .allowPublicAcquisition("jio_putAttachment", function (param_list) {
      return this.getDeclaredGadget("jio")
        .push(function (jio_gadget) {
          return jio_gadget.putAttachment.apply(jio_gadget, param_list);
        });
    })
    .allowPublicAcquisition("jio_getAttachment", function (param_list) {
      return this.getDeclaredGadget("jio")
        .push(function (jio_gadget) {
          return jio_gadget.getAttachment.apply(jio_gadget, param_list);
        });
    })
    .allowPublicAcquisition("startListenTo", function (param_list) {
      //console.log('arkoudesarkoudesarkoudesarkoudesarkoudes');
      var obj, type, fn;
      obj = param_list[0];
      type = param_list[1];
      fn = param_list[2];
      if (obj.addEventListener) {
        obj.addEventListener(type, fn, false);
      } else if (obj.attachEvent) {
        obj["e" + type + fn] = fn;
        obj[type + fn] = function () {
          obj["e" + type + fn](window.event);
        };
        obj.attachEvent("on" + type, obj[type + fn]);
      }
    })
    .allowPublicAcquisition("whoWantsToDisplayHome", function () {
      // Hey, I want to display some URL
      return this.aq_pleasePublishMyState({});
    })
    .allowPublicAcquisition("whoWantsToDisplayThisDocument",
                            function (param_list) {
        // Hey, I want to display some jIO document
        // XXX should be merged with whoWantsToDisplayThisResult
        var kw = {
          action: param_list[1] || "view"
        };
        if (param_list[0] !== undefined) {
          kw.id = param_list[0];
        }
        /*console.log(1010101010101);
        console.log(kw);
        console.log(param_list);*/
        return this.aq_pleasePublishMyState(kw);
      })
    .allowPublicAcquisition("whoWantsToDisplayThisResult",
                            function (param_list) {
        // Hey, I want to display some jIO document

        // We'll display the result using the first enabled action
        var action = "view", action_info, action_id;
        for (action_id in portal_types.Output) {
          if (portal_types.Output.hasOwnProperty(action_id)) {
            action_info = portal_types.Output[action_id];
            if ((action_info.condition === undefined) ||
                (action_info.condition(this))) {
              action = action_id;
              break;
            }
          }
        }
        return this.aq_pleasePublishMyState({
          action: action,
          id: param_list[0],
          result: param_list[1]
        });
      })
    .allowPublicAcquisition("getConfigurationDict", function () {
      return this.props.configuration_dict;
    })
    .allowPublicAcquisition("configurationIsSet", function () {
      this.props.configSet = true;
    })
    .allowPublicAcquisition("setConfigurationDict", function (conf_dict) {
      this.props.configuration_dict = JSON.parse(conf_dict);
    })
    // Configure jIO to use localstorage
    // And load configuration from server
    .allowPublicAcquisition("getDefaultConfigurationDict", function () {
      var jio_gadget, g = this;
      //console.log('@@@@@@@@@@@@@@@getting DeclalredGadget@@@@@@@@@@@@@@@');
      //console.log(g);
      return g.getDeclaredGadget("jio")
        /*.push(function (gadget) {
          jio_gadget = gadget;
          console.log(jio_gadget);
          return jio_gadget.createJio({
            type: "local",
            username: "dream",
            applicationname: "dream"
          });
        })*/
        .push(function (gadget) {
          jio_gadget = gadget;
          // XXX Hardcoded relative URL
          return jio_gadget.ajax({url: "../../getConfigurationDict"});
        })
        .push(function (evt) {
          g.props.configuration_dict = JSON.parse(evt.target.responseText);
          return g.props.configuration_dict;
        });
    })

    /////////////////////////////////////////////////////////////////
    // ready
    /////////////////////////////////////////////////////////////////
    // Precompile the templates while loading the first gadget instance
    .ready(function () {
      if (panel_template === undefined) {
        // XXX Only works as root gadget
        panel_template = Handlebars.compile(
          document.getElementById("panel-template").innerHTML
        );
        //console.log(123123123123123);
        //console.log('panel_template');
        //console.log(document.getElementById("panel-template").innerHTML);
        navigation_template = Handlebars.compile(
          document.getElementById("navigation-template").innerHTML
        );
        /*console.log(123123123123);
        console.log('navigation_template');
        console.log(document.getElementById("navigation-template")
                    .innerHTML);*/
        active_navigation_template = Handlebars.compile(
          document.getElementById("active-navigation-template").innerHTML
        );
        /*console.log(123123123123);
        console.log('active_navigation_template');
        console.log(
          document.getElementById("active-navigation-template").innerHTML
        );*/
        error_template = Handlebars.compile(
          document.getElementById("error-template").innerHTML
        );
        /*console.log(123123123123);
        console.log('error_template');
        console.log(document.getElementById("error-template").innerHTML);*/
      }
    })

    // Create some link on the page
    .ready(function (g) {
      //console.log('ggggggggggggggggggggg');
      //console.log(g);
      return new RSVP.Queue()
        .push(function () {
          //console.log('**********************************1');
          //console.log(g);
          return RSVP.all([
            g.aq_pleasePublishMyState({}),
            //g.aq_pleasePublishMyState({action: "view_fast_input"}),
            g.aq_pleasePublishMyState({action: "view"})
          ]);
        })
        .push(function (link_list) {
          //console.log('____________________link_List*********************');
          //console.log(link_list);
          //console.log('_________________________*************************');
          var panel = g.props.element.querySelector("#leftpanel");

          panel.innerHTML =
            panel_template({navigationlist: []});
          panel.getElementsByClassName("pre_input_link")[0].href =
            link_list[0];
          //panel.getElementsByClassName("home_link")[0].href = link_list[0];
          //panel.getElementsByClassName("fast_input_link")[0].href =
          //  link_list[1];
          // XXX JQuery mobile
          $(panel).trigger("create");
        });
    })

    // Configure jIO to use localstorage
    // And load configuration from server
    .ready(function (g) {
      //console.log('@@@@@@@@@@@@@@@getting DeclalredGadget@@@@@@@@@@@@@@@');
      //console.log(g);
      return g.getDeclaredGadget("jio")
        .push(function (gadget) {
          return gadget.createJio({
            type: "local",
            username: "dream",
            applicationname: "dream"
          });
		});
        /*.push(function () {
          g.props.configuration_dict =  {
            "Dream-Configuration": {
              "_class": "Dream.Configuration", 
              "gui": {
                "debug_json": 1,
                "download_excel_spreadsheet": 0,
                "exit_stat": 1,
                "job_gantt": 0,
                "job_schedule_spreadsheet": 0,
                "queue_stat": 1,
                "shift_spreadsheet": 0,
                "station_utilisation_graph": 1,
                "wip_part_spreadsheet": 0,
                "wip_spreadsheet": 0
              },
              "property_list": [{
                "_class": "Dream.Property",
                "_default": 10,
                "id": "numberOfReplications",
                "name": "Number of replications",
                "type": "number"
              }]
            }
          };
        });*/
    })

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    // Render the page
    .declareMethod("render", function (options) {
      var gadget = this,
        back_kw = {action: "view"},
        page_gadget,
        portal_type = "Pre Input Module",
        nav_element = gadget.props.element
                            .getElementsByClassName("nav_container")[0],
        element = gadget.props.element
                        .getElementsByClassName("gadget_container")[0];
      console.log('!!!!!!!!!!!!!!!!!!!!!!options!!!!!!!!!!!!!!!!!!!!!!!');
      console.log(options);
      console.log('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!');
      if (options.action === undefined) {
        // Redirect to the view action
        options.action = "view";
        return gadget.aq_pleasePublishMyState(options)
          .push(gadget.pleaseRedirectMyHash.bind(gadget));
      }

      /*// if configuration_dict is defined 
      // then Pre Input Module should not be loaded
      if (gadget.props.configSet === true) {
        portal_type = "Input Module";
        $('.pre_input_link').hide();
      }*/
      if (gadget.props.configSet === true) {
        portal_types.Input =
          gadget.props.configuration_dict.application_configuration.Input;
        portal_types.Output =
          gadget.props.configuration_dict.application_configuration.Output;
      }
      // Detect what is the kind of document displayed
      if (options.id !== undefined) {
        if (options.result === undefined) {
          portal_type = "Input";
        } else {
          portal_type = "Output";
          back_kw.action = "view_result";
          back_kw.id = options.id;
        }
      }

      console.log('__________________portal_types__________________');
      console.log(portal_types);
      console.log(portal_type);
      console.log(options);
      console.log(portal_types[portal_type]);
      /*return gadget.getDeclaredGadget("jio")
        .push(function(jio_gadget) {
          if (options.id) {
            return jio_gadget.getAttachment({
              "_id": options.id,
              "_attachment": "body.json"
            });
          }
        })
        .push(function(result) {
          var data;
          if (result) {
            data = JSON.parse(result);
            gadget.props.data = data;
            portal_types.Input = data.application_configuration.input;
            portal_types.Output = data.application_configuration.output;
          }
          // Get the action information 
          return gadget.declareGadget(
            portal_types[portal_type][options.action].gadget + ".html"
          );
        })*/
      return gadget.declareGadget(
        portal_types[portal_type][options.action].gadget + ".html"
      )
        .push(function (g) {
          page_gadget = g;
          if (page_gadget.render !== undefined) {
            return page_gadget.render(options);
          }
        }).push(function () {
          return RSVP.all([
            page_gadget.getElement(),
            calculateNavigationHTML(gadget, portal_type, options),
            gadget.aq_pleasePublishMyState(back_kw),
            getTitle(gadget, portal_type, options),
            getNextLink(gadget, portal_type, options)
          ]);
        }).push(function (result_list) {
          console.log('????????????????????????????????????????????');
          console.log(result_list);
          console.log('????????????????????????????????????????????');
          var nav_html = result_list[1],
            page_element = result_list[0];

          // Update title
          gadget.props.element.querySelector("header h1").textContent =
            result_list[3];

          // XXX Hide the back button in case of module display?
          // Update back link
          gadget.props.element
            .getElementsByClassName("back_link")[0].href = result_list[2];
          // XXX Hide the forward button in case of non result?
          // Update forward link
          gadget.props.element
            .getElementsByClassName("next_link")[0].href = result_list[4];

          // Update the navigation panel
          // Clear the previous rendering
          while (nav_element.firstChild) {
            nav_element.removeChild(nav_element.firstChild);
          }
          if (nav_html !== undefined) {
            nav_element.innerHTML = nav_html;
            $(nav_element).trigger("create");
          }

          // Append in the DOM at the end to reduce flickering and reduce DOM
          // modifications
          // Clear the previous rendering
          while (element.firstChild) {
            element.removeChild(element.firstChild);
          }
          element.appendChild(page_element);
          $(element).trigger('create');

          // XXX RenderJS hack to start sub gadget services
          // Only work if this gadget has no parent.
          if (page_gadget.startService !== undefined) {
            return page_gadget.startService();
          }
        }).push(undefined, function (error) {
          if (error instanceof RSVP.CancellationError) {
            throw error;
          }
          console.error(error);
          document.querySelector("article[class='gadget_container']")
            .innerHTML = error_template({ error: error });
        });
    });
}(window, jQuery, rJS, RSVP, Handlebars, initGadgetMixin));
