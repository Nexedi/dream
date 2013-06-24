(function($, _) {
  "use strict";
  jsPlumb.bind("ready", function() {
    var graph_data = {}, dream_instance, available_people = {}, people_list,
        i, i_length, updateWorkerCount, json_plumb_configuration = {};
    graph_data.throughput = 0;
    graph_data.box_list = [
        {id: 'window1', title: 'attach1', throughput: 30, target_list: ['window2'], coordinate: {top: 5, left: 5}},
        {id: 'window2', title: 'attach2', throughput: 21, target_list: ['window3'], coordinate: {top: 5, left: 15}},
        {id: 'window3', title: 'attach3', throughput: 29, target_list: ['window7'], coordinate: {top: 5, left: 25}},
        {id: 'window4', title: 'attach1', throughput: 22, target_list: ['window5'], coordinate: {top: 20, left: 5}},
        {id: 'window5', title: 'attach2', throughput: 27, target_list: ['window6'], coordinate: {top: 20, left: 15}},
        {id: 'window6', title: 'attach3', throughput: 26, target_list: ['window7'], coordinate: {top: 20, left: 25}},
        {id: 'window7', title: 'Moulding', throughput: 40, target_list: ['window8', 'window10'], coordinate: {top: 12, left: 35}},
        {id: 'window8', title: 'tests', throughput: 23, target_list: ['window9'], coordinate: {top: 5, left: 45}},
        {id: 'window9', title: 'packaging', throughput: 25, coordinate: {top: 5, left: 55}},
        {id: 'window10', title: 'tests', throughput: 28, target_list: ['window11'], coordinate: {top: 20, left: 45}},
        {id: 'window11', title: 'packaging', throughput: 27, coordinate: {top: 20, left: 55}},
    ];
    /*json_plumb_configuration["Dream.Queue"] = {
        "id": "DummyQ",
        "name": "DummyQ",
        "isDummy": "1",
        "capacity": "1",
        "predecessorList": ["S1"],
        "successorList": ["M1"]
        };*/
    //dream_instance = DREAM.newDream(graph_data);
    //dream_instance.start();
    var main_div_offset = $("#main").offset();
    var window_id = 1;
    var element_id;
    var id_container = {};
    $( ".tool" ).draggable({ opacity: 0.7, helper: "clone",
                             stop: function(tool) {
                                     var box_top, box_left;
                                     box_top = (tool.clientY - main_div_offset.top);
                                     box_left = (tool.clientX - main_div_offset.left);
                                     id_container[tool.target.id] = (id_container[tool.target.id] || 0) + 1
                                     dream_instance.newElement({id : tool.target.id.split(".")[1] + "_" + id_container[tool.target.id],
                                                               coordinate: {top: box_top, left: box_left},
                                       class: tool.target.id,
                                     });
                                     window_id += 1;
                                  },
    }
    );
    dream_instance = jsonPlumb.newJsonPlumb();
    dream_instance.start();

  })

})(jQuery, _);
