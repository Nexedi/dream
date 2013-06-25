(function($, _) {
  "use strict";
  jsPlumb.bind("ready", function() {
    var dream_instance, available_people = {}, people_list,
        i, i_length, updateWorkerCount, json_plumb_configuration = {}, jio;
    jio = new jIO.newJio({type: "local", username: "dream", applicationname: "dream"});
    var window_id = 1;
    var element_id;
    var id_container = {};
    $( ".tool" ).draggable({ opacity: 0.7, helper: "clone",
                             stop: function(tool) {
                                     var box_top, box_left;
                                     box_top = tool.clientY;
                                     box_left = tool.clientX;
                                     id_container[tool.target.id] = (id_container[tool.target.id] || 0) + 1
                                     dream_instance.newElement({id : tool.target.id.split(".")[1] + "_" + id_container[tool.target.id],
                                                               coordinate: {y: box_top, x: box_left},
                                       class: tool.target.id,
                                     });
                                     window_id += 1;
                                  },
    }
    );
    var configuration = {
      "Dream.Source": { anchor: {RightMiddle: {}}},
      "Dream.Machine": { anchor: {RightMiddle: {}, LeftMiddle: {}, TopCenter: {}, BottomCenter: {}}},
      "Dream.Queue": { anchor: {RightMiddle: {}, LeftMiddle: {}}},
      "Dream.Exit": { anchor: {LeftMiddle: {}}},
      "Dream.Repairman": { anchor: {TopCenter: {}, BottomCenter: {}}},
    }
    dream_instance = DREAM.newDream(configuration)
    dream_instance.start();
    // Check if there is already data when we first load the page, if yes, then build graph from it
    jio.get({_id: "dream_demo"}, function(err, response) {
      console.log("jio get:", response);
      if (response !== undefined && response.data !== undefined) {
        _.each(response.data.element, function(value, key, list) {
          console.log("value", value);
          var element_id = value.id;
          var selection_data = response.data.selection[element_id] || {};
          _.each(_.pairs(selection_data), function(selection_value, selection_key, selection_list) {
            value[selection_value[0]] = selection_value[1];
          });
          console.log("going to add newElement", value);
          dream_instance.newElement(value);
        });
      }
      // once the data is read, we can subscribe to every changes
      $.subscribe("Dream.Gui.onDataChange", function(event, data) {
        console.log("onDataChange, data", data);
        $("#json_output")[0].value = JSON.stringify(data);
        jio.put({_id: "dream_demo", data: data}, function(err, response) {
          console.log("jio put:", response);}
        );
      });
    });

  })

})(jQuery, _);
