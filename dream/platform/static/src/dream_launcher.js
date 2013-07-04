(function($, _) {
  "use strict";
  jsPlumb.bind("ready", function() {
    var dream_instance, available_people = {}, people_list,
        i, i_length, updateWorkerCount, json_plumb_configuration = {}, jio;
    jio = new jIO.newJio({type: "local", username: "dream", applicationname: "dream"});
    var window_id = 1;
    var element_id;
    var id_container = {}; // to allow generating next ids, like Machine_1, Machine_2, etc
    var property_container = {entity: {id: "entity", type:"string", _class: "Dream.Property", default: "Part"},
                              // XXX is it possible not to repeat id ?
                              mean: {id: "mean", type: "string", _class: "Dream.Property", default: "0.9"},
                              distributionType: {id: "distributionType", type: "string", _class: "Dream.Property", default: "Exp"},
                              stdev: {id: "stdev", type: "string", _class: "Dream.Property", default: "0.1"},
                              min: {id: "min", type: "string", _class: "Dream.Property", default: "0.1"},
                              max: {id: "max", type: "string", _class: "Dream.Property", default: "1"},
                              failureDistribution: {id: "failureDistribution", type: "string", _class: "Dream.Property", default:"Fixed"},
                              MTTF: {id: "MTTF", type: "string", _class: "Dream.Property", default: "40"},
                              MTTR: {id: "MTTR", type: "string", _class: "Dream.Property", default: "10"},
                              repairman: {id: "repairman", type: "string", _class: "Dream.Property"},
                              isDummy: {id: "isDummy", type: "string", _class: "Dream.Property", default: "0"},
                              capacity: {id: "capacity", type: "string", _class: "Dream.Property", default: "1"},
                              numberOfReplications: {id: "numberOfReplications", type: "string", _class: "Dream.Property", default: "10"},
                              maxSimTime: {id: "maxSimTime", type: "string", _class: "Dream.Property", default: "100"},
                              confidenceLevel: {id: "confidenceLevel", type: "string", _class: "Dream.Property", default: "0.5"},
    };
    property_container["interarrivalTime"] =  {id:"interarrivalTime",
                                               property_list: [property_container["mean"], property_container["distributionType"]],
                                               _class: "Dream.PropertyList"};
    property_container["processingTime"] = {id:"processingTime",
                                            property_list: [property_container["mean"], property_container["distributionType"],
                                                            property_container["stdev"], property_container["min"],
                                                            property_container["max"],,
                                            ],
                                            _class: "Dream.PropertyList"};
    property_container["failures"] = {id:"failures",
                                      property_list: [property_container["failureDistribution"], property_container["MTTF"],
                                                      property_container["MTTR"], property_container["repairman"],
                                      ],
                                      _class: "Dream.PropertyList"};

    var configuration = {
      "Dream-Source": { anchor: {RightMiddle: {}}, /* TODO: make anchor not a configuration option and allow to connect from everywhere */
                        property_list: [property_container["interarrivalTime"], property_container["entity"]],
                        _class: 'Dream.Source',
      },
      "Dream-Machine": { anchor: {RightMiddle: {}, LeftMiddle: {}, TopCenter: {}, BottomCenter: {}},
                         property_list: [property_container["processingTime"], property_container["failures"]],
                         _class: 'Dream.Machine',
      },
      "Dream-Queue": { anchor: {RightMiddle: {}, LeftMiddle: {}},
                       property_list: [property_container["capacity"], property_container["isDummy"]],
                       _class: 'Dream.Queue',
      },
      "Dream-Exit": { anchor: {LeftMiddle: {},}, _class: 'Dream.Exit' },
      "Dream-Repairman": { anchor: {TopCenter: {}, BottomCenter: {}},
                           property_list: [property_container["capacity"]],
                           _class: 'Dream.Repairman',
      },
      "Dream-Configuration": { property_list: [ property_container["numberOfReplications"],
                                                property_container["maxSimTime"],
                                                property_container["confidenceLevel"], ],
                               _class: 'Dream.Repairman', },
    }

    dream_instance = DREAM.newDream(configuration)
    dream_instance.start();
    $( ".tool" ).draggable({ opacity: 0.7, helper: "clone",
                             stop: function(tool) {
                                     var box_top, box_left, _class;
                                     box_top = tool.clientY;
                                     box_left = tool.clientX;
                                     id_container[tool.target.id] = (id_container[tool.target.id] || 0) + 1;
                                     _class = tool.target.id.replace('-', '.'); // XXX - vs .
                                     dream_instance.newElement({id : tool.target.id + "_" + id_container[tool.target.id],
                                                               coordinate: {y: box_top, x: box_left},
                                       _class: _class,
                                     });
                                     window_id += 1;
                                  },
    });

    // Check if there is already data when we first load the page, if yes, then build graph from it
    jio.get({_id: "dream_demo"}, function(err, response) {
      console.log("jio get:", response);
      if (response !== undefined && response.data !== undefined) {
        // Add all elements
        _.each(response.data.element, function(value, key, list) {
          var element_id = value.id;
          var preference_data = response.data.preference !== undefined ? response.data.preference[element_id] :  {};
          _.each(_.pairs(preference_data), function(preference_value, preference_key, preference_list) {
            value[preference_value[0]] = preference_value[1];
          });
          dream_instance.newElement(value);
          dream_instance.updateElementData(element_id, {data: value.data || {}});
        });
        // Now link elements between them and update id_container
        _.each(response.data.element, function(value, key, list) {
          var element_id = value.id, prefix, suffix, splitted_element_id,
              successor_list = value.successorList || [];
          splitted_element_id = element_id.split("_");
          prefix = splitted_element_id[0];
          suffix = splitted_element_id[1];
          id_container[prefix] = Math.max((id_container[prefix] || 0), parseInt(suffix, 10));
          if (successor_list.length > 0) {
            _.each(successor_list, function(successor_value, successor_key, list) {
              dream_instance.connect(value.id, successor_value);
            });
          }
        });
        dream_instance.setGeneralProperties(response.data.general);
        dream_instance.initGeneralProperties(); // XXX
        $("#json_output").text(JSON.stringify(dream_instance.getData(), undefined, " "));
      }

      // once the data is read, we can subscribe to every changes
      $.subscribe("Dream.Gui.onDataChange", function(event, data) {
        console.log("onDataChange, data", data);
        $("#json_output").text(JSON.stringify(data, undefined, " "));
        jio.put({_id: "dream_demo", data: data}, function(err, response) {
          console.log("jio put:", response);}
        );
      });
    });

    $("#run_simulation").button().click(
      function(e){
       dream_instance.runSimulation(
          function(data) {
            if (data['success']) {
              $("#json_result").text(JSON.stringify(data['success'], undefined, " "));
              $.each(data.coreObject, function(idx, obj){
                 var e = $("#" + obj.id);
                 /* attach something to each corresponding core object */
                 // e.tooltip(JSON.stringify(obj['results'], undefined, " "));
              })
            } else {
              $("#json_result").effect('shake', 50).text(data['traceback']);
            }
       });
       e.preventDefault();
       return false;
     });
    $("#clear_all").button().click(
      function(e){
       dream_instance.clearAll(
          function() {
            dream_instance.clearAll();
       });
       e.preventDefault();
       return false;
     });
  })

})(jQuery, _);
