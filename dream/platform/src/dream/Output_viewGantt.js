/*global rJS, RSVP, jQuery, gantt,
         initGadgetMixin, console */
/*jslint nomen: true, unparam: true */
(function (window, rJS, RSVP, $, gantt,
           initGadgetMixin) {
  "use strict";

  /*
   GANTT widget

    Gantt expect data in the following format:

      time_unit: one of minute, hour, day, week, month or year. This will set gantt.config.scale_unit ( http://docs.dhtmlx.com/gantt/desktop__configuring_time_scale.html#settingthestepofthescale )
      
      subscales: sets gantt.config.subscales ( http://docs.dhtmlx.com/gantt/desktop__configuring_time_scale.html#addingthesecondscales )
      
      task_list: [
          {
            id: "project_1", # an unique id, different than "0" which is a reserved id
            text: "First Project", # the text to display
            start_date: '2015-03-02 08:54',
            # The date in '%d-%m-%Y %H:%M' format, optionnal for projects
            #  XXX it would be better to use ISO8601 / http://www.w3.org/TR/NOTE-datetime

            duration: 100, # the duration in time unit, optionnal for projects
            type: 'project',
            open: true
          },
          {
            id: "project_1_task_1",
            text: "A Task",
            start_date: start_date,
            stop_date: stop_date,
            duration: 100,
            parent: "project_1",    # id of the parent
            open: false
          }
        ]

  XXX both stop & start date are required for compatibility with dxhtmlscheduler

  TODOs:
   - make a really reusable gadget
   - handle links (prerequisites)

  */

  var gadget_klass = rJS(window);
  initGadgetMixin(gadget_klass);
  gadget_klass
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("aq_getAttachment", "jio_getAttachment")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function (options) {
      var jio_key = options.id,
        gadget = this;
      gadget.props.jio_key = jio_key;
      gadget.props.result = options.result;

      return gadget.aq_getAttachment({
          "_id": gadget.props.jio_key,
          "_attachment": "body.json"
        })
        .push(function (simulation_json) {
          var json_data = JSON.parse(simulation_json);
          gadget.props.result = json_data.result.result_list[options.result][
            options.action_definition.configuration.output_id];
        });
    })
    .declareMethod("startService", function () {
      
      var gantt_tasks = {
        data: this.props.result.task_list,
        links: []
      };

      gantt.config.duration_unit = this.props.result.time_unit;
      
      if (this.props.result.subscales) {
        gantt.config.subscales = this.props.result.subscales;
      }
      
      gantt.init($(this.props.element).find('.gant_container')[0]);
      gantt.parse(gantt_tasks);

      return new RSVP.Queue()
        .push(function () {
          // Infinite wait, until cancelled
          return (new RSVP.defer()).promise;
        })
        .push(undefined, function (error) {
          gantt.clearAll();
          throw error;
        });
    });
}(window, rJS, RSVP, jQuery, gantt, initGadgetMixin));
