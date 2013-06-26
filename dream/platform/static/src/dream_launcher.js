(function($, _) {
  "use strict";
  jsPlumb.bind("ready", function() {
    var dream_instance, available_people = {}, people_list,
        i, i_length, updateWorkerCount, json_plumb_configuration = {}, jio;
    jio = new jIO.newJio({type: "local", username: "dream", applicationname: "dream"});
    var window_id = 1;
    var element_id;
    var id_container = {}; // to allow generating next ids, like Machine_1, Machine_2, etc
    var property_container = {interarrivalTime: {id:"interarrivalTime",
                                                 property_list: [{id: "mean", type: "string", _class: "Dream.Property"},
                                                                  {id: "distributionType", type: "string", _class: "Dream.Property"}],
                                                 _class: "Dream.PropertyList"},
                              entity: {id: "entity",
                                       type:"string",
                                       _class: "Dream.Property"},};
    var configuration = {
      "Dream-Source": { anchor: {RightMiddle: {}},
                        property_list: [property_container["interarrivalTime"], property_container["entity"]],
      },
      "Dream-Machine": { anchor: {RightMiddle: {}, LeftMiddle: {}, TopCenter: {}, BottomCenter: {}}},
      "Dream-Queue": { anchor: {RightMiddle: {}, LeftMiddle: {}}},
      "Dream-Exit": { anchor: {LeftMiddle: {}}},
      "Dream-Repairman": { anchor: {TopCenter: {}, BottomCenter: {}}},
    }
    dream_instance = DREAM.newDream(configuration)
    dream_instance.start();
    $( ".tool" ).draggable({ opacity: 0.7, helper: "clone",
                             stop: function(tool) {
                                     var box_top, box_left;
                                     box_top = tool.clientY;
                                     box_left = tool.clientX;
                                     id_container[tool.target.id] = (id_container[tool.target.id] || 0) + 1
                                     dream_instance.newElement({id : tool.target.id + "_" + id_container[tool.target.id],
                                                               coordinate: {y: box_top, x: box_left},
                                       class: tool.target.id,
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
          console.log("value", value);
          var element_id = value.id;
          var preference_data = response.data.preference[element_id] || {};
          _.each(_.pairs(preference_data), function(preference_value, preference_key, preference_list) {
            value[preference_value[0]] = preference_value[1];
          });
          console.log("going to add newElement", value);
          dream_instance.newElement(value);
        });
        // Now link elements between them and update id_container
        _.each(response.data.element, function(value, key, list) {
          var element_id = value.id, prefix, suffix, splitted_element_id,
              successor_list = value.successorList || [];
          splitted_element_id = element_id.split("_");
          prefix = splitted_element_id[0];
          suffix = splitted_element_id[1];
          console.log("suffix", suffix);
          id_container[prefix] = Math.max((id_container[prefix] || 0), parseInt(suffix, 10));
          console.log("id_container", id_container);
          if (successor_list.length > 0) {
            _.each(successor_list, function(successor_value, successor_key, list) {
              dream_instance.connect(value.id, successor_value);
            });
          }
        });
      }
      // once the data is read, we can subscribe to every changes
      $.subscribe("Dream.Gui.onDataChange", function(event, data) {
        console.log("onDataChange, data", data);
        $("#json_output")[0].value = JSON.stringify(data, undefined, " ");
        jio.put({_id: "dream_demo", data: data}, function(err, response) {
          console.log("jio put:", response);}
        );
      });
    });

  })

})(jQuery, _);
