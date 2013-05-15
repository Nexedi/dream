(function($, _) {
  "use strict";
  jsPlumb.bind("ready", function() {
    var graph_data = {}, dream_instance, available_people = {}, people_list,
        i, i_length, updateWorkerCount;
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

    dream_instance = DREAM.newDream(graph_data);
    dream_instance.start();

    //Fill list of people
    people_list = ["Worker1", "Worker2", "Worker3", "Worker4", "Worker5", "Worker6", "Worker7", "Worker8"];
    i_length = people_list.length;
    for (i = 0; i < i_length; i++) {
      $("#not_available ul").append('<li class="ui-state-default">' + people_list[i] + "</li>");
    }

    updateWorkerCount = function () {
      var available_worker_length = 0,
          available_worker_values =  _.values(available_people);
      _.each(available_worker_values, function(value) {
        if (value === true) {
          available_worker_length += 1;
        }
      });
      $("#total_workers h2").text(available_worker_length.toString());
    }

    // Make list of people draggable, update list of people depending
    // to make them available or not
    $("#available li").draggable({appendTo: "body"});
    $("#not_available li").draggable({appendTo: "body"});
    $("#available").droppable({
      drop: function(event, ui) {
        available_people[ui.draggable.text()] = true;
        dream_instance.setSimulationParameters(available_people);
        updateWorkerCount();
      }
    });
    $("#not_available").droppable({
      drop: function(event, ui) {
        available_people[ui.draggable.text()] = false;
        dream_instance.setSimulationParameters(available_people);
        updateWorkerCount();
      }
    });
  })

})(jQuery, _);
