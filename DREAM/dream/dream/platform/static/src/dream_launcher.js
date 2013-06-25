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

  })

})(jQuery, _);
